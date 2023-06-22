import torch
import os
import bs4
from bs4 import BeautifulSoup
from tqdm import tqdm
import shutil
import dl_translate as dlt
import nltk
class WebLanguage:
    _setup = False
    _verbose = False
    def __init__(self, verbose=False, excluded_tags=['']):
        self._verbose = verbose
    def setup(self):
        if torch.backends.mps.is_available():
            device = 'mps'
            if self._verbose:
                print('[WL]: Using Metal accelerator backend.')
        elif torch.cuda.is_available():
            device = 'cuda'
            if self._verbose:
                print('Using CUDA accelerator backend.')
        else:
            device = 'auto'
            if self._verbose:
                print('Didn\'t detect either CUDA or Metal accelerator backend.')
                print('Setting backend to "auto." This will be slower.')
        self.mt = dlt.TranslationModel(device=device)
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        self._setup = True
    
    def __translate_text(text, src_lang, tgt_lang):
        translated_text = translate(text, src_lang, tgt_lang)
        return translated_text

    def __translate_attributes(element, src_lang, tgt_lang):
        attrs_to_translate = ["value", "placeholder", "title"]
        for attr in attrs_to_translate:
            if attr in element.attrs:
                if element[attr] not in excluded_words:
                    translated_attr = translate_text(element[attr], src_lang, tgt_lang)
                    element[attr] = translated_attr

    def __translate_html_file(file_path, src_lang, tgt_lang):
        with open(file_path, "r") as file:
            content = file.read()
        soup = BeautifulSoup(content, "html.parser")
        elements = soup.find_all()
        for element in elements:
            if element.name in excluded_tags:
                continue
            if element.string:
                if element.string not in excluded_words:
                    translated_text = __translate_text(element.string, src_lang, tgt_lang)
                    element.string.replace_with(translated_text)
            __translate_attributes(element, src_lang, tgt_lang)
        with open(file_path, "w") as file:
            file.write(str(soup))

    def translate(text, src_lang, tgt_lang):
        sents = nltk.tokenize.sent_tokenize(text, "english")
        translated_text = " ".join(mt.translate(sents, source=src_lang, target=tgt_lang))
        return translated_text