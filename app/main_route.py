#!/usr/bin/env python3
# encoding: utf-8

######################### imports #############################################
from __future__ import division
from flask import Flask, render_template, request, jsonify, redirect
import csv
import json
from collections import namedtuple, OrderedDict
import operator
import utilities
import copy
import os

DATA_DIR = "/dockermount"
FAULTS = os.path.join(DATA_DIR, "WholeDataFaults.txt")
RATES = os.path.join(DATA_DIR, "WholeDataRates.csv")

# global variables
app = Flask(__name__, static_url_path = "/static")
data_dict = {}
data_dict_rates = {}

############# functions to create the main dictionaries ##########################
def parse_file():
    data_dict_builder = {}
    global data_dict
    Bigrecord = namedtuple("Bigrecord",
        "make model year level1 level2 level3 modelcount")
    def make_record_level2(line):
        (make, model, year,
            level1, level2, level3, modelcount) = line
        return Bigrecord(make, model, year, level1, level2, level3,
         int(modelcount))

    with open(FAULTS) as fd:
        lines = csv.reader(fd, delimiter = '|')
        for l in lines:
            big = make_record_level2(l)

            data_dict_builder.setdefault(big.make, {}).setdefault(big.model,
                {}).setdefault(big.year, {}).setdefault(big.level1,
                []).append((big.level2, big.level3, big.modelcount))

    data_dict = data_dict_builder

def parse_file_rates():
    data_dict_builder = {}
    global data_dict_rates
    Bigrecord = namedtuple("Bigrecord",
        "make model year testresult modelcount")
    def make_record(line):
        (make, model, year, testresult, modelcount) = line
        return Bigrecord(make, model, year, testresult, int(modelcount))

    with open(RATES) as fd:
        lines = csv.reader(fd)
        for l in lines:
            big = make_record(l)
            data_dict_builder.setdefault(big.make, {}).setdefault(big.model,
                {}).setdefault(big.year, {})[big.testresult] = big.modelcount


    data_dict_rates = data_dict_builder


######################### utility functions ###################################

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

def create_pass_by_volume():
    top_list = []
    i = 0
    data_dict_rates_copy1 = copy.deepcopy(data_dict_rates)

    while i < 11:
        highest_count = 0
        top_make = ''
        top_model = ''
        total_count = 0
        for make, model_years in data_dict_rates_copy1.items():
                for model, years_passfail in model_years.items():
                    for year, passfail in years_passfail.items():
                        total_count = passfail.get('P', 0) + passfail.get('F', 0)
                        #print('total_count = '+repr(total_count))
                        if total_count > highest_count:
                            top_make = make
                            top_model = model
                            highest_count = total_count                       
        top_list.append((top_make, top_model))
        data_dict_rates_copy1[top_make].pop(top_model)
        i = i + 1
    return top_list

def create_pass_by_yearvolume(given_year):
    top_list = []
    i = 0
    data_dict_rates_copy = copy.deepcopy(data_dict_rates)

    while i < 11:
        highest_count = 0
        top_make = ''
        top_model = ''
        for make, model_years in data_dict_rates_copy.items():
                for model, years_passfail in model_years.items():
                    for year, passfail in years_passfail.items():
                        if year == given_year:
                            total_count = passfail.get('P', 0) + passfail.get('F', 0)
                            if total_count > highest_count:
                                top_make = make
                                top_model = model
                                highest_count = total_count
                        
        top_list.append((top_make, top_model))
        data_dict_rates_copy[top_make].pop(top_model)
        i = i + 1
    return top_list

######################### pass rate functions ##################################
def select_make_model_rate(make, model, year=None):
    if year is None:
        return data_dict_rates[make][model]
    else:
        return data_dict_rates[make][model][year]

def calculate_pass_rate_year(dictionary):

    passes, fails = dictionary.get("P", 0), dictionary.get("F", 0)
    total = passes + fails
    rate = round((100*passes / total), 1)
    return (passes, fails, rate)

def calculate_pass_rate_all(dictionary):
    passfail_counts = {"P": 0, "F": 0}

    for year, passfail in dictionary.items():
        passfail_counts["P"] += passfail.get("P", 0)
        passfail_counts["F"] += passfail.get("F", 0)

    passes, fails = passfail_counts["P"], passfail_counts["F"]
    total = passes + fails
    rate = round((100*passes / total), 1)

    return (passes, fails, rate)

######################### level 1 functions ##################################
def select_make_model(make, model, year=None):
    if year is None:
        return data_dict[make][model]
    else:
        return data_dict[make][model].get(year, {})


def extract_level1(dictionary):
    level1_dictionary = {}
    for year, levels in dictionary.items():
        for level1, bigrecords in levels.items():
        	running_total = level1_dictionary.get(level1, 0)
        	failure_count = sum(bigrecord[-1] for bigrecord in bigrecords)
        	level1_dictionary[level1] = running_total + failure_count

    return level1_dictionary


def extract_level1_year(dictionary):
    level1_dictionary = {}
    for level1, bigrecords in dictionary.items():
       	running_total = level1_dictionary.get(level1, 0)
       	failure_count = sum(bigrecord[-1] for bigrecord in bigrecords)
       	level1_dictionary[level1] = running_total + failure_count

    return level1_dictionary


def analyse_level1(dictionary):
    tuple_list = []
    for level1, count in dictionary.items():
    	tuple_list.append((level1, count))

    return tuple_list

######################## level 2 functions ####################################
def select_level2(make, model, level1, year=None):
    if year is None:
        d = data_dict[make][model]
        return analyse_level2(level1, d)
    else:
        return data_dict[make][model][year][level1]

