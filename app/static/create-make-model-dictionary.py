#!/usr/bin/env python
import json

# function to handle file reading
def read(filename):
    return (l.split(",") for l in open(filename) if l.strip())

# create an empty dictionary
make_model_dictionary = {}

for line in read("WholeData.csv"):
	model_set = set()
	make = line[0].strip()[1:-1]
	model = line[1].strip()[1:-1]
	if make in make_model_dictionary:
		make_model_dictionary[make].add(model)
	else:
		model_set.add(model)
		make_model_dictionary[make] = model_set

for key in make_model_dictionary.keys():
	make_model_dictionary[key]=list(make_model_dictionary[key])
#print(json.dumps(make_model_dictionary))
#exit()


#print(make_model_dictionary)
# print out the dictionary into a separate text file
with open("MakesAndModels.json", "w") as text_file:
	json.dump(make_model_dictionary, text_file, indent=2)	