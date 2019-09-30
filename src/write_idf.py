"""
Zone Programs:
                Midrise Apartment
                Retail

"""

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
idf = IDF('/Users/soroush/Documents/gh_template.idf')
# IDF.setiddname("C:/EnergyPlusV9-1-0/Energy+.idd")
# idf = IDF("C:/EnergyPlusV9-1-0/ExampleFiles/Minimal.idf")

idf.epw = '/Users/soroush/Documents/ESP_Barcelona.081810_IWEC.epw'

#######################################################################################################################
# add zone data to idf file. zone_name has to contain "vivienda" (for residental zones) or "comercio" (for retail)
def add_electric_equipment (zone_name):
    if "vivienda" in zone_name:
        idf.newidfobject("ELECTRICEQUIPMENT",
                        Name = zone_name + "ElectricEquipment",
                        Zone_or_ZoneList_Name = zone_name,
                        Schedule_Name = "MidriseApartment Apartment Equip",
                        Design_Level_Calculation_Method = "Watts/Area",
                        Watts_per_Zone_Floor_Area = 3.8750276284180103,
                        EndUse_Subcategory = "ElectricEquipment")

    elif "comercio" in zone_name:
        idf.newidfobject("ELECTRICEQUIPMENT",
                         Name = zone_name + "ElectricEquipment",
                         Zone_or_ZoneList_Name = zone_name,
                         Schedule_Name = "Retail Bldg Equip",
                         Design_Level_Calculation_Method = "Watts/Area",
                         Watts_per_Zone_Floor_Area = 2.368072439588784,
                         EndUse_Subcategory = "ElectricEquipment")
def add_light (zone_name):
    if "vivienda" in zone_name:
        idf.newidfobject("LIGHTS",
                            Name = zone_name + "Lights",
                            Zone_or_ZoneList_Name = zone_name,
                            Schedule_Name = "MidriseApartment Apartment Light",
                            Design_Level_Calculation_Method = "Watts/Area",
                            Watts_per_Zone_Floor_Area = 11.8403571)
    elif "comercio" in zone_name:
        idf.newidfobject("LIGHTS",
                         Name=zone_name + "Lights",
                         Zone_or_ZoneList_Name=zone_name,
                         Schedule_Name="Retail Bldg Light",
                         Design_Level_Calculation_Method="Watts/Area",
                         Watts_per_Zone_Floor_Area=18.2987337)
def add_people (zone_name):
    if "vivienda" in zone_name:
        idf.newidfobject("PEOPLE",
                        Name = zone_name + "People",
                        Zone_or_ZoneList_Name = zone_name ,
                        Number_of_People_Schedule_Name = "MidriseApartment Apartment Occ",
                        Number_of_People_Calculation_Method = "People/Area",
                        People_per_Zone_Floor_Area = 0.028309217430000002,
                        Fraction_Radiant = 0.3,
                        Activity_Level_Schedule_Name = "MidriseApartment Activity")
    if "comercio" in zone_name:
        idf.newidfobject("PEOPLE",
                        Name = zone_name + "People",
                        Zone_or_ZoneList_Name = zone_name ,
                        Number_of_People_Schedule_Name = "Retail Bldg Occ",
                        Number_of_People_Calculation_Method = "People/Area",
                        People_per_Zone_Floor_Area = 0.161459415,
                        Fraction_Radiant = 0.3,
                        Activity_Level_Schedule_Name = "Retail Activity")
def add_zone_infiltration (zone_name):
    if "vivienda" in zone_name:
        idf.newidfobject("ZONEINFILTRATION:DESIGNFLOWRATE",
                        Name = zone_name + "ZoneInfiltration",
                        Zone_or_ZoneList_Name = zone_name ,
                        Schedule_Name = "MidriseApartment Infil",
                        Design_Flow_Rate_Calculation_Method = "Flow/Area",
                        Flow_per_Zone_Floor_Area = 0.00022656844600000002)
    if "comercio" in zone_name:
        idf.newidfobject("ZONEINFILTRATION:DESIGNFLOWRATE",
                         Name=zone_name + "ZoneInfiltration",
                         Zone_or_ZoneList_Name=zone_name,
                         Schedule_Name="Retail Infil Half On",
                         Design_Flow_Rate_Calculation_Method="Flow/Area",
                         Flow_per_Zone_Floor_Area=0.00022656844600000002)
#######################################################################################################################
zone_names = ["vivienda0","comercio0"]

idf.add_block(
    name='vivienda0',
    coordinates=[(5,0),(15,0),(15,5),(5,5)],
    height=3)

idf.translate([0,0,3])

idf.add_block(
    name='comercio0',
    coordinates=[(0,0),(10,0),(10,5),(0,5)],
    height=3)

idf.intersect_match()
idf.set_default_constructions()

zones = idf.idfobjects["ZONE"]
target_zone_names = ["vivienda0", "comercio0"]
initial_zone_names = []

for i in range(len(zones)):
    zones[i].Name = target_zone_names[i]
    initial_zone_names.append(zones[i].Name)
srfs = idf.getsurfaces('')
for srf in srfs:
    for index in range(len(initial_zone_names)):
        if target_zone_names[index] in srf.Zone_Name:
            srf.Zone_Name = target_zone_names[index]

for i in zone_names:
    add_electric_equipment(i)
    add_light(i)
    add_people(i)
    add_zone_infiltration(i)

# idf.view_model()
idf.printidf()
# idf.run()