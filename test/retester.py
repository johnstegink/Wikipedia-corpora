import re

curly_braces_re = re.compile(r"\{[^}]+}")
category_re = re.compile(r"^Category:.*?$", flags=re.MULTILINE | re.IGNORECASE)
white_spaces_re = re.compile(r"\s+")


def clean_wiki_text( text):
    """
    Clean the text coming from wikipedia
    :param self:
    :param text:
    :return:
    """
    clean = curly_braces_re.sub("", text) # Remove everyting between curly braces
    clean = category_re.sub("", clean) # Remove the categories
    clean = clean.replace("=====", "")
    clean = clean.replace("====", "")
    clean = clean.replace("===", "")
    clean = clean.replace("==", "")

    # Remove white spaces and list items
    not_list_item_or_empty_lines = [line for line in clean.split("\n") if not line.strip().startswith("*") and white_spaces_re.sub("", line) != ""]
    clean = "\n".join(not_list_item_or_empty_lines)

    return clean




with open("/Users/jstegink/thesis/corpora/testset/en/r_149.xml", "r") as f:
    inhoud = f.read()

print( clean_wiki_text( inhoud))

