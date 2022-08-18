# Class to split Wikipedia article in sections
from lxml import etree as ET
import functions
import os
import re
import wikitextparser as wtp

class Sections:
    def __init__(self, contents):
        """
        Create a sections object
        :param contents: Xml contents
        """

        self.xml = ET.fromstring( contents)
        self.contents = contents


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
        Returns a list of links to other articles that can be used as keys for this article in the "keys" element
        :param part:
        :return:
        """

        keys = ET.Element("keys")
        for link in part.wikilinks:
            if not ":" in link:
                ET.SubElement( keys, "key").text = link.target

        return keys



    def __get_links(self, links):
        """
        Returns a list of links to other articles in the "links" element
        :param part:
        :return:
        """

        links_elem = ET.Element("links")
        for link in links:
            ET.SubElement( links_elem, "link", attrib={"id": str(link[0]), "index": "", "class": str(link[1])})

        return links_elem



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


    def create_sections_xml(self, with_keys, links, id):
        """
        Create sections as xml file
        :param with_keys if True a document with keys (outlinks) is created otherwise the parameter links is used for the document
        :param links  if with_keys is False the links will be added to the link section of the document and the section will have no links
        :param id
        :return: the number of sections without the main section and the number of sections in a tuple (xml, nrofsections)
        """
        text = self.xml.find("text").text
        title = self.xml.find("title").text
        page = wtp.parse( text)

        # The main part of the Xml
        doc = ET.Element("doc", attrib={"id": id})
        ET.SubElement( doc, "title").text = title
        if with_keys:
            doc.append( self.__get_keys(page))
        else:
            doc.append( self.__get_links(links))

        # Now per section
        id_counter = 1
        for section in page.sections:

            if( id_counter > 1): # Split if this is not the first section
                (section_title, section_text) = self.__split_text_and_title( section.plain_text())
            else:
                section_title = ""
                section_text = section.plain_text()
                section_text = re.sub(r"\{[^}+]}", "", section_text)

            if len(section_text) > 10:  # Some data
                section_elem = ET.SubElement(doc, "section", attrib={"id": f"{id}_{id_counter:02}"})
                ET.SubElement(section_elem, "title").text = section_title
                if with_keys:
                    section_elem.append(self.__get_keys(section))
                else:
                    section_elem.append(self.__get_links([]))
                ET.SubElement(section_elem, "text").text = section_text

                id_counter += 1

        return (functions.xml_as_string(doc), id_counter )


    def create_sections(self, with_keys, links, id, output_dir):
        """
        Create sections into the output dir
        :param with_keys if True a document with keys (outlinks) is created otherwise the parameter links is used for the document
        :param links  if with_keys is False the links will be added to the link section of the document and the section will have no links
        :param id
        :param output_dir
        :return: the number of sections without the main section
        """

        # Write the xml
        (xml, nrofsections) = self.create_sections_xml( with_keys, links, id)
        filename = os.path.join( output_dir, f"{id}.xml")
        functions.write_file(filename, xml )

        return nrofsections
