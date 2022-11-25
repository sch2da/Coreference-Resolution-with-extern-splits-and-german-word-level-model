import os
import logging
import argparse
from collections import defaultdict

import jsonlines

logger = logging.getLogger()
logger.setLevel(logging.INFO)
LOG_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s: \t %(message)s', "%Y-%m-%d %H:%M:%S")
# Logger console
sh = logging.StreamHandler()
sh.setFormatter(LOG_FORMATTER)
sh.setLevel(logging.INFO)
logger.addHandler(sh)

DOC_PATTERN = END_DOC_TAG = "#end document"

def split_file(file):
    new_file = file.replace("_gold_conll", "_splitted" + str(args.min_doc_length) + "_gold_conll")
    if os.path.exists(args.dir) and os.path.exists(args.dir + "/" + new_file):
        os.remove(args.dir + "/" + new_file)

    with open(args.dir +  "/" + file, mode="r", encoding="utf8") as f_input:
        doc = f_input.read().split(DOC_PATTERN)
        for d in doc:
            prepare_doc(new_file, d)

def prepare_doc(file, doc):
    lines = doc.splitlines()
    length = len(lines)
    amount = int(length / args.min_doc_length)
    if amount > 0:
        splitted_doc = split_doc(lines)
        for s in splitted_doc:
            write_file(file, s)
    else:
        write_file(file, lines)
        

def split_doc(lines):
    begin_tag = ""
    begin_index = 0
    splitted_doc = []
    for i in range(len(lines)):
        if "#begin" in lines[i]:
            begin_tag = lines[i]
            begin_index = i
            break
    lines = lines[begin_index + 1:]
    lines_len = len(lines)

    doc_id = begin_tag.split()[2].replace("(", "").replace(")", "").replace(";", "")
    sent_begin_index = 0
    sent_end_index = args.min_doc_length
    i = 0
    loop = True
    while loop:
        new_doc_id = doc_id + "_splitted_" + str(i)
        i += 1

        try:
            sent_end_index = lines.index("", sent_end_index)
        except:
            sent_end_index = len(lines)
            loop = False
        splitted = get_part_of_doc(lines, (doc_id, new_doc_id), begin_tag, sent_begin_index, sent_end_index)
        splitted_len = len(splitted)
        splitted_doc.append(splitted)

        diff = sent_end_index - sent_begin_index
        sent_begin_index += diff + 1
        sent_end_index += args.min_doc_length

    return splitted_doc

def get_part_of_doc(doc, doc_ids, begin_tag, start, end):
    splitted = []
    # update new id
    for k in range(start, end):
        splitted.append(doc[k].replace(doc_ids[0], doc_ids[1]))
    # add begin
    splitted.insert(0, begin_tag.replace(doc_ids[0], doc_ids[1]))
    #splitted.insert(end + 1, END_DOC_TAG)
    
    return splitted

def write_file(file, new_doc):
    with open(args.dir +  "/" + file, mode="a", encoding="utf8") as f:
        for l in new_doc:
            f.writelines("".join(l) + "\n")
        f.writelines(END_DOC_TAG)
        f.writelines("\n")

def build_parser():
    parser = argparse.ArgumentParser(description='Split docs in conll format in smaller part')
    parser.add_argument("--dir", required=True, help="Path from dir which contain conll files")
    parser.add_argument("--min-doc-length", required=True, type=int, help="Minimum size of a document")
    parser.add_argument("--log", default="", help="Path from dir to save log file")
    parser.add_argument("--suffix", default="", help="Split specific data set")
    return parser
    

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    # Set up logger file
    if args.log:
        if not os.path.exists(args.log):
            os.mkdir(args.log)
        fh = logging.FileHandler("{0}/{1}.log".format(args.log, "split_doc"))        
        fh.setFormatter(LOG_FORMATTER)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

    logger.info("############ Start split document ############")

    data_files = [f for f in os.listdir(args.dir) if "_splitted" not in f]
    if args.suffix:
        new_data_files = []
        for i in range(len(data_files)):
            file_suffix = data_files[i].split(".")[2].replace("_gold_conll", "")
            if file_suffix == args.suffix:
                new_data_files.append(data_files[i])
        data_files = new_data_files


    for f in data_files:
        logger.info("File: " + f)
        split_file(f)

    logger.info("############ End preprocessing ############\n\n")


