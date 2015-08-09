#from HTMLParser import HTMLParser
import csv
from bs4 import BeautifulSoup, SoupStrainer, NavigableString

filename = "plantlist.htm"
plants = []

plant_file = open(filename, 'r')
dont_include = ("Top","0?--!9")

html = plant_file.read()
parsed_html = BeautifulSoup(html)
for item in BeautifulSoup(html, parseOnlyThese=SoupStrainer('li')):
    if item is None or not hasattr(item, 'contents') or len(item.contents) == 0:
        continue
    try:
        if len(item.contents) == 0:
            continue
        
        item_contents = item.contents[0]
        
        if "?--!" in item_contents:
            plants.append(item_contents.split("?--!")[0].strip())
        elif item_contents.name == "a" and item_contents.contents[0] not in dont_include and len(item_contents.contents[0]) != 1:
            plants.append(item_contents.contents[0])
    except:
        continue
    
with open('plants.csv', 'wb') as csvfile:
    plant_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for plant in plants:
        try:
            plant_writer.writerow([plant,])
        except:
            continue