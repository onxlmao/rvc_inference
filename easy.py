import json
import os
import shutil
import urllib.request
import zipfile
from argparse import ArgumentParser

import gradio as gr
from src.main import song_cover_pipeline

# Base directories
BASE_DIR = os.getcwd()
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')
output_dir = os.path.join(BASE_DIR, 'song_output')


# ---------------- Utility Functions ----------------

def get_current_models(models_dir):
    models_list = os.listdir(models_dir)
    items_to_remove = ['hubert_base.pt', 'MODELS.txt', 'public_models.json', 'rmvpe.pt']
    return [item for item in models_list if item not in items_to_remove]


def update_models_list():
    models_l = get_current_models(rvc_models_dir)
    return gr.update(choices=models_l)


def extract_zip(extraction_folder, zip_name):
    os.makedirs(extraction_folder, exist_ok=True)
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(extraction_folder)
    os.remove(zip_name)

    index_filepath, model_filepath = None, None
    for root, dirs, files in os.walk(extraction_folder):
        for name in files:
            if name.endswith('.index') and os.stat(os.path.join(root, name)).st_size > 1024 * 100:
                index_filepath = os.path.join(root, name)
            if name.endswith('.pth') and os.stat(os.path.join(root, name)).st_size > 1024 * 1024 * 40:
                model_filepath = os.path.join(root, name)

    if not model_filepath:
        raise gr.Error(f'No .pth model file was found in the extracted zip. Please check {extraction_folder}.')

    os.rename(model_filepath, os.path.join(extraction_folder, os.path.basename(model_filepath)))
    if index_filepath:
        os.rename(index_filepath, os.path.join(extraction_folder, os.path.basename(index_filepath)))

    # Remove any unnecessary nested folders
    for filepath in os.listdir(extraction_folder):
        full_path = os.path.join(extraction_folder, filepath)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)


def download_online_model(url, dir_name, progress=gr.Progress()):
    try:
        progress(0, desc=f'[~] Downloading voice model with name {dir_name}...')
        zip_name = url.split('/')[-1]
        extraction_folder = os.path.join(rvc_models_dir, dir_name)
        if os.path.exists(extraction_folder):
            raise gr.Error(f'Voice model directory {dir_name} already exists! Choose a different name for your voice model.')

        if 'pixeldrain.com' in url:
            url = f'https://pixeldrain.com/api/file/{zip_name}'

        urllib.request.urlretrieve(url, zip_name)
        progress(0.5, desc='[~] Extracting zip...')
        extract_zip(extraction_folder, zip_name)
        return f'[+] {dir_name} Model successfully downloaded!'
    except Exception as e:
        raise gr.Error(str(e))


def upload_local_model(zip_path, dir_name, progress=gr.Progress()):
    try:
        extraction_folder = os.path.join(rvc_models_dir, dir_name)
        if os.path.exists(extraction_folder):
            raise gr.Error(f'Voice model directory {dir_name} already exists! Choose a different name for your voice model.')

        zip_name = zip_path.name
        progress(0.5, desc='[~] Extracting zip...')
        extract_zip(extraction_folder, zip_name)
        return f'[+] {dir_name} Model successfully uploaded!'
    except Exception as e:
        raise gr.Error(str(e))


def pub_dl_autofill(pub_models, event: gr.SelectData):
    return gr.update(value=pub_models.loc[event.index[0], 'URL']), gr.Text.update(value=pub_models.loc[event.index[0], 'Model Name'])


def swap_visibility():
    # Swap visibility between file upload and YouTube link inputs
    return gr.update(visible=True), gr.update(visible=False), gr.update(value=''), gr.update(value=None)


def process_file_upload(file):
    return file.name, gr.update(value=file.name)


def show_hop_slider(pitch_detection_algo):
    if pitch_detection_algo == 'mangio-crepe':
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)


# ---------------- UI Building Functions ----------------

