#!/usr/bin/env python
# encoding: utf-8

# imports
from flask import Flask, render_template, request, jsonify, redirect
import csv
from collections import namedtuple, OrderedDict
#from app import app
app = Flask(__name__, static_url_path = "/static")

# imports for plots

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

# Level 1 functions

Record = namedtuple("Record", "make model description count")
def make_record(line):
    (make, model, description, count) = line
    return Record(make.strip(), model.strip(), description.strip(), int(count))
    
with open("static/SummedData.csv") as fd:
    records = list(csv.reader(fd))
    records = records[1:]
    records = [make_record(r) for r in records]
    
def select_make_model(make, model):
    return [r for r in records if
        r.make == make and r.model == model]
        
def key(r):
    return r.count

def sort_by_count(r):         
    return sorted(r, key=key, reverse=True)

def get_total_count(selection):
    sum = 0
    for record in selection:
        sum += record.count
    return sum

def get_percentage(record, sum_of_counts):
    
    percentage = record.count/sum_of_counts
    percentage = round(100*percentage, 1)

    return percentage


# Level 2 functions
Bigrecord = namedtuple("Bigrecord", "make model level1 level2 level3 count")
def make_record_level2(line):
    (make, model, level1, level2, level3, count) = line
    return Bigrecord(make, model, level1, level2, level3, int(count))

with open("static/WholeData.csv") as fd1:
    records1 = list(csv.reader(fd1))
    records1 = records1[1:]
    records1 = [make_record_level2(r) for r in records1]

def select_level2(make, model, level1):
    return [r for r in records1 if
        r.make == make and r.model == model and r.level1 == level1]


# app routing

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/', methods=['POST'])
def navigate():
    return redirect("/{}/{}".format(request.form['make'], request.form['model']))


@app.route('/<make>/<model>')
def visit_vehicle_level1(make, model):
    """obtain the values chosen by the user for make and model..."""
    results = sort_by_count(select_make_model(make, model))
        
    sum_of_counts = get_total_count(results)
    
    results_dictionary = OrderedDict()
    for result in results[:10]:
        results_dictionary[result] = get_percentage(result, sum_of_counts)
    return render_template('resultlevel1.html', results=results_dictionary, make=make, model=model, total=sum_of_counts)


@app.route('/<make>/<model>/<level1>')
def visit_vehicle_level2(make, model, level1):
    results = sort_by_count(select_level2(make, model, level1))
    sum_of_counts = get_total_count(results)
    return render_template('resultlevel2.html', results=results, make=make, model=model, level1=level1, total=sum_of_counts)
    people = ('Tom', 'Dick', 'Harry', 'Slim', 'Jim')
    y_pos = np.arange(len(people))
    performance = 3 + 10 * np.random.rand(len(people))
    error = np.random.rand(len(people))

    plt.barh(y_pos, performance, xerr=error, align='center', alpha=0.4)
    plt.yticks(y_pos, people)
    plt.xlabel('Performance')
    plt.title('How fast do you want to go today?')

    plt.show()



if __name__ == '__main__':
    app.run(debug = True)