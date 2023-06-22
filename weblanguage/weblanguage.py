import torch
import os
import bs4
from bs4 import BeautifulSoup
from tqdm import tqdm
import shutil
import dl_translate as dlt
import nltk

class WebLanguage:
    def __init__(self, folder_path, output_folder, src_lang, tgt_lang, excluded_words=[], excluded_tags=['script', 'style'], verbose=False, progress=True):
        self.folder_path = folder_path
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.excluded_words = excluded_words
        self.excluded_tags = excluded_tags
        self.output_folder = output_folder
        self.verbose = verbose
        self.progress = progress
        self.mt = dlt.TranslationModel(device=self._get_device())

    def _get_device(self):
        if torch.backends.mps.is_available():
            if self.verbose:
                print('[WL] using MPS')
            return 'mps'
        elif torch.cuda.is_available():
            if self.verbose:
                print('[WL] using CUDA')
            return 'cuda'
        else:
            if self.verbose:
                print('[WL] using AUTO, MPS + CUDA unavailable')
            return 'auto'

    def _translate_text(self, text):
        sents = nltk.tokenize.sent_tokenize(text, "english")
        translated_text = " ".join(self.mt.translate(sents, source=self.src_lang, target=self.tgt_lang))
        return translated_text

    def _translate_attributes(self, element):
        attrs_to_translate = ["value", "placeholder", "title"]
        for attr in attrs_to_translate:
            if attr in element.attrs:
                if element[attr] not in self.excluded_words:
                    translated_attr = self._translate_text(element[attr])
                    element[attr] = translated_attr

    def _translate_html_file(self, file_path):
        with open(file_path, "r") as file:
            content = file.read()
        soup = BeautifulSoup(content, "html.parser")
        elements = soup.find_all()
        for element in elements:
            if element.name in self.excluded_tags:
                continue
            if element.string:
                if element.string not in self.excluded_words:
                    translated_text = self._translate_text(element.string)
                    element.string.replace_with(translated_text)
            self._translate_attributes(element)
        with open(file_path, "w") as file:
            file.write(str(soup))

    def _check_and_create_output_folder(self):
        if not os.path.isdir(self.folder_path):
            print('Error: input path does not exist')
            exit(0)

        if os.path.isdir(self.output_folder):
            override = input('Output path already exists. Override? (y/N) ')
            if not ((override.strip().lower() == 'y') or (override.strip().lower() == 'yes')):
                exit(0)
            else:
                print('Overriding.')
        else:
            os.mkdir(self.output_folder)

    def translate_html_files(self):
        self._check_and_create_output_folder()

        files_to_translate = [file_name for file_name in os.listdir(self.folder_path) if file_name.endswith(".html")]
        print('Translating. This may take a while.')
        if self.progress:
            with tqdm(total=len(files_to_translate), desc="Translating HTML files") as pbar:
                for file_name in files_to_translate:
                    shutil.copy(os.path.join(self.folder_path, file_name), os.path.join(self.output_folder, file_name))
                    file_path = os.path.join(self.output_folder, file_name)
                    self._translate_html_file(file_path)
                    pbar.update(1)
        else:
            for file_name in files_to_translate:
                shutil.copy(os.path.join(self.folder_path, file_name), os.path.join(self.output_folder, file_name))
                file_path = os.path.join(self.output_folder, file_name)
                self._translate_html_file(file_path)
                pbar.update(1)