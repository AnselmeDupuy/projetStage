import os
import sys
from bs4 import BeautifulSoup
from csscompressor import compress as css_compress
from jsmin import jsmin
import classes.TagGenerator as TagGenerator
import classes.NavGen as NavGen

def generate_html():
    html_file = 'templates/index.html'
    toml_folder = 'src/content'
    tag_generator = TagGenerator.TagGenerator(html_file, toml_folder)

    files = NavGen.NavGen().get_files()

    tag_generator.generate_nav_items(files)
    

    for file in files:
        tag_generator.generate_html_from_toml(file)

    
    tag_generator.generate_JS(html_file)
    tag_generator.save_html("incidents/test.html")


def main():
    generate_html()

if __name__ == "__main__":
    main()