import sys
import numpy as np
import torch
from tqdm import tqdm
from owlgui.utils.base_config import BaseConfig

from owlgui.utils.concurrency.generic_node import GenericNode
from owlgui.utils.concurrency.py_queue import PyQueue
sys.path.append('/home/owlvit/big_vision/')
# from scenic.projects.owl_vit.configs import owl_v2_clip_b16 as config_module
from scenic.projects.owl_vit.configs import clip_b32 as config_module
from scenic.projects.owl_vit import models

class Configs(BaseConfig):
    class Comms:
        in_queues = {'embedder_in': PyQueue(ip="localhost", port=50000, queue_name='embedder_in', size=10, blocking=True)}
        out_queues = {'embedder_out': PyQueue(ip="localhost", port=50000, queue_name='embedder_out', size=10, 
                                              write_format={'class_name': None, 'class_embedding': None},blocking=True)}


class TextEmbedder(GenericNode):
    def __init__(self) -> None:
        super().__init__(**Configs.Comms.to_dict())
        
        config = config_module.get_config(init_mode='canonical_checkpoint')
        self.module = models.TextZeroShotDetectionModule(
            body_configs=config.model.body,
            normalize=config.model.normalize,
            box_bias=config.model.box_bias)
        
        checkpoint_path = 'checkpoints/' + config.init_from.checkpoint_path.split('/')[-1]
        self.variables = self.module.load_variables(checkpoint_path)
        self.config = config
        
    
    def loop(self, data): 
        class_name = data['class_name']
        print(data)
             
        embeddings = self.compute_embeddings([class_name], self.module, self.variables)
        
        data['class_embedding'] = embeddings
        return data
        
        
    def is_running(self):
        return self.process is not None and self.process.is_alive()
    
    def get_result(self):
        self.ret.get()
        self.process.join()
        
        self.process = None


# def compute_embeddings_mp(classnames, module, variables, ret):
#     embeddings = compute_embeddings(classnames, module, variables)
#     ret.put(embeddings)

    def compute_embeddings(self, classnames, module, variables):
        with torch.no_grad():
            zeroshot_weights = []
            for classname in tqdm(classnames):
                texts = [template.format(classname) for template in templates] #format with class
                texts += [classname]
                texts = np.array([module.tokenize(q, 16) for q in texts], dtype=np.int32)
                class_embeddings = module.apply(variables, np.zeros([1, self.config.dataset_configs.input_size, self.config.dataset_configs.input_size, 3])
                                                , texts[None, ...], train=False)['query_embeddings'][0]
                class_embeddings /= np.linalg.norm(class_embeddings, axis=-1, keepdims=True)
                class_embedding = class_embeddings.mean(axis=0)
                class_embedding /= np.linalg.norm(class_embeddings)
                zeroshot_weights.append(class_embedding)
            zeroshot_weights = np.array(zeroshot_weights)
        return zeroshot_weights[None]


templates = [
    'a bad photo of a {}.',
    'a photo of many {}.',
    # 'a sculpture of a {}.',
    'a photo of the hard to see {}.',
    'a low resolution photo of the {}.',
    'a rendering of a {}.',
    # 'graffiti of a {}.',
    'a bad photo of the {}.',
    'a cropped photo of the {}.',
    # 'a tattoo of a {}.',
    # 'the embroidered {}.',
    'a photo of a hard to see {}.',
    'a bright photo of a {}.',
    'a photo of a clean {}.',
    'a photo of a dirty {}.',
    'a dark photo of the {}.',
    # 'a drawing of a {}.',
    'a photo of my {}.',
    # 'the plastic {}.',
    'a photo of the cool {}.',
    'a close-up photo of a {}.',
    'a black and white photo of the {}.',
    # 'a painting of the {}.',
    # 'a painting of a {}.',
    'a pixelated photo of the {}.',
    # 'a sculpture of the {}.',
    'a bright photo of the {}.',
    'a cropped photo of a {}.',
    # 'a plastic {}.',
    'a photo of the dirty {}.',
    'a jpeg corrupted photo of a {}.',
    'a blurry photo of the {}.',
    'a photo of the {}.',
    'a good photo of the {}.',
    'a rendering of the {}.',
    # 'a {} in a video game.',
    'a photo of one {}.',
    # 'a doodle of a {}.',
    'a close-up photo of the {}.',
    'a photo of a {}.',
    # 'the origami {}.',
    # 'the {} in a video game.',
    'a sketch of a {}.',
    # 'a doodle of the {}.',
    # 'a origami {}.',
    'a low resolution photo of a {}.',
    # 'the toy {}.',
    # 'a rendition of the {}.',
    'a photo of the clean {}.',
    'a photo of a large {}.',
    # 'a rendition of a {}.',
    'a photo of a nice {}.',
    'a photo of a weird {}.',
    'a blurry photo of a {}.',
    # 'a cartoon {}.',
    # 'art of a {}.',
    # 'a sketch of the {}.',
    # 'a embroidered {}.',
    'a pixelated photo of a {}.',
    'itap of the {}.',
    'a jpeg corrupted photo of the {}.',
    'a good photo of a {}.',
    # 'a plushie {}.',
    'a photo of the nice {}.',
    'a photo of the small {}.',
    'a photo of the weird {}.',
    # 'the cartoon {}.',
    # 'art of the {}.',
    # 'a drawing of the {}.',
    'a photo of the large {}.',
    'a black and white photo of a {}.',
    # 'the plushie {}.',
    'a dark photo of a {}.',
    'itap of a {}.',
    # 'graffiti of the {}.',
    # 'a toy {}.',
    'itap of my {}.',
    'a photo of a cool {}.',
    'a photo of a small {}.',
    # 'a tattoo of the {}.',
]

if __name__ == "__main__":
    print('ciao')
    TextEmbedder().run()