import os
import sys
from bs4 import BeautifulSoup

from paths import BASE_DIR, CONTENT_FOLDER

class NavGen:
    """Classe pour gérer la navigation et récupérer les fichiers d'incidents"""
    
    def __init__(self):
        """Initialise navgen en chargeant la liste des fichiers du dossier content"""
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
        """Affiche la liste de tous les fichiers chargés"""
        for file in self.files:
            print(file)

    def get_files(self):
        """Retourne la liste des fichiers d'incidents"""
        return self.files
    
    def get_file_numbers(self):
        """Retourne le nombre total de fichiers chargés"""
        return len(self.files)
    

    