import json
import sys

def compile():
	queue = []
	counter = 0
	LIMIT = 10000
	compiled_file = open('compiled_fanfic.json', 'w+')
	compiled_file.write('[')
	total_len = 0
	while (counter < LIMIT):
		print "File #" + str(counter)
		json_data = open('data/fanfic_data_'+str(counter)+'.json')
		data = json_data.read()
		if len(data) < 100:
			print 'data', data, data == "[]"
		if not data == "[]":
			string = data.replace(']', '').replace('[','')
			compiled_file.write(string)
			if (counter + 1 < LIMIT):
				compiled_file.write(',')
		json_data.close()
		json_data = open('data/fanfic_data_'+str(counter)+'.json')
		json_obj = json.load(json_data)
		if len(json_obj) < 25:
			queue.append(counter)
		total_len += len(json_obj)
		json_data.close()
		counter+=1
	compiled_file.write(']')

	compiled_file.close()

	queueF = open('queue.txt', 'w+')
	queueF.write(repr(queue))
	queueF.close()
	print queue

	compiled_file = open('compiled_fanfic.json')
	final_data = json.load(compiled_file)
	print len(final_data), total_len
