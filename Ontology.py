# Class to read articles with the given subject from WikiData
from SPARQLWrapper import SPARQLWrapper, JSON


class Ontology:

    def __init__(self, wikidata_endpoint, subject):
        """
        :param wikidata_endpoint: Wikidata SPARQL endpoint
        :param subject: subject for the articles
        """
        self.wikidata = wikidata_endpoint
        self.subject = subject

        # Check the subject
        message = Ontology.check_subject( subject)
        if message != "":
            raise Exception( message)



    @staticmethod
    def check_subject( subject):
        """
        Checks if a subject is valid.
        :param subject: The subject to be checked
        :return: "" if OK, a error message otherwise
        """

        subjects = ["software", "animals"]
        if subject not in subjects:
            return f"Invalid subject, please use one of the following: {', '.join( subjects)}."
        else:
            return ""


