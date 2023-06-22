import weblanguage
from pywebcopy import save_webpage
import os
save_webpage(
      url="https://github.com/",
      project_folder=os.path.abspath('nosync_website'),
      bypass_robots=True,
      debug=True,
      open_in_browser=True,
      delay=None,
      threaded=True
)
folder_path = "nosync_website"
src_lang = "en"
tgt_lang = "fr"
excluded_words = ["GitHub"]
output_folder = "output"
translator = weblanguage.WebLanguage(folder_path, output_folder, src_lang, tgt_lang, excluded_words, progress=True)
translator.translate_html_files()
