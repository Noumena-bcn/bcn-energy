import glob
import os
import xml.etree.ElementTree as et
from xml.etree.ElementTree import tostring
import pyproj
from geomeppy import IDF
from geomeppy.geom.polygons import Polygon3D
from geomeppy.utilities import almostequal

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

def gps_to_xy(lon, lat, z):
    crs_wgs = pyproj.Proj(init='epsg:4326')  # assuming you're using WGS84 geographic
    crs_bng = pyproj.Proj(
        init='epsg:5649')  # use a locally appropriate projected CRS https://epsg.io/map#srs=5649&x=31431725.375401&y=4583225.826214&z=13&layer=streets
    x, y = pyproj.transform(crs_wgs, crs_bng, lon, lat)
    return x, y, z

def extract_polygon_elements(root):
    elements = []
    folders = root.findall(".//{http://www.opengis.net/kml/2.2}Folder")  # finds folder elements
    for folder in folders:
        placemarks = folder.findall(
            ".//{http://www.opengis.net/kml/2.2}Placemark")  # finds placemark elements in each folder element
        placemark_elements = []
        for placemark in placemarks:
            description = placemark.findall(
                ".//{http://www.opengis.net/kml/2.2}description")  # finds description in each placemark element
            if len(description) == 1:
                name = tostring(description[0], encoding='utf8', method='xml').decode("utf-8").rstrip()
                name = name[98:-18]
            else:
                name = "no description"
            styleUrl = folder.findall(
                ".//{http://www.opengis.net/kml/2.2}styleUrl")  # finds elements name in each folder/placemark element
            style = tostring(styleUrl[0], encoding='utf8', method='xml').decode("utf-8").rstrip()
            style = style [96:-15]
            polygons = placemark.findall(
                ".//{http://www.opengis.net/kml/2.2}Polygon")  # finds polygons in each placemark element

            elements_polygon = [name, style, ]
            for polygon in polygons:
                coords = polygon.findall(
                    ".//{http://www.opengis.net/kml/2.2}coordinates")  # finds the coordinates elements in each polygon element
                elements_polygon.append(coords[0])
            placemark_elements.append(elements_polygon)
        elements.append(placemark_elements)
    return elements

def element_to_coordinates(coords):
    coords_str = tostring(coords, encoding='utf8', method='xml').decode("utf-8")  # converts the element to a string
    coords_str = coords_str.replace('<', '>')
    text = coords_str.split('>')[4]  # takes the coordinates numbers from the string as one line
    text = text.replace('\n', '')
    text = text.replace('\t', '')
    coordinate = text.split(' ')  # converts the coordinates string line to the list of 3 numbers
    coordinate = list(filter(None, coordinate))
    coordinates_list = []
    for i in coordinate:
        i = i.split(',')
        gps = []
        for j in i:
            gps.append(float(j))
        num = gps_to_xy(gps[0], gps[1], gps[2])
        if num not in coordinates_list:
            coordinates_list.append(num)
    return coordinates_list


path = '/Users/soroush/Desktop/Noumena/eixample-sample1'

# Extracting the elements
paths_H = find_paths('H')
H_root = get_roots(paths_H)[0]
polygons = extract_polygon_elements(H_root)

folders = []
for folder in polygons:
    placemarks = []
    for placemark in folder:
        if placemark [0] != "Terraza":
            placemark [2] = element_to_coordinates(placemark[2])
            placemarks.append(placemark[0:3])
    folders.append(placemarks)


for folder in folders:
    print ("new folder")
    for placemark in folder:
        print (placemark)