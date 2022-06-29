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



    def __get_keys(self, part):
        """
        Returns a list of links to other articles that can be used as keys for this article
        :param part:
        :return:
        """

        keys = ET.Element("keys")
        for link in part.wikilinks:
            if not ":" in link:
                ET.SubElement( keys, "key").text = link.target

        return keys



    def __split_text_and_title(self, text):
        """
        Splits the text and title, the title is the first line of the document
        :return: (title, text)
        """

        text_parts = text.partition("\n")
        if len(text_parts) > 1:
            return (text_parts[0].strip(), "\n".join(text_parts[1:]).strip())
        else: # No room for a title
            return ("", text)



    def create_sections(self):
        """
        Create sections into the output dir
        :param output_dir:
        :return: the number of sections without the main section
        """

        text = self.xml.find("text").text
        title = self.xml.find("title").text
        page = wtp.parse( text)

        # The main part of the Xml
        doc = ET.Element("doc", attrib={"id": self.name})
        ET.SubElement( doc, "title").text = title
        doc.append( self.__get_keys(page))

        # Now per section
        id_counter = 1
        for section in page.sections:
            section_elem = ET.SubElement( doc, "section", attrib={"id": f"{id_counter:02}"})

            if( id_counter > 1): # Split if this is not the first section
                (section_title, section_text) = self.__split_text_and_title( section.plain_text())
            else:
                section_title = ""
                section_text = section.plain_text()

            ET.SubElement(section_elem, "title").text = section_title
            section_elem.append(self.__get_keys(section))
            ET.SubElement(section_elem, "text").text = section_text

            id_counter += 1

        # Write the xml
        filename = os.path.join( self.output_dir, f"{self.name}.xml")
        functions.write_file(filename, functions.xml_as_string(doc))

        return id_counter - 1 # The number of sections, without the main section