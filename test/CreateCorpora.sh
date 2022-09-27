#!/bin/sh

cd /Users/jstegink/Dropbox/John/Studie/OU/Afstuderen/Thesis/Corpora/code/WikiDataCorpus
source venv/bin/activate

OUTPUT_DIR=/users/jstegink/thesis/corpora


echo WikiData NL
rm -r $OUTPUT_DIR/wikidata/nl
venv/bin/python WikiDataCorpus.py -s "wd:Q7397" -l nl -o $OUTPUT_DIR/wikidata/nl

#echo WikiData EN
#rm -r $OUTPUT_DIR/wikidata/en
## Physics
#venv/bin/python WikiDataCorpus.py -s "wd:Q413" -l en -o $OUTPUT_DIR/wikidata/en
## Chemistry
#venv/bin/python WikiDataCorpus.py -s "wd:Q2329" -l en -o $OUTPUT_DIR/wikidata/en
#
#echo WikiMatch NLls

#rm -r $OUTPUT_DIR/wikimatch/nl
#venv/bin/python GWikiMatchCorpus.py -l nl -o $OUTPUT_DIR/wikimatch/nl
##echo WikiMatch EN
#rm -r $OUTPUT_DIR/wikimatch/en
#venv/bin/python GWikiMatchCorpus.py -l en -o $OUTPUT_DIR/wikimatch/en
#
#echo S2ORC
#rm -r $OUTPUT_DIR/S2ORC
#venv/bin/python S2ORCCorpus.py -s "History" -m "../../S2ORC/Lezen/metadata" -p "../../S2ORC/Lezen/pdf_parses" -o  $OUTPUT_DIR/S2ORC
