# Class to split Wikipedia article in sections
from lxml import etree as ET
import functions
import os
import re
import wikitextparser as wtp

class Sections:
    def __init__(self, contents, id, output_dir ):
        """
        Create a sections object
        :param contents: Xml contents
        :param name: Name of the file, without extension
        :param output_dir:
        """

        self.xml = ET.fromstring( contents)
        self.contents = contents
        self.id = id
        self.name = f"{id:05}"
        self.output_dir = output_dir


    def __get_tekst(self, part):
        """
        Gets the plain text
        :param part:
        :return:
        """
        text = part.plain_text().replace("=", " ")

        elem = ET.Element("text")
        elem.text = text

        return text.strip()


    def __get_node(self, name, contents):
        """
        Creates a node with the given name and contents
        :param name:
        :param contents:
        :return:
        """
        elem = ET.Element(name)
        elem.text = contents

        return elem



    def __get_links(self, part):
        """
        Returns a list of links to other articles
        :param part:
        :return:
        """

        linksElem = ET.Element("links")
        for link in part.wikilinks:
            linkElem = ET.Element("link")
            linkElem.text = link.target
            linksElem.append( linkElem)

        return linksElem


    def __save_xml(self, part, id, title, subid):
        """
        Create the xml and save it a file with the given id
        :param part:
        :param id:
        :param title:
        :param use_subtitle:
        :return:
        """
        text = self.__get_tekst( part)
        subtitle = ""

        # Split the text into a subtitle and text if neccesairy
        if subid == 1:
            subtitle = "introduction"
        elif subid > 1:
            text_parts = text.partition("\n")
            if len( text_parts) > 1:
                subtitle = text_parts[0].strip()
                text = "\n".join( text_parts[1:]).strip()


        doc = ET.Element("doc")
        doc.append( self.__get_node( "title", title))
        doc.append( self.__get_node( "subtitle", subtitle))
        doc.append( self.__get_node( "id", id))
        doc.append( self.__get_node( "text", text))
        doc.append( self.__get_links( part))

        filename = os.path.join( self.output_dir, f"{id}.xml")
        functions.write_file(filename, functions.xml_as_string(doc))



    def create_sections(self):
        """
        Create sections into the output dir
        :param output_dir:
        :return:
        """

        text = self.xml.find("text").text
        title = self.xml.find("title").text
        page = wtp.parse( text)

        self.__save_xml(page, self.name, title, 0)

        id_counter = 1
        for section in page.sections:
            id = f"{self.name}_{id_counter:02}"
            self.__save_xml(section, id, title, id_counter)
            id_counter += 1

