import os
from pathlib import Path
import gdown
from tqdm import tqdm

MDX_DOWNLOAD_LINK = 'https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/'
RVC_DOWNLOAD_LINK = 'https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/'

BASE_DIR = os.getcwd()

# Ensure the directories exist
mdxnet_models_dir = Path(BASE_DIR) / 'mdxnet_models'
rvc_models_dir = Path(BASE_DIR) / 'rvc_models'
mdxnet_models_dir.mkdir(parents=True, exist_ok=True)
rvc_models_dir.mkdir(parents=True, exist_ok=True)

def dl_model(link, model_name, dir_name):
    url = f'{link}{model_name}'
    output_path = str(Path(dir_name) / model_name)
    # gdown.download shows a progress bar when quiet=False
    gdown.download(url, output_path, quiet=False)

if __name__ == '__main__':
    mdx_model_names = [
        'UVR-MDX-NET-Voc_FT.onnx',
        'UVR_MDXNET_KARA_2.onnx',
        'Reverb_HQ_By_FoxJoy.onnx'
    ]
    # Wrap the MDX model downloads in a tqdm progress bar
    for model in tqdm(mdx_model_names, desc='Downloading MDX models'):
        dl_model(MDX_DOWNLOAD_LINK, model, mdxnet_models_dir)

    rvc_model_names = [
        'hubert_base.pt',
        'rmvpe.pt'
    ]
    # Wrap the RVC model downloads in a tqdm progress bar
    for model in tqdm(rvc_model_names, desc='Downloading RVC models'):
        dl_model(RVC_DOWNLOAD_LINK, model, rvc_models_dir)

    print('All models downloaded!')
