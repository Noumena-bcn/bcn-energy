import glob
import os
import xml.etree.ElementTree as et
from xml.etree.ElementTree import tostring



def find_paths(res):  # block resolution, 'H' for High or 'L' for Low resolution
    list = []
    files = glob.glob(os.path.join(path, '*%s.kml' % res))
    for i in files:
        list.append(i)
    return list

def get_roots(paths):  # Reads the paths and returns the list of the kml file as et elements
    roots = []
    for i in paths:
        tree = et.parse(i)
        root = tree.getroot()
        roots.append(root)
    return roots

def extract_zone_names(root):
    elements = []
    folders = root.findall(".//{http://www.opengis.net/kml/2.2}Folder")  # finds folder elements
    for folder in folders:
        description = folder.findall(".//{http://www.opengis.net/kml/2.2}description")  # finds placemark elements in each folder element
        elements.append(description)
    return elements

path = '/Users/soroush/Desktop/Noumena/eixample-sample1'

# Extracting the elements
paths_H = find_paths('H')
H_root = get_roots(paths_H)[0]
zone_name = extract_zone_names(H_root)
for i in range(len(zone_name)):
    print("-------------- zone ", str(i), "--------------" )
    for j in range(len(zone_name[i])):
        name = tostring(zone_name[i][j], encoding='utf8', method='xml').decode("utf-8").rstrip()
        name = name[98:-18]
        print ( str(j), ": " , name)

