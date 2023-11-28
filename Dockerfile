FROM ubuntu:20.04
  

ARG USER=owlvit
ARG PASSWORD=owlvit

ARG CONDA_SCRIPT=Miniforge3-23.3.1-1-Linux-x86_64.sh
ARG CONDA_LINK=https://github.com/conda-forge/miniforge/releases/download/23.3.1-1/${CONDA_SCRIPT}
ARG CONDA_MD5=aef279d6baea7f67940f16aad17ebe5f6aac97487c7c03466ff01f4819e5a651

ARG pip=/home/${USER}/miniforge3/envs/${USER}/bin/pip
ARG PYTHONDONTWRITEBYTECODE=true

RUN apt update \
    && ln -fs /usr/share/zoneinfo/Europe/Rome /etc/localtime \
    && apt install --no-install-recommends -y -qq sudo git build-essential unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup ${USER} \
    && useradd -ms /bin/bash ${USER} -g ${USER} \
    && echo "${USER}:${PASSWORD}" | chpasswd \
    && usermod -a -G sudo ${USER} \
    && sed -i.bak -e 's/%sudo\s\+ALL=(ALL\(:ALL\)\?)\s\+ALL/%sudo ALL=NOPASSWD:ALL/g' /etc/sudoers

USER ${USER}
WORKDIR /home/${USER}

RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends wget bzip2 \
    && wget ${CONDA_LINK} \
    && bash ./${CONDA_SCRIPT} -b \
    && /home/${USER}/miniforge3/bin/mamba init bash \
    && sudo find /home/${USER}/miniforge3 -follow -type f -name '*.a' -delete \
    && sudo find /home/${USER}/miniforge3 -follow -type f -name '*.pyc' -delete \
    && /home/${USER}/miniforge3/bin/mamba clean -afy \
    && rm ${CONDA_SCRIPT} \
    && echo "mamba activate owlvit" >> /home/${USER}/.bashrc

COPY ./env.yml ./env.yml
RUN /home/${USER}/miniforge3/condabin/mamba env create --file env.yml && rm env.yml

RUN sudo apt update && sudo apt install ffmpeg libsm6 libxext6  -y

RUN git clone https://github.com/google-research/scenic.git \
    && cd scenic && git checkout de635e17b107 \
    && $pip install -e . && $pip install -r scenic/projects/owl_vit/requirements.txt

RUN git clone https://github.com/google-research/big_vision.git \
    && cd big_vision && git checkout 53f18caf27a \
    && $pip install -r big_vision/requirements.txt

RUN $pip install --upgrade "jax[cuda11_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

RUN sudo mv /etc/sudoers.bak /etc/sudoers
CMD ["bash"]
