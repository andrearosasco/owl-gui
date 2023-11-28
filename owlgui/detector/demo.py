import sys
import time

import cv2

sys.path.append('/home/owlvit/big_vision/')

from sort import Sort
from owlgui.utils.base_config import BaseConfig
from owlgui.utils.concurrency.generic_node import GenericNode
from owlgui.utils.concurrency.py_queue import PyQueue


import jax.numpy as jnp
import jax
import numpy as np
import fixed_queries as models_fq
# from scenic.projects.owl_vit.configs import owl_v2_clip_b16 as config_module
from scenic.projects.owl_vit.configs import clip_b32 as config_module
from scipy.special import expit as sigmoid
import skimage
import tensorflow as tf

tf.config.experimental.set_visible_devices([], 'GPU')


class Configs(BaseConfig):
    class Comms:
        in_queues = {'from_embedder': PyQueue(ip="localhost", port=50000, queue_name='embedder_out', size=0, blocking=False),
                     'from_source': PyQueue(ip="localhost", port=50000, queue_name='source_to_det', size=1, blocking=True),
                     'from_visualizer': PyQueue(ip="localhost", port=50000, queue_name='viz_to_det', size=1, blocking=False)}
        out_queues = {'to_embedder': PyQueue(ip="localhost", port=50000, queue_name='embedder_in', size=0, write_format={'class_name': None}, blocking=True),
                      'to_visualizer': PyQueue(ip="localhost", port=50000, queue_name='det_to_viz', size=1, write_format={k: None for k in ['boxes', 'labels', 'scores', 'thresholds', 'class_names']}, blocking=False)}


class Detector(GenericNode):
    
    def __init__(self):
        super().__init__(**Configs.Comms.to_dict())
        
        ### Initialize SORT tracker ###
        self.tracking = False
        max_age, min_hits, iou_threshold = 1, 3, 0.3
        self.mot_tracker = Sort(max_age=max_age, 
                min_hits=min_hits,
                iou_threshold=iou_threshold)
        
        ### Initialize Detector ###
        config = config_module.get_config(init_mode='canonical_checkpoint')

        # Modified module that uses precomputed textual embedding
        self.module_fq = models_fq.TextZeroShotDetectionModule(
            body_configs=config.model.body,
            normalize=config.model.normalize,
            box_bias=config.model.box_bias)
        
        # The apply function is compiled to run faster
        self.jitted = jax.jit(self.module_fq.apply, static_argnames=('train',))

        # Load weights
        checkpoint_path = 'checkpoints/' + config.init_from.checkpoint_path.split('/')[-1]
        self.variables = self.module_fq.load_variables(checkpoint_path)
        
        # Prepare initial text queries
        self.class_names = []
        self.class_embeddings = np.zeros([1, 0, 512])

        # self.write('to_embedder', {'class_name': 'human_face'})
        self.thresholds = []
        self.config = config
        
    def loop(self, data):
        
        rgb = data['rgb']
        
        if 'class_name' in data and 'class_embedding' in data:
            self.class_names.append(data['class_name'])
            self.class_embeddings = np.concatenate([self.class_embeddings, data['class_embedding']], axis=1)
        
        if 'add' in data:
            class_name = data['add']['class_name']
            threshold = data['add']['threshold']
            print(class_name)
            if class_name not in self.class_names:
                self.write('to_embedder', {'class_name': class_name})
                self.thresholds += [threshold]
            
        if 'remove' in data:
            class_name = data['remove']['class_name']
            print(class_name)
            if class_name in self.class_names:
                idx = self.class_names.index(class_name)
                self.thresholds.pop(idx)
                self.class_names.pop(idx)
                self.class_embeddings = np.delete(self.class_embeddings, idx, axis=1)
            
                
        if 'threshold' in data:
            class_idx = data['threshold']['class']
            value = data['threshold']['value']
            print(class_idx, value)
            self.thresholds[class_idx] = value
                
        if len(self.class_names) == 0:
            return {}

        image = rgb.astype(np.float32) / 255.0
        h, w, _ = image.shape
        size = max(h, w)
        image_padded = np.pad(
            image, ((0, size - h), (0, size - w), (0, 0)), constant_values=0.5)

        # Resize to model input size:
        input_image = skimage.transform.resize(
            image_padded,
            (self.config.dataset_configs.input_size, self.config.dataset_configs.input_size),  # input_size, input_size
            anti_aliasing=True)


        # Note: The model expects a batch dimension.
        start = time.perf_counter()
        predictions = self.jitted(
            self.variables,
            input_image[None, ...],
            self.class_embeddings,
            train=False)
        print(f'{1 / (time.perf_counter() - start)}')

        # Remove batch dimension and convert to numpy:
        predictions = jax.tree_util.tree_map(lambda x: np.array(x[0]), predictions)

        logits = predictions['pred_logits']
        boxes = predictions['pred_boxes']
        
        logits = logits[..., :len(self.class_names)]  # Remove padding.
        scores = sigmoid(np.max(logits, axis=-1))
        labels = np.argmax(logits, axis=-1)

        # plots for each class the most probable logits
        # plot_heatmap(logits[np.argmax(logits, axis=0)].T, text_queries)
        # plot all the logits
        # plot_heatmap(logits.T, text_queries)
        # trackers = mot_tracker.update(dets) # x1, y1, x2, y2

        if self.tracking:
            output = (input_image * 255).astype(np.uint8)
            dets = np.zeros([0, 6])
            for i, box in enumerate(boxes):
                if scores[i] >= self.thresholds[labels[i]]:
                    cx, cy, w, h = (box * self.config.dataset_configs.input_size).astype(int)
                    x1, y1, x2, y2 = int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2)
                    aux = np.array([x1, y1, x2, y2, scores[i], labels[i]])
                    dets = np.concatenate([dets, aux[None]], axis=0)

            boxes, labels, scores = self.mot_tracker.update(dets) # x1, y1, x2, y2
            
            for box, label in zip(boxes, labels):
                x1, x2, y1, y2, id = box.astype(int)
                output = cv2.rectangle(img=output, pt1=(x1, x2),
                                    pt2=(y1, y2), color=(255, 0, 0), thickness=5)

                output = cv2.putText(output, f'{self.class_names[int(label)]}', (x1, int(y2 + 0.2)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)


        else:
            output = (input_image * 255).astype(np.uint8)
            for score, box, label in zip(scores, boxes, labels):
                if score < self.thresholds[label]:
                    continue
                cx, cy, w, h = (box * self.config.dataset_configs.input_size).astype(int)
                x1, x2, y1, y2 = int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2)
                output = cv2.rectangle(img=output, pt1=(x1, x2),
                                                    pt2=(y1, y2), color=(255, 0, 0), thickness=5)

                output = cv2.putText(output, f'{self.class_names[label]}: {score:1.2f}', (int(cx - w / 2), int(cy + h / 2 + 0.2)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # cv2.imshow('test', output[..., ::-1])
        # cv2.waitKey(1)
        
        return {'boxes': boxes, 'labels': labels, 'scores': scores,
                'thresholds': self.thresholds, 'class_names': self.class_names}
        

if __name__ == '__main__':
    detector = Detector()
    detector.run()