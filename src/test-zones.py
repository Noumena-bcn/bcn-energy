import glob
import os
import xml.etree.ElementTree as et
from xml.etree.ElementTree import tostring
import pyproj
from geomeppy import IDF
from geomeppy.geom.polygons import Polygon3D
from geomeppy.utilities import almostequal

#######################################################################################################################

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
        num = gps_to_xy(gps[0], gps[1],gps[2])
        if num not in coordinates_list:
            coordinates_list.append(num)
    return coordinates_list

def make_L_blocks(polygon_coordinates):
    for index in range(len(polygon_coordinates)):
        block_name = 'L_block' + str(index)
        roof_name = 'Shading' + str(index)
        polygon_xy = []
        polygon_z = []
        for point in polygon_coordinates[index]:
            polygon_xy.append((point[0], point[1]))
            polygon_z.append(point[2])
        idf.add_shading_block(
            name=block_name,
            coordinates=polygon_xy,
            height=polygon_z[0]
        )
        shading_roof = idf.newidfobject(
            'SHADING:SITE:DETAILED',
            Name=roof_name
        )
        shading_roof.setcoords(polygon_coordinates[index])

def move_to_origin(floor_coordinates):
    n = 0
    h_center = [0, 0, 0]
    for j in floor_coordinates:
        n = n + 1
        h_center[0] = h_center[0] + int(j[0])
        h_center[1] = h_center[1] + int(j[1])
    for k in range(2):
        h_center[k] = h_center[k] / (-n)
    idf.translate(h_center)

def populate_adjacencies(s1, s2):
    poly1 = Polygon3D(s1.coords)
    poly2 = Polygon3D(s2.coords)
    if almostequal(abs(poly1.distance), abs(poly2.distance), 3):
        if almostequal(poly1.normal_vector, poly2.normal_vector, 3) or almostequal(poly1.normal_vector,
                                                                                   -poly2.normal_vector, 3):
            return True

#######################################################################################################################
# DEFINE HERE THE MAIN PATH

path = '/Users/soroush/Desktop/Noumena/eixample-sample1'
# path = r'C:\Users\Coroush\Desktop\Noumena\bcn-energy-github\190531-Files\eixample-sample1'

IDF.setiddname('/Applications/EnergyPlus-8-8-0/Energy+.idd')
idf = IDF('/Applications/EnergyPlus-8-8-0/ExampleFiles/Minimal.idf')
# IDF.setiddname("C:/EnergyPlusV9-1-0/Energy+.idd")
# idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/Minimal.idf")

idf.epw = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

#######################################################################################################################
# Making H building

# Extracting the elements
paths_H = find_paths('H')
H_root = get_roots(paths_H)[0]
polygons = extract_polygon_elements(H_root)[1:]
polygons.reverse()

folders = []
coordinates = []

for folder in polygons:
    placemarks = []
    for placemark in folder:
        if placemark [0] != "Terraza":
            placemark[2] = element_to_coordinates(placemark[2])
            placemark[2] = [row [0:2] for row in placemark[2]]
            if placemark[0:3] not in placemarks:
                placemarks.append(placemark[0:3])
                for i in placemark[2]:
                    coordinates.append(i)
    folders.append(placemarks)

for folder in range(len(folders)):
    for placemark in range(len(folders[folder])):
        b_name = "level " + str(len(folders)-folder) + " unit " + str(placemark)
        idf.add_block(
            name=b_name,
            coordinates=folders[folder][placemark][2],
            height=3
        )
    idf.translate([0,0,3])
idf.translate([0,0,-3])

#######################################################################################################################
# Making L blocks

paths_L = find_paths('L')
L_roots = get_roots(paths_L)

L_elements = []
for root in L_roots:
    L_elements.append(extract_polygon_elements(root)[0])

L_polygons = []
for i in L_elements:
    for j in i:
        L_polygons.append(element_to_coordinates(j[2]))

make_L_blocks(L_polygons)

#######################################################################################################################
# Move to origin, default construction and intersect match

move_to_origin(coordinates)
idf.set_default_constructions() # INSTEAD OF THIS I NEED TO ASSIGN MATERIALS FOR EACH SURFACE
idf.match()

#######################################################################################################################
# adding external windows for non adjacent to shading blocks

idf.set_wwr(
    wwr=0.4,
    construction="Project External Window"
)
shading_srfs = idf.getshadingsurfaces()
block_srfs = idf.getsurfaces("Wall")
windows = idf.getsubsurfaces("window")

adj_walls = []
for i in range(len(block_srfs)):
    for j in shading_srfs:
        ad = (populate_adjacencies(block_srfs[i],j))
        if ad:
            adj_walls.append (block_srfs[i])
            break

m = 0
for i in range(len(windows)):
    a = windows[i]
    for b in adj_walls:
        if b.Name in a.Name:
            idf.popidfobject("FENESTRATIONSURFACE:DETAILED",i-m)
            m += 1
            break

#######################################################################################################################

idf.to_obj('test-zones.obj')
# idf.view_model()
# idf.run()