import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime
# Process Data

""""
Given a JSON object like the following:
	story = { *("title": ..., "author": *...), "summary":..., "url":...,
	  	  "meta": " rating - language - genre - chapters - words - reviews - follows - updated - published - characters(pairings),
		   update_ts: ..., publish_ts: ... }
Break down into dict of
{ title by author : favorites, summary, pairing, characters, genere, url, length, |sys.now - update_ts| (time since last update), combo score of time since last update & favs }

Sort by combo score and look at top 10.

Draw pretty graph for those.

then compare other fields on whole set

"""

def parse_chars(chars):
	pairings = []
	if '[' in chars:
		pairings.append(tuple(mapsplit[0].replace('[','').split(', ')))
		if split[1].startswith('['):
			pairings.append(tuple(mapsplit[1].replace('[','').split(', ')))
	characters = map(lambda x: x.replace('[','').replace(']',''), chars.split(', '))
	return pairings, characters

def parse_meta(meta):
	res = {}
	start = 0
	parts = map(lambda s: s.encode('ascii').strip(), meta.split(' - '))
	rating, genres, pairings = None, None, None
	chapters, words, reviews = None, None, None
	favs, follows, characters = None, None, None	
	rating = parts[0].replace('Rated: ','')
	if not parts[2].startswith('Chapters'):
		genres = parts[2].split('/')
		chapters = int(parts[3].replace('Chapters: ',''))
		words = (parts[4].replace('Words: ','').replace(',',''))
		start = 5
	else:
		chapters = int(parts[2].replace('Chapters: ',''))
		words = int(parts[3].replace('Words: ','').replace(',',''))
		start = 4
	for i in range(start, len(parts)):
		if parts[i].startswith('Favs: '):
			favs = int(parts[i].replace('Favs: ','').replace(',',''))
		elif parts[i].startswith('Follows: '):
			follows = int(parts[i].replace('Follows: ','').replace(',',''))
		elif parts[i].startswith('Reviews: '):
			reviews = int(parts[i].replace('Reviews: ','').replace(',',''))
		elif parts[i].startswith('Published: '):
			continue
		elif parts[i].startswith('Updated: '):
			continue
		else:
			pairings, characters = parse_chars(parts[i])
	
	# Compute score
	# score = 2favs + reviews + 3follows
	score = reviews + 2*favs + 3*follows
	return {'rating': rating, 'genres':genres, 'chapters':chapters, 'words':words,
		'favs':favs, 'follows':follows, 'characters':characters, 'pairings':pairings, 'score':score}

json_data = open('compiled_fanfic.json')
data = json.load(json_data)

result = []
for story in data:
	parsedMeta = parse_meta(story[u'meta'])
	result.append(dict({ 'title':story[u'title'], 'author':story[u'author'], 'summary':story[u'summary'], 'url':story[u'url'] }.items() + parsedMeta.items()))
	result[-1]['publish_ts'] = story[u'publish_ts']
	result[-1]['update_ts'] = story[u'update_ts']
	now = datetime.now()
	lastUpdate = datetime.fromtimestamp(story[u'publish_ts'])
	delta = now - lastUpdate
	timeSinceLastUpdate = delta.days
	result[-1]['timeSinceLastUpdate'] = timeSinceLastUpdate

top = sorted(result, key=lambda k: k['score'])
top50 = sorted(top[:50], key=lambda k: k['timeSinceLastUpdate'])
for i in range(10):
	story = top50[i]
	print i, story['title'], story['score'], story['timeSinceLastUpdate'], story['summary'], story['characters'], story['pairings'], story['words'], story['chapters']	




"""



 # Draw pretty grpah
mindate = 0
mydate = 0
maxdate = 1225
amonth = 10
sorted_x_date_longs = []
sorted_x_date_strings = []
ystart = 0
y = 0




sorted_y = []
print data
sorted_title_author_strings = []
data.sort()
for x in data:
	print x[u'title']
	sorted_title_author_strings.append(x[u'title'])
	mydate+=1
	y+=1
	sorted_y.append(y)
	sorted_x_date_longs.append(mydate)
	sorted_x_date_strings.append(str(mydate))


plt.xkcd()
fig, ax = plt.subplots()
plt.broken_barh([(0,1),(2,3)],(0,1))
plt.title("WHOO HOO!!")
ax.set_xlim(mindate-amonth, maxdate+amonth)
ax.set_xticks(sorted_x_date_longs)
ax.set_xticklabels(sorted_x_date_strings)
ax.set_ylim(ystart-10, y + 10)
ax.set_yticks(sorted_y)
ax.set_yticklabels(sorted_title_author_strings)
plt.savefig('graph.png')

"""


