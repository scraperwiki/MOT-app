#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, render_template, request, jsonify, redirect
import csv
from collections import namedtuple, OrderedDict
#from app import app
app = Flask(__name__, static_url_path = "/static")

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
    #percentage_dictionary = {}
    
    
    percentage = record.count/sum_of_counts
    percentage = round(100*percentage, 1)

    return percentage


@app.route('/')
def root():
    return app.send_static_file("car-search.html")

@app.route('/', methods=['POST'])
def navigate():
    return redirect("/{}/{}".format(request.form['make'], request.form['model']))


@app.route('/<make>/<model>')
def visit_make(make, model):
    """obtain the values chosen by the user for make and model..."""
    results = sort_by_count(select_make_model(make, model))[:10]
    
    sum_of_counts = get_total_count(results)
    # print(get_total_count())
    results_dictionary = OrderedDict()
    for result in results:
        results_dictionary[result] = get_percentage(result, sum_of_counts)
    return render_template('result.html', results=results_dictionary)


if __name__ == '__main__':
    app.run(debug = True)