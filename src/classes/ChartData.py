import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import toml
import json

from paths import BASE_DIR, CONTENT_FOLDER

class ChartData:
    """Classe pour extraire et gérer les données d'impact depuis les fichiers TOML"""
    
    def __init__(self, file):
        """Initialise avec un fichier TOML ou HTML et charge les données"""
        self.file = file
        self.data = None  # Données TOML parsées
        self.soup = None  # Document HTML parsé

        file_name = os.path.basename(self.file).lower()

        # Charge les données TOML si c'est un fichier .toml
        if file_name.endswith('.toml'):
            self.data = self.load_data()

        # Parse un fichier HTML s'il est fourni
        if file_name.endswith(('.html', '.htm')):
            try:
                with open(self.file, 'r', encoding='utf-8') as file:
                    self.soup = BeautifulSoup(file, 'html.parser')
            except Exception as e:
                print("no html file given (chart)", e)


    def load_data(self):
        """Charge et parse un fichier TOML, retourne les données ou False en cas d'erreur"""
        try:
            if os.path.exists(self.file):
                toml_path = self.file
            else:
                toml_path = os.path.join(CONTENT_FOLDER, os.path.basename(self.file))

            with open(toml_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except Exception as e:
            print(f"Error loading TOML file: {self.file}", e)
            return False


    def get_impact_data(self):
        """Extrait et retourne la section 'impact' du fichier TOML"""
        if not self.data:
            return None

        impact_section = self.data.get('impact', {})
        if not isinstance(impact_section, dict):
            return None

        # Retourne un dictionnaire avec toutes les données d'impact
        impact_data = {
            key: value
            for key, value in impact_section.items()
        }

        return impact_data
    
    def send_impact_data_to_JS(self, impact_data=None):
        """Injecte les données d'impact dans un script JSON du document HTML"""
        if impact_data is None:
            impact_data = self.get_impact_data()

        if impact_data is None or self.soup is None or self.soup.body is None:
            return False

        # Crée un tag script contenant les données en JSON
        script_tag = self.soup.new_tag('script', id='impact-data', type='application/json')
        script_tag.string = json.dumps(impact_data)
        self.soup.body.append(script_tag)
        return True