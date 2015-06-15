#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/<make>')
def visit_make(make):
    recognised_makes = ['ford', 'benz', 'audi', 'volkswagen']
    if make.lower() in recognised_makes:
        return 'I recognise {} '.format(make)
    else:
        return 'I do not recognise {} '.format(make)
    return 'Error in input!'


if __name__ == '__main__':
    app.run()