# Class to read S2ORC Corpus

import functions
import orjson
import os
from lxml import etree as ET

class S2ORC:

    def __init__(self, metadata, pdf_parses):
        """
        Read the S2ORC corpus
        :param input_dir: Directory with pdf_parses
        """
        self.metadata_dir = metadata
        self.pdf_parses_dir = pdf_parses
        self.metadata = self.__read_all_metadata()


    def __read_all_metadata(self):
        """
        Read all metadata in a dictionary
        :return: a dictionary with the id as key and the metadata as value
        """

        metadata = {}
        for file in functions.read_all_files_from_directory(self.metadata_dir, "json"):
            for info in self.__read_objects_from_file( file):
                # Only entries with full text and bib_entries for the links
                if info["has_pdf_parse"]:
                    if info["has_pdf_parsed_body_text"] and info["has_pdf_parsed_bib_entries"]:
                        id = info["paper_id"]
                        metadata[id] = info

        return metadata



    def __read_objects_from_file(self, filename):
        """
        Read all lines from the file in a list of dictionaries with the json properties
        :param filename:
        :return: list of dictionaries with the json properties
        """
        dicts = []
        print( filename)
        with open(filename) as file:
            for line in file.readlines():
                dicts.append( orjson.loads(line))

        return dicts



    def __read_bibentry_link_translation(self, info):
        """
        Create a dictionary that contains all bibentries that contain a link of a paper in this set
        :param info:
        :return:
        """

        translation = {}
        entries = info["bib_entries"]
        for entry in entries.keys():
            link = entries[entry]["link"]
            if link in self.metadata:
                translation[entry] = link

        return translation


    def __create_link_node(self, parent, links):
        """
        Appends a links node to the parent node and fills it with link elements containing
        the ids in links
        :param parent:
        :param links:
        :return:
        """

        links_node = ET.SubElement( parent, "links")
        link_set = set( links)  # Just unique values
        for link in link_set:
            ET.SubElement(links_node, "link").text = str(link)

    def __resolve_links_section(self, section, bib_entries):
        """
        Resolves the links in the section text and removes the text of the link from the text
        :param section:
        :param bib_entries: All entries from the bibiography
        :return: (text, links)      Cleaned text and resolved links
        """

        text = section["text"]
        links = []
        for cite in section["cite_spans"]:
            cite_text = cite["text"]
            ref_id = cite["ref_id"]
            text = text.replace(cite_text, "")  # Remove the citation from the text
            if (ref_id in bib_entries):
                links.append(bib_entries[ref_id])
                print( ref_id)

        return (text, links)



    def __convert_info_to_xml(self, info, output_dir):
        """
        Convert the json object to an Xml file and put it in the output directory
        :param info:
        :param output_dir:
        :return:
        """

        id = info["paper_id"]
        metadata = self.metadata[id]

        bib_entries = self.__read_bibentry_link_translation(info)

        doc = ET.Element("doc", attrib={"id": id})
        ET.SubElement( doc, "title").text = metadata["title"]

        # Add the links
        links = [link for link in metadata["outbound_citations"] if link in self.metadata]  # Only links to papers in this set
        self.__create_link_node( doc, links)


        # Now the sections
        section_id = 1
        for section in info["body_text"]:
            section_node = ET.SubElement(doc, "section", attrib={"id": id, "subid": str(section_id)})
            (text, links) = self.__resolve_links_section(section, bib_entries)

            ET.SubElement( section_node, "title").text = section["section"]
            ET.SubElement( section_node, "text").text = text
            self.__create_link_node( section_node, links)

            section_id += 1


        # Write the xml
        filename = os.path.join( output_dir, f"{id}.xml")
        functions.write_file(filename, functions.xml_as_string(doc))




    def convert_to_xml(self, output_dir):
        """
        Convert all objects to Xml and put them in the output directory
        :param output_dir:
        :return:
        """

        for file in functions.read_all_files_from_directory(self.pdf_parses_dir, "json"):
            for info in self.__read_objects_from_file( file):
                id = info["paper_id"]

                # Copy this paper if qualified
                if id in self.metadata:
                    self.__convert_info_to_xml(info, output_dir)
