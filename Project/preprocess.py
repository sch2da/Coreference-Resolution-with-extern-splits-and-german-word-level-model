import os
import logging
import argparse
from collections import defaultdict

import jsonlines
from nltk.parse import CoreNLPDependencyParser

logger = logging.getLogger()
logger.setLevel(logging.INFO)
LOG_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s: \t %(message)s', "%Y-%m-%d %H:%M:%S")
# Logger console
sh = logging.StreamHandler()
sh.setFormatter(LOG_FORMATTER)
sh.setLevel(logging.INFO)
logger.addHandler(sh)

FILE_ENDING_JSONLINES = ".jsonlines"
DOC_PATTERN = "#end document"
SENT_PATTERN = "\n\n"

class CorefSpansHolder:
    """
    A simple container to process coreferent spans line by line
    (as previous information might be needed)

    self.starts contains word indices of span starts
    self.spans contains spans that have been built

    Both dictionaries use entity indices as keys.
    """
    def __init__(self):
        self.starts = defaultdict(lambda: [])
        self.spans = defaultdict(lambda: [])

    def __iter__(self):
        for start_lst in self.starts.values():
            try:
                assert len(start_lst) == 0
            except:
                logger.error("start list not empty")
                logger.error("start_lst: " + str(start_lst) + " " + str(len(start_lst)))
        return iter(self.spans.values())

    def add(self, coref_info: str, word_id: int, line: str):
        """
        Examples of coref_info: "(50)", "(50", "50)", "(50)|(80" etc
        """
        coref_info = coref_info.strip().split("|")
        for ci in coref_info:
            self._add_one(ci, word_id, line)

    def _add_one(self, coref_info: str, word_id: int, line: str):
        if coref_info[0] == "(":
            if coref_info[-1] == ")":
                entity_id = int(coref_info[1:-1])
                self.spans[entity_id].append([word_id, word_id + 1])
            else:
                entity_id = int(coref_info[1:])
                self.starts[entity_id].append(word_id)
        elif coref_info[-1] == ")":
            try:
                entity_id = int(coref_info[:-1])
                self.spans[entity_id].append(
                    [self.starts[entity_id].pop(), word_id + 1])
            except:
                logger.error("Closing coref_info without opening coref_info: " + line)
        else:
            logger.error("ValueError raised: Invalid coref_info: " + coref_info)
            raise ValueError(f"Invalid coref_info: {coref_info}")


def extract_one_file(filename_input, dir_conll, dir_output):
    # Delete old preprocessed file
    if os.path.exists(args.dir_output) and os.path.exists(args.dir_output + "/" + filename_input + FILE_ENDING_JSONLINES):
        os.remove(args.dir_output + "/" + filename_input + FILE_ENDING_JSONLINES)

    with open(args.dir_conll +  "/" + filename_input, mode="r", encoding="utf8") as f_input:
        doc = f_input.read().split(DOC_PATTERN)
    
    doc_counter = 0
    doc_counter_not_failed = 0
    sents_counter = 0
    sents_counter_failed = 0

    for d in doc:
        if d.isspace():
            continue
        blocks = d.split(SENT_PATTERN)

        data = {
            "document_id":      "",
            "cased_words":      [],
            "sent_id":          [],
            "part_id":          [],
            "speaker":          [],
            "pos":              [],
            "deprel":           [],
            "head":             [],
            "clusters":         []
        }
        coref_spans = CorefSpansHolder()
        total_words = 0
        sent_id = 0

        for b in blocks:
            all_sent = list(b.splitlines())
            only_sent = []
            raw_sent = []
            for s in all_sent:
                if not s:
                    continue
               
                doc_id = ""
                sents_counter += 1
                s.strip()
                s_splitted = s.split()
                if s.startswith("#begin document"):
                    if "_splitted" in s and "droc" in filename_input:
                        doc_id = s_splitted[2].replace("(","").replace(")","").replace(";","")
                        temp = s_splitted[-1].split("_")
                        s_splitted[-1] = "_".join(temp[0:-2])
                        data["part_id"] = int(s_splitted[-1][-3:].replace("(","").replace(")","").replace(";",""))
                    else:
                        doc_id = s_splitted[2].replace("(","").replace(")","").replace(";","")                
                        data["part_id"] = int(s_splitted[-1][-3:].replace("(","").replace(")", "").replace(";",""))
                    
                    data["document_id"] = doc_id + "_" + str(data["part_id"])


                if s.startswith(doc_id):
                    only_sent.append(s)
                    try:
                        raw_sent.append(s_splitted[3])
                    except:
                        logger.warning("raw sent not append " + s)
                    continue
                
            raw_sent_joined = " ".join(raw_sent)
            parsed_sent = ""
            is_equal_length = True
            if raw_sent_joined:    
                if args.with_parser_values:
                    parsed_sent = get_parse_sent(raw_sent_joined).splitlines()

                    if len(raw_sent) != len(parsed_sent):
                        sents_counter_failed += 1
                        parsed_sent = ""
                        is_equal_length = False

                if is_equal_length:
                    sents_info_extract(data, coref_spans, only_sent, parsed_sent, sent_id, total_words)
                    total_words += len(raw_sent)
                    sent_id += 1

        data["clusters"] = list(coref_spans)
        if len(data["clusters"]) > 0 or args.with_empty_cluster:
            data_into_jsonlines(data, filename_input, args.dir_output)
            doc_counter_not_failed += 1
        else:
            logger.warning("Doc dont have coref info: " + data["document_id"])
        doc_counter += 1

    str_doc_failed = f"{doc_counter - doc_counter_not_failed}/{doc_counter} ({(doc_counter - doc_counter_not_failed)/doc_counter:.2%})"
    str_sents_failed = f"{sents_counter_failed}/{sents_counter} ({sents_counter_failed/sents_counter:.2%})"
    logger.info("\tDoc failed: " + str_doc_failed)
    logger.info("\tSents failed: " + str_sents_failed + "\n")

