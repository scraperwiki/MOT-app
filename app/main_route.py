#!/usr/bin/env python
# encoding: utf-8

# imports
from flask import Flask, render_template, request, jsonify, redirect
import csv
import json
from collections import namedtuple, OrderedDict
import operator

# imports for plots
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl
from mpld3 import fig_to_html

# global variables
app = Flask(__name__, static_url_path = "/static")
data_dict = {}

####### function to create the main dictionary ################################
def parse_file():
    data_dict_builder = {}
    global data_dict
    Bigrecord = namedtuple("Bigrecord", 
        "make model year testresult level1 level2 level3 modelcount")
    def make_record_level2(line):
        (make, model, year, testresult, 
            level1, level2, level3, modelcount) = line
        return Bigrecord(make, model, year, testresult, level1, level2, level3,
         int(modelcount))

    with open("static/WholeData.csv") as fd:
        records = list(csv.reader(fd))
        records = records[1:]
        records = [make_record_level2(r) for r in records]

    for r in records:
        data_dict_builder.setdefault(r.make, {}).setdefault(r.model, 
            {}).setdefault(r.year, {}).setdefault(r.testresult, 
            {}).setdefault(r.level1, []).append((r.level2, r.level3, r.modelcount))
        
        # makes = data_dict_builder.setdefault(r.make, {})
        # models = makes.setdefault(r.model, {})
        # years = models.setdefault(r.year, {})
        # testresults = years.setdefault(r.testresult, {})
        # level1 = years.setdefault(r.level1, [])        
        # level1.append((r.level2, r.level3, r.modelcount))

    data_dict = data_dict_builder

    return data_dict_builder

######################### utility functions ###################################

def key(r):
    return r[-1]

def sort_by_count(r):         
    return sorted(r, key=key, reverse=True)

def get_total_count(dictionary_list):
    sum = 0
    for dictionary in dictionary_list:
        for level1, list_of_tuples in dictionary.items():
            for eachtuple in list_of_tuples:
                sum += eachtuple[-1]
    return sum

def get_total_count_tuple(tuple_list):
    sum = 0
    for eachtuple in tuple_list:
        sum += eachtuple[-1]
    return sum

def get_percentage(record, sum_of_counts):
    
    percentage = record[-1]/sum_of_counts
    percentage = round(100*percentage, 1)

    return percentage

# check the counts for the different makes in the data
def create_make_count():
    make_dict = {}
    #sum = 0
    for record in records:
        if record.make in make_dict:
            make_dict[record.make] += 1
        else:
            make_dict[record.make] = 1

    sorted_x = sorted(make_dict.items(), key=operator.itemgetter(1))
    print(sorted_x)
    return make_dict

######################### level 1 functions ##################################
def select_make_model(make, model, year=None):
    if year is None:
        return data_dict[make][model]
    else:
        return data_dict[make][model][year]


def calculate_pass_rate_all(dictionary):    
    passfail_counts = {"P": 0, "F": 0}
    for year, passfail_levels in dictionary.items():
        for passfail, levels in passfail_levels.items():
            for level1, bigrecords in levels.items():
                for bigrecord in bigrecords:
                    if passfail not in passfail_counts:
                       passfail_counts[passfail] = 0
                    passfail_counts[passfail] += bigrecord[-1]
    
    passes, fails = passfail_counts["P"], passfail_counts["F"]
    total = passes + fails
    rate = round((100*passes / total), 1)
    return (passes, fails, rate)

def calculate_pass_rate_year(dictionary):
    passfail_counts = {"P": 0, "F": 0}
    for passfail, levels in dictionary.items():
        for level1, bigrecords in levels.items():
            for bigrecord in bigrecords:
                if passfail not in passfail_counts:
                    passfail_counts[passfail] = 0
                passfail_counts[passfail] += bigrecord[-1]
    
    passes, fails = passfail_counts["P"], passfail_counts["F"]
    total = passes + fails
    rate = round((100*passes / total), 1)
    return (passes, fails, rate)

def extract_level1(dictionary):
    level1_dictionary_list = []
    for year, passfail_levels in dictionary.items():
        for passfail, levels in passfail_levels.items():
            if passfail == "F":
                level1_dictionary_list.append(levels)


    # for i, dicto in enumerate(level1_dictionary_list):
    #     print(dicto.keys())
    return level1_dictionary_list

def extract_level1_year(dictionary):
    level1_dictionary_list = []
    for passfail, levels in dictionary.items():
        if passfail == "F":
            level1_dictionary_list.append(levels)


    # for i, dicto in enumerate(level1_dictionary_list):
    #     print(dicto.keys())
    return level1_dictionary_list

def analyse_level1(dictionary_list):
    tuple_list = []
    for dictionary in dictionary_list:        
        for level1, list_of_tuples in dictionary.items():
            sum_of_counts = 0
            for eachtuple in list_of_tuples:
                sum_of_counts += eachtuple[-1]
            tuple_list.append((level1, sum_of_counts))

    return tuple_list

######################## level 2 functions ####################################
def select_level2(make, model, level1, year=None):
    if year is None:
        d = data_dict[make][model]
        return analyse_level2(level1, d)
    else:
        return data_dict[make][model][year]["F"][level1]

