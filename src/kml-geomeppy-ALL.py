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
            polygons = placemark.findall(
                ".//{http://www.opengis.net/kml/2.2}Polygon")  # finds polygons in each placemark element
            elements_polygon = []
            for polygon in polygons:
                coords = polygon.findall(
                    ".//{http://www.opengis.net/kml/2.2}coordinates")  # finds the coordinates elements in each polygon element
                elements_polygon.append(coords[0])
            placemark_elements.append(elements_polygon)
        elements.append((placemark_elements))
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


def populate_adjacencies(s1, s2):
    poly1 = Polygon3D(s1.coords)
    poly2 = Polygon3D(s2.coords)
    if almostequal(abs(poly1.distance), abs(poly2.distance), 3):
        if almostequal(poly1.normal_vector, poly2.normal_vector, 3) or almostequal(poly1.normal_vector,-poly2.normal_vector, 3):
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
polygon_element = extract_polygon_elements(H_root)

# Dividing the elements into two lists of blocks and surfaces
blocks_elements = []
surface_elements = []
for i in polygon_element:
    for j in i:
        if len(j) > 1:
            surface_elements.append(j)
        else:
            blocks_elements.append(j[0])

# Putting each zone/block into one list
group_surface = []
for elements in surface_elements:
    surface_coordinates = []
    for element in elements:
        points = element_to_coordinates(element)
        surface_coordinates.append(points)
    group_surface.append(surface_coordinates)

# Extracting the slabs from each block
slabs_groups = []
for surfaces in group_surface:
    slabs = []
    for points in surfaces:
        if len(points) > 2:
            polygon_z_average = 0
            for point in points:
                polygon_z_average += point[2]
            polygon_z_average /= len(points)
            if points[0][2] == polygon_z_average:
                slabs.append(points)
    slabs_groups.append(slabs)

# Separating balconies from apartments
apartments = []
balconies = []
for slab in slabs_groups:
    if len(slab) == 1:
        balconies.append(slab)
    elif len(slab) == 2:
        apartments.append(slab)
    else:
        print("I don't know if its a balcony or apartment")

# Extracting the floor coordinates and height
floor_coordinates = []
floor_heights = []
floor_z = []
apartments.reverse()
for apartment in apartments:
    floor_coordinates.append(apartment[0])
    z_value = apartment[1][0][2] - apartment[0][0][2]
    floor_heights.append(z_value)
    floor_z.append(apartment[0][0][2])

# sorting groups based on floor z values so the polygons in the same height will be in the same group
# so they will all move up together
z = floor_z[0]
level = []
levels = []
for i in range(len(floor_z)):
    if floor_z[i] == z:
        level.append(i)
    if floor_z[i] != z:
        z = floor_z[i]
        levels.append(level)
        level = []

# making the idf blocks
for level in levels:
    for i in level:
        idf.add_block(
            name=str(i),
            coordinates=floor_coordinates[i],
            height=floor_heights[i]
        )
    idf.translate([0, 0, 3])
idf.translate([0, 0, -3])

#######################################################################################################################
# Making L blocks

paths_L = find_paths('L')
L_roots = get_roots(paths_L)

L_elements = []
for root in L_roots:
    L_elements.append(extract_polygon_elements(root))

L_polygons = []
for i in L_elements:
    for j in i:
        for k in j:
            L_polygons.append(element_to_coordinates(k[0]))

make_L_blocks(L_polygons)

#######################################################################################################################
# Move to origin, default construction and intersect match

def move_to_origin():
    n = 0
    h_center = [0, 0, 0]
    for i in floor_coordinates:
        for j in i:
            n = n + 1
            h_center[0] = h_center[0] + j[0]
            h_center[1] = h_center[1] + j[1]
    for k in range(2):
        h_center[k] = h_center[k] / (-n)

    idf.translate(h_center)

move_to_origin()
idf.set_default_constructions()
idf.intersect_match()

#######################################################################################################################
# adding external windows for non adjacent to shading blocks

idf.set_wwr(
    wwr=0.4,
    construction="Project External Window")

shading_srfs = idf.getshadingsurfaces()
block_srfs = idf.getsurfaces("Wall")
windows = idf.getsubsurfaces("window")

print (idf.getsurfaces())


# adj_walls = []
# for i in range(len(block_srfs)):
#     for j in shading_srfs:
#         ad = (populate_adjacencies(block_srfs[i],j))
#         if ad:
#             adj_walls.append (block_srfs[i])
#             break
#
# m = 0
# for i in range(len(windows)):
#     a = windows[i]
#     for b in adj_walls:
#         if b.Name in a.Name:
#             idf.popidfobject("FENESTRATIONSURFACE:DETAILED",i-m)
#             m += 1
#             break

# ########################################################################################################################
#
# idf.to_obj("allblocks.obj")
# idf.view_model()
# idf.run()
