import json
import re
import csv

import os
print(os.getcwd())

class Task:
    def __init__(self, slot):
        self.slots = [slot,]

    def __str__(self):
        return str(self.slots)

    def addSlot(self, slot):
        self.slots += [slot,]
 
tasks = {}
conv_ids = []
with open("..\\TaskmasterToRasa\\resources\\TM-1-2019\\train-dev-test\\dev.csv") as conv_id_file:
    reader = csv.reader(conv_id_file)
    while True:
        try:
            conv_ids += [next(reader)[0]]
        except StopIteration:
            break
    
# Get all dialogues
dialogues = {}
with open("..\\TaskmasterToRasa\\resources\\TM-1-2019\\woz-dialogs.json") as f:
    dialogues = list(filter(lambda x: re.search(r"restaurant-table-1", x["instruction_id"]) != None and x["conversation_id"] in conv_ids, json.load(f)))
    # with open("..\\TaskmasterToRasa\\resources\\restaurant-woz-dialogues.json", "w") as j:
    #     json.dump(dialogues, j)


nlu = []
for dialogue in dialogues:
    found = False
    for utter in dialogue["utterances"]:
        find_restaurant = ""
        if utter["speaker"] == "ASSISTANT":
            continue
        
        utter_to_add = utter["text"]
        if "segments" in utter.keys():
            for s in utter["segments"]:
                annotation = s["annotations"][0]["name"].split(".")
                if "location" in annotation:
                    found = True
                replaceable = "[{}]({})".format(s["text"], "-".join(annotation[1:2]))
                utter_to_add = re.sub(s["text"], replaceable, utter_to_add, flags=re.IGNORECASE)

        find_restaurant += utter_to_add

        if found:
            nlu += [find_restaurant]
            break

with open("..\\TaskmasterToRasa\\Model\\data\\nlu.yml", "w") as f:
    nlu_string = '''version: 2.0

nlu:
- intent: find_restaurant
  examples: |
'''
    for utterance in nlu:
        nlu_string += "    - {}\n".format(utterance)
    f.write(nlu_string)