# todo import config from YAML
# todo translate javascript
print('1: Importing Modules. This may take a moment.')
import warnings
warnings.filterwarnings("ignore")
import torch
import os
import bs4
from bs4 import BeautifulSoup
import yaml
from tqdm import tqdm
import shutil
import dl_translate as dlt
import nltk
print('2: Setting up Model. This may take a couple minutes when you start the program for the first time, but on slower networks it may take as long as an hour.')
if torch.backends.mps.is_available():
    device = 'mps'
    print('Using Metal accelerator backend.')
elif torch.cuda.is_available():
    device = 'cuda'
    print('Using CUDA accelerator backend.')
else:
    device = 'auto'
    print('Didn\'t detect either CUDA or Metal accelerator backend.')
    print('Setting backend to "auto." This will be slower.')
mt = dlt.TranslationModel(device=device)
print('3: Downloading NLTK model. This may take a minute when you start the program for the first time, but on slower networks it may take a couple minutes.')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def translate_text(text, src_lang, tgt_lang):
    translated_text = translate(text, src_lang, tgt_lang)
    return translated_text

def translate_attributes(element, src_lang, tgt_lang):
    attrs_to_translate = ["value", "placeholder", "title"]
    for attr in attrs_to_translate:
        if attr in element.attrs:
            if element[attr] not in excluded_words:
                translated_attr = translate_text(element[attr], src_lang, tgt_lang)
                element[attr] = translated_attr

def translate_html_file(file_path, src_lang, tgt_lang):
    with open(file_path, "r") as file:
        content = file.read()
    soup = BeautifulSoup(content, "html.parser")
    elements = soup.find_all()
    for element in elements:
        if element.name in excluded_tags:
            continue
        if element.string:
            if element.string not in excluded_words:
                translated_text = translate_text(element.string, src_lang, tgt_lang)
                element.string.replace_with(translated_text)
        translate_attributes(element, src_lang, tgt_lang)
    with open(file_path, "w") as file:
        file.write(soup.prettify())

def translate(text, src_lang, tgt_lang):
    sents = nltk.tokenize.sent_tokenize(text, "english")
    translated_text = " ".join(mt.translate(sents, source=src_lang, target=tgt_lang))
    return translated_text

folder_path = "examples"
src_lang = "en"
tgt_lang = "fr"
excluded_words = ["WebLanguage"]
excluded_tags = ["script", "style"]
output_folder = "output"

if not os.path.isdir(folder_path):
    print('Error: input path does not exist')
    exit(0)

if os.path.isdir(output_folder):
    override = input('Output path already exists. Override? (y/N) ')
    if not ((override.strip().lower() == 'y') or (override.strip().lower() == 'yes')):
        exit(0)
    else:
        print('Overriding.')
else:
    os.mkdir(output_folder)

files_to_translate = [file_name for file_name in os.listdir(folder_path) if file_name.endswith(".html")]
print('4: Translating. This may take a while.')
with tqdm(total=len(files_to_translate), desc="Translating HTML files") as pbar:
    for file_name in files_to_translate:
        shutil.copy(os.path.join(folder_path, file_name), os.path.join(output_folder, file_name))
        file_path = os.path.join(output_folder, file_name)
        translate_html_file(file_path, src_lang, tgt_lang)
        pbar.update(1)
