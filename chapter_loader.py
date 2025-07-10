import os

DATA_DIR = "chapters"

def get_chapter_path(meta):
    filename = f"class_{meta['class']}_{meta['subject']}_ch{meta['chapter']}.txt"
    path = os.path.join(DATA_DIR, filename)
    return path if os.path.exists(path) else None

def load_chapter(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()