def analyse_level2(mylevel1, dictionary):
    tuple_list = []
    for year, passfail_levels in dictionary.items():
        for passfail, levels in passfail_levels.items():
            if passfail == "F":
                for level1, bigrecords in levels.items():
                    if level1 == mylevel1:
                        for bigrecord in bigrecords:
                            tuple_list.append(bigrecord)
    
    
    return tuple_list

################################# graphing ####################################
def create_graph(x, y):
    x.reverse()
    y.reverse()
    fig = plt.figure()

    width = .75
    ind = np.arange(len(x))
    plt.barh(ind, x)
    plt.yticks(ind + width / 2, y)
    fig.tight_layout()

    figure_html=fig_to_html(fig)
    return figure_html


################### computational app routing #################################
@app.route('/make', methods=['GET', 'POST'])
def getModel(): 
    make = request.json['make']
    models = list(data_dict[make].keys()) 
    models = json.dumps(models)  
    return models

@app.route('/make/model', methods=['GET', 'POST'])
def getYear(): 
    make = request.json['make']
    model = request.json['model']
    years = list(data_dict[make][model].keys()) 
    years = json.dumps(years)  
    return years

##################### navigational app routing ################################

@app.route('/')
def index():
    makes = list(data_dict.keys())    
    return render_template("index.html", make=makes)

@app.route('/', methods=['POST'])
def navigate():
    if request.form['year']=='Select a year':
        if request.form['submit-button']=='Display Top Faults':
            return redirect("/FAULTS/{}/{}".format(request.form['make'], 
                request.form['model']))
        else:
            return redirect("/PASS/{}/{}".format(request.form['make'], 
                request.form['model']))

    else:
        if request.form['submit-button']=='Display Top Faults':
            return redirect("/{}/FAULTS/{}/{}".format(request.form['year'],
                request.form['make'], request.form['model']))
        else:
            return redirect("/PASS/{}/{}/{}".format(request.form['make'], 
                request.form['model'], request.form['year']))

@app.route('/PASS/<make>/<model>')
def pass_vehicle_allyears(make, model):    
    passes, fails, rate = calculate_pass_rate_all(
        select_make_model(make, model))     
    return render_template("passrate.html", make=make, model=model, 
        count_fail=fails, count_pass=passes, rate=rate)

@app.route('/PASS/<make>/<model>/<year>')
def pass_vehicle_byyear(make, model, year):    
    passes, fails, rate = calculate_pass_rate_year(
        select_make_model(make, model, year))
    return render_template("passrateyear.html", make=make, model=model, 
        year=year, count_fail=fails, count_pass=passes, rate=rate)


@app.route('/FAULTS/<make>/<model>')
def visit_vehicle_level1(make, model):
    """obtain the values chosen by the user for make and model..."""
    level1 = extract_level1(select_make_model(make, model))
    level1_tuples = analyse_level1(level1)
    sorted_tuples = sort_by_count(level1_tuples)
    sum_of_counts = get_total_count(level1)
    
    # create dictionary to hold percentages
    results_dictionary = OrderedDict()
    for result in sorted_tuples[:10]:
        results_dictionary[result] = get_percentage(result, sum_of_counts)

    # array of descriptions
    y = [r[0] for r in sorted_tuples[:10]]

    # array of counts
    x = [results_dictionary[r] for r in sorted_tuples[:10]]    

    fig = create_graph(x, y)        
    
    return render_template('resultlevel1.html', results=results_dictionary, 
        make=make, model=model, total=sum_of_counts, fig=fig)

@app.route('/<year>/FAULTS/<make>/<model>')
def visit_vehicle_level1_byyear(make, model, year):
    """obtain the values chosen by the user for make and model..."""
    level1 = extract_level1_year(select_make_model(make, model, year))
    level1_tuples = analyse_level1(level1)
    sorted_tuples = sort_by_count(level1_tuples)
    sum_of_counts = get_total_count(level1)
    
    # create dictionary to hold percentages
    results_dictionary = OrderedDict()
    for result in sorted_tuples[:10]:
        results_dictionary[result] = get_percentage(result, sum_of_counts)

    # array of descriptions
    y = [r[0] for r in sorted_tuples[:10]]
    # array of counts
    x = [results_dictionary[r] for r in sorted_tuples[:10]]    

    fig = create_graph(x, y)        
    
    return render_template('resultlevel1_year.html', results=results_dictionary, 
        make=make, model=model, year=year, total=sum_of_counts, fig=fig)

@app.route('/FAULTS/<make>/<model>/<level1>')
def visit_vehicle_level2(make, model, level1):
    level2_tuples = select_level2(make, model, level1)
    #print("level 2: "+repr(level2_tuples))    
    sorted_tuples = sort_by_count(level2_tuples)
    sum_of_counts = get_total_count_tuple(level2_tuples)
    return render_template('resultlevel2.html', results=sorted_tuples, 
        make=make, model=model, level1=level1, total=sum_of_counts)

@app.route('/<year>/FAULTS/<make>/<model>/<level1>')
def visit_vehicle_level2_byyear(make, model, level1, year):
    level2_tuples = select_level2(make, model, level1, year)
    sorted_tuples = sort_by_count(level2_tuples)
    sum_of_counts = get_total_count_tuple(level2_tuples)
    return render_template('resultlevel2_year.html', results=sorted_tuples, 
        make=make, model=model, level1=level1, year=year, total=sum_of_counts)

########################### run the app #######################################
if __name__ == '__main__':
    parse_file()    
    app.run(debug = True)