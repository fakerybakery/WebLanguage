import weblanguage
folder_path = "example_html"
src_lang = "en"
tgt_lang = "fr"
excluded_words = ["WebLanguage"]
excluded_tags = ["script", "style"]
output_folder = "output"

translator = weblanguage.WebLanguage(folder_path, src_lang, tgt_lang, excluded_words, excluded_tags, output_folder)
translator.translate_html_files()
