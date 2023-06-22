from pywebcopy import save_webpage
import os
save_webpage(
      url="https://httpbin.org/",
      project_folder=os.path.abspath('website'),
    #   project_name="my_site",
      bypass_robots=True,
      debug=True,
      open_in_browser=True,
      delay=None,
      threaded=True,
)
