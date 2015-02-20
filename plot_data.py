import plotly.plotly as py
from plotly.graph_objs import *
import generate_data
import datetime

def plot(data):
	return

def test_plot():
	test_data = generate_data.test_generation()
	print test_data
	d = []
	for c in test_data.keys():
		ys = [entry[1] for entry in test_data[c]]
		xs = [datetime.datetime.fromtimestamp(entry[0]).strftime("%m/%d") for entry in test_data[c]] 
		print xs, ys
		trace = Scatter(x=xs,y=ys,name=c,line=Line(shape='spline'))
		d.append(trace)
	data = Data(d)
	plot_url = py.plot(data, filename='test')	
