from collections import defaultdict
import logging
import os
import argparse
from typing import Tuple

import jsonlines

logger = logging.getLogger()
logger.setLevel(logging.INFO)
LOG_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s: \t %(message)s', "%Y-%m-%d %H:%M:%S")
# Logger console
sh = logging.StreamHandler()
sh.setFormatter(LOG_FORMATTER)
sh.setLevel(logging.INFO)
logger.addHandler(sh)

FILE_ENDING_JSONLINES = ".jsonlines"

def get_head(mention: Tuple[int, int], doc: dict) -> int:
    """Returns the span's head, which is defined as the only word within the
    span whose head is outside of the span or None. In case there are no or
    several such words, the rightmost word is returned

    Args:
        mention (Tuple[int, int]): start and end (exclusive) of a span
        doc (dict): the document data

    Returns:
        int: word id of the spans' head
    """
    head_candidates = set()
    start, end = mention
    for i in range(start, end):
        ith_head = doc["head"][i]
        if ith_head is None or not (start <= ith_head < end):
            head_candidates.add(i)
    if len(head_candidates) == 1:
        return head_candidates.pop()
    return end - 1

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Path from dir which contain jsonlines files to convert")
    parser.add_argument("--log", default="", help="Path from dir to save log file")
    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    # Set up logger file
    if args.log:
        if not os.path.exists(args.log):
            os.mkdir(args.log)
        fh = logging.FileHandler("{0}/{1}.log".format(args.log, "convert_to_heads"))        
        fh.setFormatter(LOG_FORMATTER)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

    logger.info("############ Start convert to heads ############")

    data_files = [f for f in os.listdir(args.dir) if "_head" in f]
    for d in data_files:
        os.remove(args.dir + "/" + d)

    data_files = [f for f in os.listdir(args.dir) if "_head" not in f]   
    for d in data_files:

        with jsonlines.open(args.dir + "/" + d, mode="r") as inf:
            with jsonlines.open(args.dir + "/" + d.replace(FILE_ENDING_JSONLINES, "_head" + FILE_ENDING_JSONLINES), mode="w") as outf:
                deleted_spans = 0
                deleted_clusters = 0
                total_spans = 0
                total_clusters = 0

                for doc in inf:
                    total_spans += sum(len(cluster) for cluster in doc["clusters"])
                    total_clusters += len(doc["clusters"])

                    head_clusters = [
                        [get_head(mention, doc) for mention in cluster]
                        for cluster in doc["clusters"]
                    ]

                    # check for duplicates
                    head2spans = defaultdict(list)
                    for cluster, head_cluster in zip(doc["clusters"], head_clusters):
                        for span, span_head in zip(cluster, head_cluster):
                            head2spans[span_head].append((span, head_cluster))

                    doc["head2span"] = []

                    for head, spans in head2spans.items():
                        spans.sort(key=lambda x: x[0][1] - x[0][0])  # shortest spans first
                        doc["head2span"].append((head, *spans[0][0]))

                        if len(spans) > 1:
                            logging.debug(f'FILENAME {doc["document_id"]} {doc["cased_words"][head]}')
                            for span, cluster in spans:
                                logging.debug(f'{id(cluster)} {" ".join(doc["cased_words"][slice(*span)])}')
                            logging.debug("=====")

                            for _, cluster in spans[1:]:
                                cluster.remove(head)
                                deleted_spans += 1

                    filtered_head_clusters = [cluster for cluster in head_clusters if len(cluster) > 1]
                    deleted_clusters += len(head_clusters) - len(filtered_head_clusters)
                    doc["word_clusters"] = filtered_head_clusters
                    doc["span_clusters"] = doc["clusters"]
                    del doc["clusters"]

                    outf.write(doc)

                logger.info("Deleted in : " + d)
                logger.info(f"\t{deleted_spans}/{total_spans} ({deleted_spans/total_spans:.2%}) spans")
                logger.info(f"\t{deleted_clusters}/{total_clusters} ({deleted_clusters/total_clusters:.2%}) clusters \n")

    logger.info("############ Finish! ############\n\n")
