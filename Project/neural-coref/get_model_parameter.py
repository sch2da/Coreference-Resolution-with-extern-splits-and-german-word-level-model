import os
import argparse

import torch

from model import CorefModel, IncrementalCorefModel
import util

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
    argparser.add_argument("--device")
    args = argparser.parse_args()

    device = torch.device('cpu' if args.device is None else f'cuda:{args.device}')
    model_path = os.path.normpath(args.model)
    model = model_path.split(os.sep)[-1].replace("model_" ,"")
    splitted = model.split("_")[0:-3]
    config_name = "_".join(splitted)

    config = util.initialize_config(config_name, create_dirs=False)

    if model.startswith("c2f"):
        model = CorefModel(config, device)
    elif model.startswith("increm"):
        model = IncrementalCorefModel(config, device)

    loaded = torch.load(args.model, map_location=device)

    count_list = []
    counter_all = 0
    for key, val in loaded.items():
        counter = 0
        counter = get_size_of_nested_list(val.tolist())
        counter_all += counter
        count_list.append((key, counter))

    for cl in count_list:
        print(cl)
    print("\ncounter_all: " + str(f"{counter_all:,}"))


    total_params = sum(	param.numel() for param in model.parameters() )
    print("The model has a parameter weight of " + str(f"{total_params:,}"))
    print("Difference: " + str(int(counter_all - total_params)))

