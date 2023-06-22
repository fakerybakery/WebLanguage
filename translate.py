# todo import config from YAML
print('1: Importing Modules')
import torch
import os
import bs4
from bs4 import BeautifulSoup
import re
import yaml
from tqdm import tqdm
import shutil
import dl_translate as dlt
import nltk
print('2: Setting up Model')
if torch.backends.mps.is_available():
    device = 'mps'
elif torch.cuda.is_available():
    device = 'cuda'
else:
    device = 'auto'
mt = dlt.TranslationModel(device=device)
print('3: Downloading NLTK model')
nltk.download("punkt")
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
        if element.string:
            if element.string not in excluded_words:
                translated_text = translate_text(element.string, src_lang, tgt_lang)
                element.string.replace_with(translated_text)
        translate_attributes(element, src_lang, tgt_lang)
    with open(file_path, "w") as file:
        formatter = bs4.formatter.HTMLFormatter(indent='\t')
        file.write(soup.prettify(formatter=formatter))
def translate(text, src_lang, tgt_lang):
    sents = nltk.tokenize.sent_tokenize(text, "english")
    translated_text = " ".join(mt.translate(sents, source=src_lang, target=tgt_lang))
    print(translated_text)
    return translated_text
folder_path = "examples"
src_lang = "en"
tgt_lang = "fr"
excluded_words = ["WebLanguage"]
output_folder = "output"
if not os.path.isdir(folder_path):
    print('Error: input path does not exist')
    exit(0)
if os.path.isdir(output_folder):
    print('Error: output path already exists')
    exit(0)
else:
    os.mkdir(output_folder)
files_to_translate = [file_name for file_name in os.listdir(folder_path) if file_name.endswith(".html")]
print('4: Translating')
with tqdm(total=len(files_to_translate), desc="Translating HTML files") as pbar:
    for file_name in files_to_translate:
        shutil.copy(os.path.join(folder_path, file_name), os.path.join(output_folder, file_name))
        file_path = os.path.join(output_folder, file_name)
        translate_html_file(file_path, src_lang, tgt_lang)
        pbar.update(1)
