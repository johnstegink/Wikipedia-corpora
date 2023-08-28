#!/bin/zsh

#
# Creates all corpora
#

COPRUSDIR=/Volumes/Extern/Studie/studie/corpora
CURRENT=`pwd`

VENVDIR=/Users/jstegink/Dropbox/John/Studie/OU/Afstuderen/Thesis/Corpora/code/WikiDataCorpus/venv/bin
SCRATCHDIR=/Volumes/Extern/Studie/studie/scratch

source $VENVDIR/activate
cd $CURRENT

# # Wikidata (physics)
# $VENVDIR/python WikiDataCorpus.py -s "wd:Q413" -l nl -o $COPRUSDIR/wikidata_nl 
# $VENVDIR/python WikiDataCorpus.py -s "wd:Q413" -l en -o $COPRUSDIR/wikidata_en 

# # WikiSim
# $VENVDIR/python wire2gwikimatch.py -i Wikisim/WikiSim.csv -o $SCRATCHDIR/WikiSim_nl/data.tsv -c=6
# $VENVDIR/python GWikiMatchCorpus.py -l nl -i $SCRATCHDIR/WikiSim_nl -o $COPRUSDIR/wikisim_nl
# $VENVDIR/python wire2gwikimatch.py -i Wikisim/WikiSim.csv -o $SCRATCHDIR/WikiSim_en/data.tsv -c=6
# $VENVDIR/python GWikiMatchCorpus.py -l en -i $SCRATCHDIR/WikiSim_en -o $COPRUSDIR/wikisim_en

# # WiRe
 $VENVDIR/python wire2gwikimatch.py -i WiRe/WiRe.csv -o $SCRATCHDIR/WiRe_nl/data.tsv -c=6
 $VENVDIR/python GWikiMatchCorpus.py -l nl -i $SCRATCHDIR/WiRe_nl -o $COPRUSDIR/WiRe_nl
 $VENVDIR/python wire2gwikimatch.py -i WiRe/WiRe.csv -o $SCRATCHDIR/WiRe_en/data.tsv -c=6
 $VENVDIR/python GWikiMatchCorpus.py -l en -i $SCRATCHDIR/WiRe_en -o $COPRUSDIR/WiRe_en

# # WikiMatch
#$VENVDIR/python GWikiMatchCorpus.py -l nl -i GwikiMatch -o $COPRUSDIR/gWikimatch_nl
#$VENVDIR/python GWikiMatchCorpus.py -l en -i GwikiMatch -o $COPRUSDIR/gWikimatch_en