def data_into_jsonlines(data, filename_input, dir_output):
    if data["document_id"] == "":
        return
    if not os.path.exists(args.dir_output):
        os.mkdir(args.dir_output)
    with jsonlines.open(args.dir_output + "/" + filename_input + FILE_ENDING_JSONLINES, mode='a') as file_output:
        file_output.write(data) 

def get_parse_sent(raw_sents):
    try:
        dep_parser = CoreNLPDependencyParser(url='http://localhost:9009')
        parsed_sent, = dep_parser.raw_parse(raw_sents)
    except:
        logger.error("CORENLP server not worked")
    return parsed_sent.to_conll(10)

def sents_info_extract(data, coref_spans, sent, parsed_sent, sent_id, total_words):
    for i in range(len(sent)):
        s_splitted = sent[i].split()

        word_id = total_words + int(s_splitted[2])
        word = s_splitted[3]
        coref_info = s_splitted[-1]
        
        data["cased_words"].append(word)
        data["speaker"].append(s_splitted[9])
        data["sent_id"].append(sent_id)

        if coref_info != "-":
            coref_spans.add(coref_info, word_id, " ".join(s_splitted))

        if args.with_parser_values:
            p_splitted = parsed_sent[i].split("\t")
            data["pos"].append(p_splitted[3])
            data["deprel"].append(p_splitted[7])
            head = int(p_splitted[6]) - 1
            head = None if head < 0 else total_words + head 
            data["head"].append(head)      

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir-conll", required=True, help="Path from dir which contain conll files")
    parser.add_argument("--dir-output", required=True, help="Path from dir which save preprocessed files")
    parser.add_argument("--log", default="", help="Path from dir to save log file")
    parser.add_argument("--suffix", default="", help="Preprocess specific data set")
    parser.add_argument('--with-empty-cluster', action="store_true", help="Documents with empty clusters are preprocessed with")
    parser.add_argument("--with-parser-values", action="store_true", help="Parse the sents to get further information. The CORENLP server must be active")
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    # Set up logger file
    if args.log:
        if not os.path.exists(args.log):
            os.mkdir(args.log)
        fh = logging.FileHandler("{0}/{1}.log".format(args.log, "preprocess"))        
        fh.setFormatter(LOG_FORMATTER)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

    logger.info("############ Start preprocessing ############")

    data_files = [f for f in os.listdir(args.dir_conll) if os.path.isfile(args.dir_conll + "/" + f)]
    if args.suffix:
        new_data_files = []
        for i in range(len(data_files)):
            file_suffix = data_files[i].split(".")[2].replace("_gold_conll", "")
            if file_suffix == args.suffix:
                new_data_files.append(data_files[i])
        data_files = new_data_files

    for d in data_files:
        logger.info("File: " + d)
        extract_one_file(d, args.dir_conll, args.dir_output)

    logger.info("############ End preprocessing ############\n\n")