def analyse_level2(mylevel1, dictionary):
    level2_dict = {}
    for year, levels in dictionary.items():
        for level1, bigrecords in levels.items():
            if level1 == mylevel1:
                for bigrecord in bigrecords:
                    desc = bigrecord[0] + ': ' + bigrecord[1]
                    running_total = level2_dict.get(desc, 0)
                    level2_dict[desc] = running_total + bigrecord[-1]
    return level2_dict

################### computational app routing #################################
@app.route('/model', methods=['GET', 'POST'])
def getModel():
    make = request.json['make']
    models = list(data_dict_rates[make].keys())
    models = json.dumps(models)
    return models

@app.route('/year', methods=['GET', 'POST'])
def getYear():
    make = request.json['make']
    model = request.json['model']
    years = list(data_dict_rates[make][model].keys())
    years = json.dumps(years)
    return years

##################### navigational app routing ################################

@app.route('/')
def index():
    makes = list(data_dict_rates.keys())
    return render_template("index.html", make=makes)


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/', methods=['POST'])
def navigate():
    selected_make = request.form['make']
    if selected_make == 'make':
        error = 'You did not select any car make. Please select a car make to proceed.'
        return render_template("error.html", error=error)
    else:
        selected_model = request.form['model']
        if selected_model == 'model':
            error = 'You did not select any car model. Please select a car model to proceed.'
            return render_template("error.html", error=error)
        if request.form['year']=='choose year':
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

######################### pass navigations ##################################

@app.route('/PASS/<make>/<model>')
def pass_vehicle_allyears(make, model):
    passes, fails, rate = calculate_pass_rate_all(
        select_make_model_rate(make, model))

    top_list = create_pass_by_volume()
    top_dict = {}
    for (carmake, carmodel) in top_list:
        my_tuple = calculate_pass_rate_all(select_make_model_rate(carmake, 
            carmodel))
        top_dict[(carmake, carmodel)] = my_tuple
    top_dict_sorted = OrderedDict(sorted(top_dict.items(), key= lambda x: x[1][2],reverse=True))
    return render_template("passrate.html", make=make, model=model,
        count_fail=fails, count_pass=passes, rate=rate, results=top_dict_sorted)

@app.route('/PASS/<make>/<model>/<year>')
def pass_vehicle_byyear(make, model, year):
    passes, fails, rate = calculate_pass_rate_year(
        select_make_model_rate(make, model, year))

    top_list = create_pass_by_yearvolume(year)
    top_dict = {}
    for (carmake, carmodel) in top_list:
        my_tuple = calculate_pass_rate_year(select_make_model_rate(carmake, 
            carmodel, year))
        top_dict[(carmake, carmodel)] = my_tuple
    top_dict_sorted = OrderedDict(sorted(top_dict.items(), key= lambda x: x[1][2],reverse=True))
    return render_template("passrateyear.html", make=make, model=model,
        year=year, count_fail=fails, count_pass=passes, rate=rate, results=top_dict_sorted)

######################### faults navigations #############################
############################### level 1 ##################################

@app.route('/FAULTS/<make>/<model>')
def visit_vehicle_level1(make, model):
    """obtain the values chosen by the user for make and model..."""
    if make in data_dict and model in data_dict[make]:
        level1 = extract_level1(select_make_model(make, model))
        #print(level1)
        level1_tuples = analyse_level1(level1)
        results_dictionary, sum_of_counts = utilities.create_results_dictionary(level1_tuples)
        #fig = utilities.results_graph(results_dictionary)
        return render_template('resultlevel1.html', results=results_dictionary,
            make=make, model=model, total=sum_of_counts)
    else:
        error = 'There are no failures for ' + make + ' ' + model + ' in the data set'
        return render_template("error.html", error=error)

@app.route('/<year>/FAULTS/<make>/<model>')
def visit_vehicle_level1_byyear(make, model, year):
    """obtain the values chosen by the user for make and model..."""
    if make in data_dict and model in data_dict[make] and year in data_dict[make][model]:
        level1 = extract_level1_year(select_make_model(make, model, year))
        #print(level1)
        level1_tuples = analyse_level1(level1)
        #print(level1_tuples)
        results_dictionary, sum_of_counts = utilities.create_results_dictionary(level1_tuples)
        #fig = utilities.results_graph(results_dictionary)

        return render_template('resultlevel1_year.html', results=results_dictionary,
            make=make, model=model, year=year, total=sum_of_counts)
    else:
        error = 'There are no failures for ' + make + ' ' + model + ' ' + year +' model in the data set'
        return render_template("error.html", error=error)

############################### level 2 ##################################
@app.route('/FAULTS/<make>/<model>/<level1>')
def visit_vehicle_level2(make, model, level1):
    level2_tuples = analyse_level1(select_level2(make, model, level1))

    results_dictionary, sum_of_counts = utilities.create_results_dictionary(level2_tuples)

    #fig = utilities.results_graph(results_dictionary)
    return render_template('resultlevel2.html', results=results_dictionary,
        make=make, model=model, total=sum_of_counts, level1=level1)

@app.route('/<year>/FAULTS/<make>/<model>/<level1>')
def visit_vehicle_level2_byyear(make, model, level1, year):
    level2_tuples = select_level2(make, model, level1, year)

    results_dictionary, sum_of_counts = utilities.create_results_dictionary(level2_tuples)

    #fig = utilities.results_graph(results_dictionary)

    return render_template('resultlevel2_year.html', results=results_dictionary,
        make=make, model=model, year=year, total=sum_of_counts, level1=level1)

########################### run the app #######################################
parse_file()
parse_file_rates()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
