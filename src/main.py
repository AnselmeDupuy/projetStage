import os
import sys
from bs4 import BeautifulSoup
from csscompressor import compress as css_compress
from jsmin import jsmin
import classes.TagGenerator as TagGenerator
import classes.NavGen as NavGen
import classes.ChartData as ChartData

def generate_html():
    """Génère le fichier HTML complet avec les données d'incidents et graphiques associés"""
    html_file = 'templates/index.html'
    toml_folder = 'src/content'
    tag_generator = TagGenerator.TagGenerator(html_file, toml_folder)
    files = []
    chart_data = {}
    
    # Récupère la liste de tous les fichiers du dossier content
    files = NavGen.NavGen().get_files()

    # Filtre pour garder uniquement les fichiers TOML
    for file in files:
        if os.path.splitext(file)[1] != '.toml':
            files.pop(files.index(file))

    # Crée les éléments de navigation
    tag_generator.generate_nav_items(files)

    # Traite chaque fichier incident: génère les cartes visibles et les détails cachés
    for file in files:
        tag_generator.generate_card_info(file)
        tag_generator.generate_html_from_toml(file)
        chart_data[file] = ChartData.ChartData(file).get_impact_data()

    # Ajoute les scripts JavaScript
    tag_generator.generate_JS()
    
    # Sauvegarde le fichier HTML final avec les données pour les graphiques
    tag_generator.save_html("incidents/test.html", chart_data)


def main():
    """Fonction principale qui lance la génération"""
    generate_html()

if __name__ == "__main__":
    main()