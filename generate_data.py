import random
import datetime
import time

def generate_data(chars, start, end, span):
	data = {}
	for c in chars:
		data[c] = []
		for x in xrange(int(start), int(end), int(span)):
			data[c].append((x, random.randint(0, 10)))
		print len(data[c])
	return data

def test_generation():
	chars = ["hermione", "harry"]
	today = datetime.date.today()
	todayts = time.mktime(today.timetuple())
	monthAgo = time.mktime((today - datetime.timedelta(days=30)).timetuple())
	span = datetime.timedelta(days=1)
	print chars, todayts, monthAgo, span.total_seconds()
	data = generate_data(chars, monthAgo, todayts, span.total_seconds())
	print data
	return data
