#!/bin/sh

cd /Users/jstegink/Dropbox/John/Studie/OU/Afstuderen/Thesis/Corpora/code/WikiDataCorpus
source venv/bin/activate

OUTPUT_DIR=/users/jstegink/thesis/corpora


#echo WikiData NL
#rm -r $OUTPUT_DIR/wikidata/nl
##venv/bin/python WikiDataCorpus.py -s "wd:Q7397" -l nl -o $OUTPUT_DIR/wikidata/nl  # Software
#venv/bin/python WikiDataCorpus.py -s "wd:Q413" -l nl -o $OUTPUT_DIR/wikidata/nl  # Software
#venv/bin/python WikiDataCorpus.py -s "wd:Q2329" -l nl -o $OUTPUT_DIR/wikidata/nl  # Software
#venv/bin/python WikiDataCorpus.py -s "wd:Q8008" -l nl -o $OUTPUT_DIR/wikidata/nl  # Software


#echo WikiData EN
#rm -r $OUTPUT_DIR/wikidata/en
## Physics
#venv/bin/python WikiDataCorpus.py -s "wd:Q413" -l en -o $OUTPUT_DIR/wikidata/en
## Chemistry
#venv/bin/python WikiDataCorpus.py -s "wd:Q2329" -l en -o $OUTPUT_DIR/wikidata/en

#echo WikiMatch NL
#rm -r $OUTPUT_DIR/wikimatch/nl
#venv/bin/python GWikiMatchCorpus.py -i GWikiMatch -l nl -o $OUTPUT_DIR/wikimatch/nl
##echo WikiMatch EN
#rm -r $OUTPUT_DIR/wikimatch/en
#venv/bin/python GWikiMatchCorpus.py -i GWikiMatch -l en -o $OUTPUT_DIR/wikimatch/en

#echo WiRe NL
rm -r $OUTPUT_DIR/WiRe/nl
venv/bin/python GWikiMatchCorpus.py -i WiRe -l nl -o $OUTPUT_DIR/WiRe/nl
#echo WiRe EN
rm -r $OUTPUT_DIR/WiRe/en
venv/bin/python GWikiMatchCorpus.py -i WiRe -l en -o $OUTPUT_DIR/WiRe/en
venv/bin/python GWikiMatchCorpus.py -i WiRe -l en -o $OUTPUT_DIR/WiRe/en

#echo WikiSim NL
rm -r $OUTPUT_DIR/WikiSim/nl
venv/bin/python GWikiMatchCorpus.py -i WikiSim -l nl -o $OUTPUT_DIR/WikiSim/nl
#echo WikiSim EN
rm -r $OUTPUT_DIR/WikiSim/en
venv/bin/python GWikiMatchCorpus.py -i WikiSim -l en -o $OUTPUT_DIR/WikiSim/en

#
#echo S2ORC
#rm -r $OUTPUT_DIR/S2ORC
#venv/bin/python S2ORCCorpus.py -s "History" -m "../../S2ORC/Lezen/metadata" -p "../../S2ORC/Lezen/pdf_parses" -o  $OUTPUT_DIR/S2ORC
#S2ORC