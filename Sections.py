# Class to split Wikipedia article in sections
from lxml import etree as ET
import functions
import os
import re

class Sections:
    def __init__(self, contents, name, ):
        """
        Create a sections object
        :param contents: Xml contents
        :param name: Name of the file, without extension
        :param output_dir:
        """

        self.xml = ET.fromstring( contents)
        self.name = name


    def __remove_everything_but_text(self, text):
        clean = text
        clean = re.sub(r"\{\{Infobox.*?\}\}", "", clean)  # Remove the infobox

        return clean



    def create_sections(self, output_dir):
        """
        Create sections into the output dir
        :param output_dir:
        :return:
        """

        text = self.xml.find("text").text
        text = self.__remove_everything_but_text(text)

        functions.write_file(os.path.join(output_dir, f"{self.name}.xml"), text)
#        functions.write_file( os.path.join(output_dir, f"{self.name}.xml"), functions.xml_as_string( self.xml))

