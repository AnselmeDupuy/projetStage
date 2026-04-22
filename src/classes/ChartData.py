import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import toml
import json

from paths import BASE_DIR, CONTENT_FOLDER

class ChartData:
    def __init__(self, file):
        self.file = file
        self.data = None
        self.soup = None

        file_name = os.path.basename(self.file).lower()

        if file_name.endswith('.toml'):
            self.data = self.load_data()

        if file_name.endswith(('.html', '.htm')):
            try:
                with open(self.file, 'r', encoding='utf-8') as file:
                    self.soup = BeautifulSoup(file, 'html.parser')
            except Exception as e:
                print("no html file given (chart)", e)


    def load_data(self):
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
        if not self.data:
            return None

        impact_section = self.data.get('impact', {})
        if not isinstance(impact_section, dict):
            return None

        impact_data = {
            key: value
            for key, value in impact_section.items()
        }

        # print(f"Impact data for {self.file}: {impact_data}")
        return impact_data
    
    def send_impact_data_to_JS(self, impact_data=None):
        if impact_data is None:
            impact_data = self.get_impact_data()

        if impact_data is None or self.soup is None or self.soup.body is None:
            return False

        script_tag = self.soup.new_tag('script', id='impact-data', type='application/json')
        script_tag.string = json.dumps(impact_data)
        self.soup.body.append(script_tag)
        return True