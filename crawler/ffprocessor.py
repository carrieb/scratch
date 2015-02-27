import json
import sys

def main(argv):
	print argv

def crawl():
	counter = 0
	LIMIT = 0
	compiled_file = open('compiled_fanfic.json', 'w+')
	compiled_file.write('[')
	total_len = 0
	while (counter < LIMIT):
		print "File #" + str(counter)
		json_data = open('/Users/carolyn/Downloads/fanfic_json-final_fanfic_data_'+str(counter)+'.json')
		data = json_data.read()
		compiled_file.write(data.replace(']', '').replace('[',''))
		json_data.close()
		json_data = open('/Users/carolyn/Downloads/fanfic_json-final_fanfic_data_'+str(counter)+'.json')
		json_obj = json.load(json_data)
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

if __name__ == "__main__":
	main(sys.argv[1:])