def build_main_tab():
    voice_models = get_current_models(rvc_models_dir)
    with gr.Tab("Main"):
        with gr.Accordion('Main Options', open=True):
            with gr.Row():
                rvc_model = gr.Dropdown(voice_models, label='Voice Models')
                ref_btn = gr.Button('Refresh Models 🔁', variant='primary')
                with gr.Column() as yt_link_col:
                    song_input = gr.Text(label='Song input')
                    show_file_upload_button = gr.Button('Upload file instead')
                with gr.Column(visible=False) as file_upload_col:
                    local_file = gr.File(label='Audio file')
                    song_input_file = gr.UploadButton('Upload 📂', file_types=['audio'], variant='primary')
                    show_yt_link_button = gr.Button('Paste YouTube link/Path to local file instead')
                    song_input_file.upload(process_file_upload, inputs=[song_input_file],
                                           outputs=[local_file, song_input])
                with gr.Column():
                    pitch = gr.Slider(-3, 3, value=0, step=1, label='Pitch Change (Vocals ONLY)')
            show_file_upload_button.click(swap_visibility,
                                          outputs=[file_upload_col, yt_link_col, song_input, local_file])
            show_yt_link_button.click(swap_visibility,
                                      outputs=[yt_link_col, file_upload_col, song_input, local_file])
        with gr.Accordion('Voice Conversion Options', open=False):
            with gr.Row():
                index_rate = gr.Slider(0, 1, value=0.5, label='Index Rate')
                filter_radius = gr.Slider(0, 7, value=3, step=1, label='Filter Radius')
            with gr.Row():
                rms_mix_rate = gr.Slider(0, 1, value=0.25, label='RMS Mix Rate')
                protect = gr.Slider(0, 0.5, value=0.33, label='Protect Rate')
                with gr.Column():
                    f0_method = gr.Dropdown(['rmvpe', 'mangio-crepe'], value='rmvpe', label='Pitch Detection Algorithm')
                    crepe_hop_length = gr.Slider(32, 320, value=128, step=1, visible=False, label='Crepe Hop Length')
                    f0_method.change(show_hop_slider, inputs=f0_method, outputs=crepe_hop_length)
            keep_files = gr.Checkbox(label='Keep Intermediate Files')
        with gr.Accordion('Audio Mixing Options', open=False):
            gr.Markdown('### Volume Change (decibels)')
            with gr.Row():
                main_gain = gr.Slider(-20, 20, value=0, step=1, label='Main Vocals')
                backup_gain = gr.Slider(-20, 20, value=0, step=1, label='Backup Vocals')
                inst_gain = gr.Slider(-20, 20, value=0, step=1, label='Music')
            gr.Markdown('### Audio Output Format')
            output_format = gr.Dropdown(['mp3', 'wav'], value='mp3', label='Output File Type')
        with gr.Row():
            clear_btn = gr.ClearButton(value='Clear', components=[song_input, rvc_model, keep_files, local_file])
            generate_btn = gr.Button("Generate", variant='primary')
            ai_cover = gr.Audio(label='AI Cover', show_share_button=False)
        ref_btn.click(update_models_list, None, outputs=rvc_model)
        is_webui = gr.Number(value=1, visible=False)
        generate_btn.click(
            song_cover_pipeline,
            inputs=[song_input, rvc_model, pitch, keep_files, is_webui, main_gain, backup_gain,
                    inst_gain, index_rate, filter_radius, rms_mix_rate, f0_method, crepe_hop_length,
                    protect, output_format],
            outputs=[ai_cover]
        )
        clear_btn.click(
            lambda: [0, 0, 0, 0, 0.5, 3, 0.25, 0.33, 'rmvpe', 128, 'mp3', None],
            outputs=[pitch, main_gain, backup_gain, inst_gain, index_rate, filter_radius, rms_mix_rate,
                     protect, f0_method, crepe_hop_length, output_format, ai_cover]
        )



