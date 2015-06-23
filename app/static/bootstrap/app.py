#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, request
app = Flask(__name__, static_url_path='/bootstrap-3.3.4-dist/')

def read(filename):
    return (l.rstrip() for l in open(filename))
	
with open("car-search.html", "r") as homepage:
	homepageText = homepage.read()
	
@app.route('/')
def root():    
	return homepageText
	#return app.send_static_file('car-search.html')

@app.route('/<make>')
def visit_make(make):
	recognised_makes = [r for r in read("CarMakes.txt")]
	make_data = {'ford': 1,
                 'benz': 2,
                 'audi': 3,
                 'volkswagen': 4}
    # Read CSV
    # Look up make from CSV
	if make.upper() in recognised_makes:
		# return 'I recognise {} '.format(make)
		return 'I recognise you, {}'.format(make)
	else:
		# return 'I do not recognise {}. {} '.format(make)
		return 'I do not recognise you, ' + make
	return 'Error in input!'


if __name__ == '__main__':
    app.run()