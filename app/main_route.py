#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from app import app
#app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/<make>')
def visit_make(make):
    recognised_makes = ['ford', 'benz', 'audi', 'volkswagen']
    make_data = {'ford': 1,
                 'benz': 2,
                 'audi': 3,
                 'volkswagen': 4}
    # Read CSV
    # Look up make from CSV
    if make.lower() in recognised_makes:
        return 'I recognise {}. {} '.format(make_data[make.lower()], make)
    else:
        return 'I do not recognise {}. {} '.format(make)
    return 'Error in input!'


if __name__ == '__main__':
    app.run()