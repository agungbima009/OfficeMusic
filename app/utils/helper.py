import re

def safe_filename(text):

    return re.sub(
        r'[\\/*?:"<>|]',
        "",
        text
    )