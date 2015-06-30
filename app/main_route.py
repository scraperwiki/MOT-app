#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, render_template, request, jsonify, redirect
#from app import app
app = Flask(__name__, static_url_path = "/static")

@app.route('/')
def root():
    return app.send_static_file("car-search.html")

@app.route('/', methods=['POST'])
def navigate():
    return redirect("/{}/{}".format(request.form['make'], request.form['model']))


@app.route('/<make>/<model>')
def visit_make(make, model):
    """obtain the values chosen by the user for make and model..."""
    
    return jsonify(result=make + model)    


if __name__ == '__main__':
    app.run(debug = True)