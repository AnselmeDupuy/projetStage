import os
import sys
from bs4 import BeautifulSoup

from paths import BASE_DIR, CONTENT_FOLDER

class NavGen:
    def __init__(self):
        self.base_dir = BASE_DIR
        self.folder = CONTENT_FOLDER
        self.files = []
        try:
            self.files = [
                name for name in os.listdir(CONTENT_FOLDER)
                if os.path.isfile(os.path.join(CONTENT_FOLDER, name))
            ]
        except FileNotFoundError:
            print("no content folder found")

    def print_files(self):
        for file in self.files:
            print(file)

    def get_files(self):
        return self.files
    
    def get_file_numbers(self):
        return len(self.files)
    

    