def build_download_tab():
    with gr.Tab('Download Model'):
        with gr.Tab('From URL'):
            with gr.Row():
                model_zip_link = gr.Text(
                    label='Download Link to Model',
                    info='Should be a zip file containing a .pth model file and an optional .index file.'
                )
                model_name = gr.Text(
                    label='Name Your Model',
                    info='Give your new model a unique name from your other voice models.'
                )
            with gr.Row():
                download_btn = gr.Button('Download 🌐', variant='primary', scale=19)
                dl_output_message = gr.Text(label='Output Message', interactive=False, scale=20)
            download_btn.click(download_online_model, inputs=[model_zip_link, model_name], outputs=dl_output_message)
            gr.Markdown('## Input Examples')
            gr.Examples(
                [
                    ['https://huggingface.co/phant0m4r/LiSA/resolve/main/LiSA.zip', 'Lisa'],
                    ['https://pixeldrain.com/u/3tJmABXA', 'Gura'],
                    ['https://huggingface.co/Kit-Lemonfoot/kitlemonfoot_rvc_models/resolve/main/AZKi%20(Hybrid).zip', 'Azki']
                ],
                [model_zip_link, model_name],
                [],
                download_online_model,
            )
        with gr.Tab('From Public Index'):
            gr.Markdown('## How to Use')
            gr.Markdown('- Click Initialize public models table')
            gr.Markdown('- Filter models using tags or search bar')
            gr.Markdown('- Select a row to autofill the download link and model name')
            gr.Markdown('- Click Download')
            with gr.Row():
                pub_zip_link = gr.Text(label='Download Link to Model')
                pub_model_name = gr.Text(label='Model Name')
            with gr.Row():
                download_pub_btn = gr.Button('Download 🌐', variant='primary', scale=19)
                pub_dl_output_message = gr.Text(label='Output Message', interactive=False, scale=20)
            download_pub_btn.click(download_online_model, inputs=[pub_zip_link, pub_model_name], outputs=pub_dl_output_message)


def build_upload_tab():
    with gr.Tab('Upload Model'):
        gr.Markdown('## Upload Locally Trained RVC v2 Model and Index File')
        gr.Markdown('- Find model file (weights folder) and optional index file (logs/[name] folder)')
        gr.Markdown('- Compress files into a zip file')
        gr.Markdown('- Upload zip file and give a unique name for the voice')
        gr.Markdown('- Click Upload Model')
        with gr.Row():
            with gr.Column():
                zip_file = gr.File(label='Zip File')
            local_model_name = gr.Text(label='Model Name')
        with gr.Row():
            model_upload_button = gr.Button('Upload Model', variant='primary', scale=19)
            local_upload_output_message = gr.Text(label='Output Message', interactive=False, scale=20)
            model_upload_button.click(upload_local_model, inputs=[zip_file, local_model_name],
                                      outputs=local_upload_output_message)


# ---------------- Main Function ----------------









def main():
    parser = ArgumentParser(description='RVC Inference GUI.')
    parser.add_argument("--share", action="store_true", dest="share_enabled", default=False, help="Enable sharing")
    parser.add_argument("--listen", action="store_true", default=False, help="Make the WebUI reachable from your local network.")
    parser.add_argument('--listen-host', type=str, help='The hostname that the server will use.')
    parser.add_argument('--listen-port', type=int, help='The listening port that the server will use.')
    args = parser.parse_args()

    

    with gr.Blocks(title='RVC Inference GUI') as app:
        with gr.Column(elem_classes="gradio-container"):
            gr.Markdown("<h1 style='text-align:center;'>RVC Inference EasyGUI</h1>")
            build_main_tab()
            build_download_tab()
            build_upload_tab()

    app.launch(
        share=args.share_enabled,
        server_name=None if not args.listen else (args.listen_host or '0.0.0.0'),
        server_port=args.listen_port,
    )


if __name__ == '__main__':
    main()
