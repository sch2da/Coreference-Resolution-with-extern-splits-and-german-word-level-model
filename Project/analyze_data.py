import os
import logging
import argparse

import jsonlines

def initialize_info_block():
    info = {
    "name":                              "",
    "count_doc_with_cluster":             0,
    "count_token_with_cluster":           0,
    "count_sent_with_cluster":            0,
    "count_cluster_with_cluster":         0,
    "count_coref_with_cluster":           0,

    "count_doc_without_cluster":          0,
    "count_token_without_cluster":        0,
    "count_sent_without_cluster":         0,

    "count_doc_with_speaker":             0,
    "max_token":                          0,
    "max_token_doc_id":                   ""
    }
    return info

def print_analyze_result(info):
    ROUND_VALUE = 2
    logger.info("dataset: " + info["name"])
    logger.info("number of documents with clusters: " + "{:,}".format(info["count_doc_with_cluster"]))
    logger.info("number of tokens: " + "{:,}".format(info["count_token_with_cluster"]))
    logger.info("number of sents: " + "{:,}".format(info["count_sent_with_cluster"]))
    logger.info("number of clusters: " + "{:,}".format(info["count_cluster_with_cluster"]))
    logger.info("number of coreferences: " + "{:,}".format(info["count_coref_with_cluster"]))
    tokenPdoc = round(info["count_token_with_cluster"]/info["count_doc_with_cluster"], ROUND_VALUE)
    sentPdoc = round(info["count_sent_with_cluster"]/info["count_doc_with_cluster"], ROUND_VALUE)
    clusterPdoc = round(info["count_cluster_with_cluster"]/info["count_doc_with_cluster"], ROUND_VALUE)
    corefPdoc = round(info["count_coref_with_cluster"]/info["count_doc_with_cluster"], ROUND_VALUE)
    tokenPsent = round(info["count_token_with_cluster"]/info["count_doc_with_cluster"], ROUND_VALUE)
    logger.info("token pro document: " + "{:,}".format(tokenPdoc))
    logger.info("sent pro document: " + "{:,}".format(sentPdoc))
    logger.info("cluster pro document: " + "{:,}".format(clusterPdoc))
    logger.info("coref pro document: " + "{:,}".format(corefPdoc))
    logger.info("token pro sent: " + "{:,}".format(tokenPsent))
    logger.info("number of documents without clusters: " +"{:,}".format(info["count_doc_without_cluster"]))
    logger.info("number of tokens: " + "{:,}".format(info["count_token_without_cluster"]))
    logger.info("number of sents: " + "{:,}".format(info["count_sent_without_cluster"]))
    logger.info("number of documents with speaker: " + str(info["count_doc_with_speaker"]))
    logger.info("max token: " + "{:,}".format(info["max_token"]) + " (" + info["max_token_doc_id"] + ")")

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Path from dir which contain jsonlines files to analyze")
    parser.add_argument("--log", default="", help="Path from dir to save log file")
    return parser

logger = logging.getLogger()
logger.setLevel(logging.INFO)
LOG_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s: \t %(message)s', "%Y-%m-%d %H:%M:%S")
# Logger console
sh = logging.StreamHandler()
sh.setFormatter(LOG_FORMATTER)
sh.setLevel(logging.INFO)
logger.addHandler(sh)

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    # Set up logger file
    if args.log:
        if not os.path.exists(args.log):
            os.mkdir(args.log)
        fh = logging.FileHandler("{0}/{1}.log".format(args.log, "analyze_data"))        
        fh.setFormatter(LOG_FORMATTER)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

    logger.info("############ Start analyze data ############") 

    # Count data
    info_list = [] 
    dataset_names = set()
    data_files = [f for f in os.listdir(args.dir) if "_head" not in f]   
    for d in data_files:
        name = d.split(".")[-2].replace("_gold_conll", "")
        dataset_names.add(name)

        info = initialize_info_block()
        with jsonlines.open(args.dir + "/" + d, mode="r") as inf:
            info["name"] = name
            max_token = 0
            max_token_doc = ""
            for doc in inf:
                count_doc = 0
                count_token = 0
                count_sent = 0
                count_cluster = 0
                count_coref = 0
                with_speaker = 0

                count_token = len(doc["cased_words"])
                if doc["sent_id"]:
                    count_sent = int(doc["sent_id"][-1] + 1)
                count_cluster = len(doc["clusters"])
                if max_token < len(doc["cased_words"]):
                    max_token = max(max_token, len(doc["cased_words"]))
                    max_token_doc = doc["document_id"]
                for c in doc["clusters"]:
                    count_coref += len(c)
                speaker = set(doc["speaker"])
                if speaker:
                    val_speaker = speaker.pop()
                    if not (len(speaker) == 0 and val_speaker == "-"):
                        with_speaker = 1

                if count_cluster == 0:
                    info["count_doc_without_cluster"] += 1
                    info["count_token_without_cluster"] += count_token
                    info["count_sent_without_cluster"] += count_sent
                else:
                    info["count_doc_with_cluster"] += 1
                    info["count_token_with_cluster"] += count_token
                    info["count_sent_with_cluster"] += count_sent
                    info["count_cluster_with_cluster"] += count_cluster
                    info["count_coref_with_cluster"] += count_coref
                info["count_doc_with_speaker"] += with_speaker
                info["max_token"] = max_token
                info["max_token_doc_id"] = max_token_doc
            info_list.append(info)

    # Merge info pro dataset
    merged = []
    for dataset in dataset_names:
        info = initialize_info_block()
        for i in info_list:
            if dataset == i["name"]:
                info["name"] = dataset
                info["count_doc_with_cluster"] += i["count_doc_with_cluster"]
                info["count_token_with_cluster"] += i["count_token_with_cluster"]
                info["count_sent_with_cluster"] += i["count_sent_with_cluster"]
                info["count_cluster_with_cluster"] += i["count_cluster_with_cluster"]
                info["count_coref_with_cluster"] += i["count_coref_with_cluster"]

                info["count_doc_without_cluster"] += i["count_doc_without_cluster"]
                info["count_token_without_cluster"] += i["count_token_without_cluster"]
                info["count_sent_without_cluster"] += i["count_sent_without_cluster"]

                info["count_doc_with_speaker"] += i["count_doc_with_speaker"]
                if info["max_token"] < i["max_token"]:
                    info["max_token"] = max(info["max_token"], i["max_token"])
                    info["max_token_doc_id"] = i["max_token_doc_id"]
        merged.append(info)
  
    # Analyze
    for m in merged:
        print_analyze_result(m)
        logger.info("")
        
    logger.info("############ End analyze data ############") 






