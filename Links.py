# Class create links between files
import xml.etree.ElementPath

from lxml import etree as ET
import functions
import os

class Links:
    def __init__(self, files):
        """
        Create a sections object
        :param files: filenames to be processed
        """

        self.files = files


    def __jaccard(self, set1, set2):
        """
        Calculates the jaccar index between two sets
        :param set1:
        :param set2:
        :return:
        """
        union_length = len(set.union( set1, set2))
        intersection_length = len(set.intersection( set1, set2))

        if union_length == 0 or intersection_length == 0:
            return 0
        else:
            return intersection_length / union_length


    def __jaccard_to_this(self, id):
        """
        Calculates the jaccard index between this and all other documents
        :param id:
        :param keys_in_id:
        :return: list of (id, distance)
        """

        distances = []
        is_section = "_" in id

        for other in self.keys_in_id.keys():
            # Compare sections with sections and articles with articles
            if (is_section and "_" in other) or (not is_section and not "_" in other):
                # Don't compare to yourself
                if other != id  and not other.startswith(id + "_")  and not id.startswith(other + "_"):

                    index = self.__jaccard(self.keys_in_id[id], self.keys_in_id[other])
                    if( index > 0):
                        distances.append( (other, index))

        return distances


    def __create_links(self, parent, distances, treshold):
        """
        Add link elements to the parent depending on the list of (id, distance) tuples
        :param parent:
        :param distances:
        :return:
        """

        links = ET.SubElement(parent, "links")
        for distance in distances:
            if( distance[1] >= treshold):
                link = ET.SubElement(links, "link", attrib={"id": distance[0], "index": str(distance[1])})

        parent.append(links)



    def __read_info(self, elem, articles):
        """
        Returns a set of all links in lowercase
        :param filename:
        :return: keys
        """

        key_elem = elem.find("keys")
        if key_elem is None:  # Always return a list
            keys = []
        else:
            keys = [ key.text.lower() for key in key_elem.iter("key")]


        return set(keys)
        # return set(keys).intersection(articles)


    def read_article_set(self):
        """
        Creates a set of all article titles
        :return: a set with all (lowercase) titles
        """
        articles = set()
        for file in self.files:
            xml = ET.parse(file)
            doc = xml.getroot()
            title = doc.find("title").text
            articles.add(  title.lower())

        return articles


    def read_links(self, articles):
        """
        Returns a dictionary with all keys from the file and the sections
        outgoing hyperlinks
        """

        self.keys_in_id = {}
        for file in self.files:
            xml = ET.parse(file)

            # First the document
            doc = xml.getroot()
            id = doc.attrib["id"]
            self.keys_in_id[id] = self.__read_info( doc, articles)

            # Then the sections
            for section_elem in doc.iter("section"):
                subid = section_elem.attrib["id"]
                self.keys_in_id[id + "_" + subid] = self.__read_info( section_elem, articles)


    def save_distance(self, output_dir, treshold):
        """
        Save the links and the distances in a new file with the keys removed and the links added
        :param output:
        :return:
        """

        for file in self.files:
            xml = ET.parse(file)
            doc = xml.getroot()

            # Compare with all others
            id = doc.attrib["id"]

            nw_doc = ET.Element("doc", attrib={"id": id})
            ET.SubElement(nw_doc,"title").text = doc.find("title").text
            self.__create_links(nw_doc, self.__jaccard_to_this(id), treshold)

            for section_elem in list(doc.iter("section")):
                subid = section_elem.attrib["id"]
                sectionid = id + "_" + subid

                nw_sect = ET.SubElement( nw_doc, "section", attrib={"id": id})
                ET.SubElement(nw_sect, "title").text = section_elem.find("title").text
                ET.SubElement(nw_sect, "text").text = section_elem.find("text").text

                self.__create_links(nw_sect, self.__jaccard_to_this( sectionid), treshold)

            filename = os.path.join( output_dir, os.path.basename( file))
            functions.write_file(filename, functions.xml_as_string( nw_doc))
