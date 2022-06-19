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
        Calculates the jaccar distance between two sets
        :param set1:
        :param set2:
        :return:
        """
        union_length = float( len(set.union( set1, set2)))
        intersection_length = float( len(set.intersection( set1, set2)))

        if union_length == 0 or intersection_length == 0:
            return 0
        else:
            return (union_length - intersection_length) / union_length


    def __jaccard_to_this(self, id):
        """
        Calculates the jaccard distance between this and all other documents
        :param id:
        :param keys_in_id:
        :return: list of (id, distance)
        """

        distances = []
        for other in self.keys_in_id.keys():
            if other != id  and not other.startswith(id + "_")  and not id.startswith(other + "_"):
                dist = self.__jaccard(self.keys_in_id[id], self.keys_in_id[other])
                if( dist > 0):
                    distances.append( (id, dist))

        return distances


    def __create_links(self, parent, distances):
        """
        Add link elements to the parent depending on the list of (id, distance) tuples
        :param parent:
        :param distances:
        :return:
        """

        links = ET.SubElement(parent, "links")
        for distance in distances:
            link = ET.SubElement(links, "link", attrib={"id": distance[0], "distance": str(distance[1])})

        parent.append(links)
        ## remove the key elements
        keys = parent.find("keys")
        if not keys is None:
            parent.remove( keys)



    def __read_info(self, elem):
        """
        Reads the id and a list of keys from the element
        :param filename:
        :return: keys
        """

        key_elem = elem.find("keys")
        if key_elem is None:  # Always return a list
            keys = []
        else:
            keys = [ key.text for key in key_elem.iter("key")]

        return keys


    def read_links(self):
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
            keys = self.__read_info( doc)
            self.keys_in_id[id] = set(keys)

            # Then the sections
            for section_elem in doc.iter("section"):
                subid = section_elem.attrib["id"]
                keys = self.__read_info( section_elem)
                self.keys_in_id[id + "_" + subid] = set(keys)


    def save_distance(self, output_dir):
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
            self.__create_links(doc, self.__jaccard_to_this(id))

            for section_elem in doc.iter("section"):
                subid = section_elem.attrib["id"]
                sectionid = id + "_" + subid
                self.__create_links(section_elem, self.__jaccard_to_this( sectionid))

            filename = os.path.join( output_dir, os.path.basename( file))
            functions.write_file(filename, functions.xml_as_string(doc))
