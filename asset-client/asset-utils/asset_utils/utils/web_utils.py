import os
import platform
import webbrowser


def chrome_path():
    if platform.system() == 'Linux':
        path = '/usr/bin/google-chrome %s'
    elif platform.system() == 'Darwin':
        path = 'open -a /Applications/Google\ Chrome.app %s'
    else:
        # Windows
        path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    return path


def open_in_browser(url: str):
    if os.path.exists(os.path.realpath(url)):
        # local file
        url = 'file://' + os.path.realpath(url)
    try:
        webbrowser.get(chrome_path()).open(url=url)
        return True
    except webbrowser.Error as e:
        print(f"error in opening browser:{e}")
        return False
