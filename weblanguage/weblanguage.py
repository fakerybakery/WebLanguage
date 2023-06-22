# todo implement TQDM
# todo implement JAVASCRIPT translation and CSS "content:" translation
import torch
import os
import bs4
from bs4 import BeautifulSoup
from tqdm import tqdm
import shutil
import dl_translate as dlt
import nltk


class WebLanguage:
    def __init__(
        self,
        folder_path: str,
        output_folder: str,
        src_lang: str,
        tgt_lang: str,
        excluded_words: list[str] = [],
        excluded_tags: list[str] = ["script", "style"],
        verbose: bool = False,
        progress: bool = True,
    ):
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
                print("[WL] using MPS")
            return "mps"
        elif torch.cuda.is_available():
            if self.verbose:
                print("[WL] using CUDA")
            return "cuda"
        else:
            if self.verbose:
                print("[WL] using AUTO, MPS + CUDA unavailable")
            return "auto"

    def _translate_text(self, text):
        sents = nltk.tokenize.sent_tokenize(text, "english")
        translated_text = " ".join(
            self.mt.translate(sents, source=self.src_lang, target=self.tgt_lang)
        )
        return translated_text

    def _translate_attributes(self, element):
        attrs_to_translate = ["value", "placeholder", "title"]
        for attr in attrs_to_translate:
            if attr in element.attrs:
                if element[attr] not in self.excluded_words:
                    translated_attr = self._translate_text(element[attr])
                    element[attr] = translated_attr

    def _translate_html_file(self, file_path):
        with open(file_path, "r", encoding="utf8", errors="ignore") as file:
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
        with open(file_path, "w", encoding="utf8", errors="ignore") as file:
            file.write(str(soup))

    def _check_and_create_output_folder(self):
        if not os.path.isdir(self.folder_path):
            print("Error: input path does not exist")
            exit(0)

        if os.path.isdir(self.output_folder):
            override = input("Output path already exists. Delete folder? (y/N) ")
            if not ((override.strip().lower() == "y") or (override.strip().lower() == "yes")):
                exit(0)
            else:
                shutil.rmtree(self.output_folder)
                os.mkdir(self.output_folder)
                print("Overriding.")
        else:
            os.mkdir(self.output_folder)

    def _translate_files_recursive(self, src_path, dst_path):
        for file_name in os.listdir(src_path):
            file_path = os.path.join(src_path, file_name)
            dst_file_path = os.path.join(dst_path, file_name)

            if os.path.isfile(file_path) and file_name.endswith(".html"):
                shutil.copy(file_path, dst_file_path)
                self._translate_html_file(dst_file_path)
            elif os.path.isdir(file_path):
                new_dst_path = os.path.join(dst_path, file_name)
                os.mkdir(new_dst_path)
                self._translate_files_recursive(file_path, new_dst_path)

    def translate_html_files(self):
        self._check_and_create_output_folder()

        self._translate_files_recursive(self.folder_path, self.output_folder)
        print("Translation complete.")
