import json
import re
import csv
import requests

import os

from requests.api import request
print(os.getcwd())

class Task:
    def __init__(self, slot):
        self.slots = [slot,]

    def __str__(self):
        return str(self.slots)

    def addSlot(self, slot):
        self.slots += [slot,]

nlu = {}

def AddToNLU(key, value):
    if value != "" and value != " (deleted)":
        if key in nlu.keys():
            nlu[key] += [value,]
        else:
            nlu[key] = [value,]

def setAnnotations(utterance, segments=None):
    if segments != None:
        for s in segments:
            annotation = s["annotations"][0]["name"].split(".")
            replaceable = "[{}]({})".format(s["text"], "-".join(annotation[1:2]))
            utterance = re.sub(s["text"], replaceable, utterance, flags=re.IGNORECASE)
    return utterance

tasks = {}
conv_ids = []
with open("..\\TaskmasterToRasa\\resources\\TM-1-2019\\train-dev-test\\test.csv") as conv_id_file:
    reader = csv.reader(conv_id_file)
    while True:
        try:
            conv_ids += [str(next(reader)[0]),]
        except StopIteration:
            break

## Self Dialogues
# dialogues = {}
# with open("..\\TaskmasterToRasa\\resources\\TM-1-2019\\self-dialogs.json") as f:
#     dialogues = list(filter(lambda x: re.search(r"restaurant-table-1", x["instruction_id"]) != None, json.load(f)))

# WOZ Dialogues
dialogues = {}
with open("..\\TaskmasterToRasa\\resources\\TM-1-2019\\woz-dialogs.json") as f:
    dialogues = list(filter(lambda x: re.search(r"restaurant-table-1", x["instruction_id"]) != None, json.load(f)))

for dialogue in dialogues:
    # Control variables for the dialogue state
    found_location = False
    first_restaurant = False
    u = 0

    inform_utter = ""

    utterances = dialogue["utterances"]
    while u < len(utterances):
        find_restaurant = ""
        if not found_location:
            # Deals with the first part of the dialogue. To this intent, all the user utterances until the
            # appearance of a location are considered as a unique sentence that leads to the find_restaurant intent
            if utterances[u]["speaker"] == "ASSISTANT":
                u += 1
                continue
            
            utter_segments = utterances[u]["segments"] if "segments" in utterances[u].keys() else None
            utter_to_add = setAnnotations(utterances[u]["text"], utter_segments)

            if re.search(r"\(location\)", utter_to_add, re.IGNORECASE) != None:
                found_location = True                

            find_restaurant += utter_to_add

            if found_location:
                u += 1
                while u < len(utterances) and utterances[u]["speaker"] != "ASSISTANT":
                    utter_segments = utterances[u]["segments"] if "segments" in utterances[u].keys() else None
                    utter_to_add = setAnnotations(utterances[u]["text"], utter_segments)
                    find_restaurant += utter_to_add
                    u += 1
                    
                AddToNLU("find_restaurant", find_restaurant)
                continue
        elif not first_restaurant:
            
            if utterances[u]["speaker"] == "ASSISTANT":
                AddToNLU("inform", inform_utter)
                inform_utter = ""

                assistant_segments = utterances[u]["segments"] if "segments" in utterances[u].keys() else []
                assistant_segments = list(filter(lambda x: re.search(r"name", x["annotations"][0]["name"], re.IGNORECASE) != None, assistant_segments))
                if assistant_segments != []:
                    first_restaurant = True
            else:
                utter_segments = utterances[u]["segments"] if "segments" in utterances[u].keys() else []
                inform_utter += " " + setAnnotations(utterances[u]["text"], utter_segments)
                
        u += 1


# Uncomment the next lines to get multiwoz restaurant domain evaluation
# REQUIRES RESTAURANT MODEL RUNING
d = dialogues[1]
for u in d["utterances"]:
    if u["speaker"] == "ASSISTANT":
        continue
    else:
        res = requests.post("http://localhost:5005/model/parse", json={"text": u["text"]})
        print(res.text, "\n")


with open("..\\TaskmasterToRasa\\Model\\data\\nlu.yml", "w") as f:
    nlu_string = '''version: 2.0

nlu:
'''
    for intent in nlu.keys():
        nlu_string += '''  - intent: {}
  examples: |
'''.format(intent)
        for example in nlu[intent]:
            nlu_string += "    - {}\n".format(example)
    f.write(nlu_string)

