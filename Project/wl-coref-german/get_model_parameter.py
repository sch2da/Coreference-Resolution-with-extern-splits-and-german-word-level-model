import os
import argparse

import torch

from coref import CorefModel

def get_size_of_nested_list(list_of_elem):
    ''' Get number of elements in a nested list'''
    count = 0
    for elem in list_of_elem:
        if type(elem) == list:  
            count += get_size_of_nested_list(elem)
        else:
            count += 1    
    return count

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("model", help="Path to model")
    argparser.add_argument("--config-file", default="config.toml")
    args = argparser.parse_args()

    loaded = torch.load(args.model, map_location=torch.device("cpu"))
    NOT_MODEL = ("bert_optimizer", "general_optimizer", "bert_scheduler", "general_scheduler", "epochs_trained")

    loaded_only_model = []
    for key, val in loaded.items():
        if not key in NOT_MODEL:
            loaded_only_model.append((key, val))

    count_list = []
    counter_all = 0
    for l in loaded_only_model:
        for key, val in l[1].items():
            counter = 0
            counter = get_size_of_nested_list(val.tolist())
            counter_all += counter
            count_list.append((key, counter))

    for cl in count_list:
        print(cl)
    print("\ncounter_all: " + str(f"{counter_all:,}"))


