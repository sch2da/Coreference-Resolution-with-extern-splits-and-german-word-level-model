# Masterarbeit
## Coreference Resolution auf Deutsch mit externen Splits der Datensätze und deutschsprachiges word-level Modell

### von Daniel Schmuckermeier im Sommersemester 2022
#### Betreut durch:  Prof. Dr. Abdelmajid Khelil

In diesem Repository ist der gesamte Code, um die Ergebnisse dieser Masterarbeit reproduzieren zu können. Ausgeführt wurde dies auf einem Ubuntu 20.04 Server mit einer Ampere A6000 GPU (45 GB VRAM).
Wie man die Modelle startet, die Daten vollständig preprocesst und die Ergebnisse auswertet, entnehmen sie bitte den entsprechenden Repositorys.

### externe Daten
Modelle: (Die Modellimplementierung von diesem Repository beinhalten kleine Anpassungen/Ergänzungen, um relevante Informationen für die Masterarbeit zu erhalten.)
- [neural-coref Repository, indem sich die Implementierungen vom Coarse-to-fine und Incremental Modell befinden](https://github.com/uhh-lt/neural-coref)
- [wl-coref beinhaltet das word-level Modell](https://github.com/vdobrovolskii/wl-coref)

Datensätze:
- [droc Korpus](https://gitlab2.informatik.uni-wuerzburg.de/kallimachos/DROC-Release)
- [gerdracor-coref Korpus](https://github.com/quadrama/gerdracor-coref)
- [dirndl 2015 (prosody) Korpus](https://www.ims.uni-stuttgart.de/en/research/resources/corpora/dirndl/)

Stanford Parser (mind. Java 1.8):
- [Lade CoreNLP und das deutsche Modell herunter (getestet wurde mit Version 4.4.0)](https://stanfordnlp.github.io/CoreNLP/history.html)
- Entpacke die CoreNLP-Datei
- Verschiebe das deutsche Modell in den entpackten CoreNLP-Ordner
- Starte den CoreNLP Server:
``` 
$ cd /path/to/stanford-corenlp-xxx 
$ java -Xmx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -serverProperties StanfordCoreNLP-german.properties -preload tokenize,ssplit,pos,ner,parse -status_port 9009  -port 9009 -timeout 15000 
```

### Dateien
- [analyze_data.py](./Project/analyze_data.py): Ermittle die Gesamtzahl der Token, Anzahl der Dokumente, etc.
- [convert_dirndl.py](./Project/convert_dirndl.py): Wandle die dirndl-Datensätze ins conll Format um. Für droc und gerdracor-coref befinden sich die Skripte in [neural-coref](./Project/neural-coref/).
- [preprocess.py](./Project/preprocess.py): Preprocesse die conll Dateien in jsonlines. Die Datensätze für das word-level Modell müssen mit dem Parameter ``` --with-parser-values``` gestartet werden. Dazu muss der Standford Parser gestartet werden. Dies kann mehrere Stunden dauern. Anschließend mit [convert_to_heads.py](./Project/wl-coref-german/convert_to_heads.py) den Preprocess-Prozess für das word-level Modell abschließen.
```
$ python preprocess.py --dir-conll /path/to/conll --dir-output /path/to/output --with-parser-values
```
- [split_doc.py](./Project/split_doc.py): Splittet die conll Dokumente, die größer als ```MIN_DOC_LENGTH``` sind in kleinere, conll-konforme Dokumente.

---

Translated into english:

# Master thesis
## Coreference Resolution in German with extern splits of the datasets and German word-level model


### by Daniel Schmuckermeier in summer term 2022
#### Supervised by:  Prof. Dr. Abdelmajid Khelil

In this repository is all the code to reproduce the results of this master thesis. This was run on an Ubuntu 20.04 server with an Ampere A6000 GPU (45 GB VRAM).
How to run the models, preprocess the data completely and evaluate the results can be found in the corresponding repositories.

### extern data
Models: (Model implementations from this repository include minor adjustments/additions to provide relevant information for the master's thesis).
- [neural-coref repository, where the implementations of the coarse-to-fine and incremental model are located](https://github.com/uhh-lt/neural-coref)
- [wl-coref includes the word-level model](https://github.com/vdobrovolskii/wl-coref)


Datasets:
- [droc Corpus](https://gitlab2.informatik.uni-wuerzburg.de/kallimachos/DROC-Release)
- [gerdracor-coref Corpus](https://github.com/quadrama/gerdracor-coref)
- [dirndl 2015 (prosody) Corpus](https://www.ims.uni-stuttgart.de/en/research/resources/corpora/dirndl/)


Stanford Parser (min. Java 1.8):
- [Download CoreNLP and the German model (tested with version 4.4.0)](https://stanfordnlp.github.io/CoreNLP/history.html)
- Unpack the CoreNLP file
- Move the German model into the unzipped CoreNLP folder
- Start the CoreNLP server:
``` 
$ cd /path/to/stanford-corenlp-xxx 
$ java -Xmx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -serverProperties StanfordCoreNLP-german.properties -preload tokenize,ssplit,pos,ner,parse -status_port 9009  -port 9009 -timeout 15000 
```

Files:
- [analyze_data.py](./Project/analyze_data.py): Get the total number of tokens, number of documents, etc.
- [convert_dirndl.py](./Project/convert_dirndl.py): Convert the dirndl records to conll format. For droc and gerdracor-coref, the scripts are in [neural-coref](./Project/neural-coref/).
- [preprocess.py](./Project/preprocess.py): Preprocesses the conll files in jsonlines. The records for the word-level model must be started with the parameter `` --with-parser-values``. For this the Standford parser must be started. This can take several hours. Then finish the preprocess for the word-level model with [convert_to_heads.py](./Project/wl-coref-german/convert_to_heads.py).
```
$ python preprocess.py --dir-conll /path/to/conll --dir-output /path/to/output --with-parser-values
```
- [split_doc.py](./Project/split_doc.py): Splits conll documents larger than ``MIN_DOC_LENGTH`` into smaller, conforming conll documents.





