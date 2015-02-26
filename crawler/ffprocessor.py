import json

counter = 0
LIMIT = 10
compiled_file = open('compiled_fanfic.json', 'w+')
compiled_file.write('[')
total_len = 0
while (counter < LIMIT):
	json_data = open('/Users/carolyn/Downloads/final_fanfic_data_'+str(counter)+'.json')
	data = json_data.read()
	compiled_file.write(data.replace(']', '').replace('[',''))
	json_data.close()
	json_data = open('/Users/carolyn/Downloads/final_fanfic_data_'+str(counter)+'.json')
	json_obj = json.load(json_data)
	print data
	print len(json_obj)
	total_len += len(json_obj)
	json_data.close()
	if (counter + 1 < LIMIT):
		compiled_file.write(',')
	counter+=1
compiled_file.write(']')

compiled_file.close()

compiled_file = open('compiled_fanfic.json')
final_data = json.load(compiled_file)
print len(final_data), total_len
