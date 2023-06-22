import weblanguage
folder_path = "example_html"
src_lang = "en"
tgt_lang = "fr"
excluded_words = ["WebLanguage"]
output_folder = "output"

# translator = weblanguage.WebLanguage(folder_path, src_lang, tgt_lang, excluded_words, excluded_tags, output_folder)
translator = weblanguage.WebLanguage(folder_path, output_folder, src_lang, tgt_lang, excluded_words, progress=True)
translator.translate_html_files()
