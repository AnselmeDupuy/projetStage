import os
import sys
from bs4 import BeautifulSoup
from csscompressor import compress as css_compress
from jsmin import jsmin
import classes.TagGenerator as TagGenerator
import classes.TagSelector as TagSelector
import classes.NavGen as NavGen

def example_manual_tags():
    html_file = 'src/templates/index.html'
    toml_folder = 'src/content'
    tag_generator = TagGenerator.TagGenerator(html_file, toml_folder)

    files = NavGen.NavGen().get_files()

    tag_generator.generate_nav_items(files)

    for file in files:
        tag_generator.generate_html_from_toml(file)

    
    tag_generator.save_html("src/incidents/test.html")


def main():
    example_manual_tags()

if __name__ == "__main__":
    main()