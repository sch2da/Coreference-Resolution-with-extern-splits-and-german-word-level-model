#!/usr/bin/env python3
"""
Convert on the DIRNDL 2015 (prosody) dataset and convert to conll format.
"""
import sys
import os
import argparse

FILENAME = ".german.dirndl_gold_conll"

def extract2conll(line):
    conll_format = ["-"] * 14
    splitted = line.split("\t")
    conll_format[0] = splitted[0] # document id
    conll_format[1] = splitted[1] # part id
    conll_format[2] = splitted[2] # sent id
    conll_format[3] = splitted[3] # word id
    conll_format[4] = splitted[4] # word
    if splitted[-1] == "_":
        conll_format[-1] = "-"
    else:
        conll_format[-1] = splitted[-1] # coref info    
    return "\t".join(conll_format)

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Path from dir which contain DIRNDL 2015 (prosody) dataset to convert")
    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    dirndl_files = [f for f in os.listdir(args.dir) if os.path.isfile(args.dir + "/" + f)]
    for f in dirndl_files:
        with open(args.dir +  "/" + f, mode="r", encoding="utf8") as f_input:
            docs = f_input.read().split("end document")

        category = f.split(".")[-1]
        converted_doc = []
        for d in docs:
            converted_lines = []
            d = d.splitlines()
            length = len(d)
            for i in range(length):
                line = ""
                if d[i].startswith("#begin document") or d[i].startswith("#end document") or d[i].isspace():
                    line = d[i]
                elif d[i].startswith("dlf"):
                    line = extract2conll(d[i])
                converted_lines.append(line + "\n")
            converted_lines.append("#end document")
            converted_doc.append(converted_lines)

        # This document have an error in wl-coref 
        # dlf-nachrichten-200703251000); part 003
        if category == "train":
            converted_doc.pop(48)

        with open(category + FILENAME, mode="w", encoding="utf8") as f_output:
            for conv in converted_doc:
                f_output.writelines(conv)

