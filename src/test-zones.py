import glob
import os
import xml.etree.ElementTree as et
from xml.etree.ElementTree import tostring
import pyproj
from geomeppy import IDF
from geomeppy.utilities import almostequal
from geomeppy.geom.polygons import Polygon3D
import platform as _platform

#######################################################################################################################
# DEFINE HERE THE MAIN PATH

os_name = _platform.system()

if os_name == "Darwin": # if running on Mac use these files
    print("- Running on {}".format("Mac"))
    path = '/Users/soroush/Desktop/Noumena/eixample-sample1'
    IDF.setiddname('/Applications/EnergyPlus-8-8-0/Energy+.idd')
    idf = IDF('/Users/soroush/Desktop/Noumena/bcn-energy/src/gh_template.idf')
    idf.epw = '/Users/soroush/Desktop/Noumena/bcn-energy/src/ESP_Barcelona.081810_IWEC.epw'

elif os_name == "Windows": # if running on Windows use these files
    print("- Running on {}".format("Windows"))
    path = r"C:\Users\Coroush\Desktop\git-noumena\bcn-energy\src\db-kml"
    IDF.setiddname("C:/EnergyPlusV8-8-0/Energy+.idd")
    idf = IDF("C:/Users/Coroush/Desktop/git-noumena/bcn-energy/src/gh_template.idf")
    idf.epw = 'C:/ladybug/ESP_Barcelona.081810_IWEC/ESP_Barcelona.081810_IWEC.epw'

#######################################################################################################################
# Functions

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
        block_name = 'L_block{}'.format(index)
        roof_name = 'Shading{}'.format(index)
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
                         Name = zone_name + "Lights",
                         Zone_or_ZoneList_Name = zone_name,
                         Schedule_Name = "Retail Bldg Light",
                         Design_Level_Calculation_Method = "Watts/Area",
                         Watts_per_Zone_Floor_Area = 18.2987337)
    elif "comun" in zone_name:
        idf.newidfobject("LIGHTS",
                         Name=zone_name + "Lights",
                         Zone_or_ZoneList_Name=zone_name,
                         Schedule_Name="MidriseApartment Corridor Light",
                         Design_Level_Calculation_Method="Watts/Area",
                         Watts_per_Zone_Floor_Area=5.3819805)

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
    elif "comercio" in zone_name:
        idf.newidfobject("PEOPLE",
                        Name = zone_name + "People",
                        Zone_or_ZoneList_Name = zone_name ,
                        Number_of_People_Schedule_Name = "Retail Bldg Occ",
                        Number_of_People_Calculation_Method = "People/Area",
                        People_per_Zone_Floor_Area = 0.161459415,
                        Fraction_Radiant = 0.3,
                        Activity_Level_Schedule_Name = "Retail Activity")

def add_zone_infiltration (zone_name):
    if "vivienda" or "comun" in zone_name:
        idf.newidfobject("ZONEINFILTRATION:DESIGNFLOWRATE",
                        Name = zone_name + "ZoneInfiltration",
                        Zone_or_ZoneList_Name = zone_name ,
                        Schedule_Name = "MidriseApartment Infil",
                        Design_Flow_Rate_Calculation_Method = "Flow/Area",
                        Flow_per_Zone_Floor_Area = 0.000226568446)
    elif "comercio" in zone_name:
        idf.newidfobject("ZONEINFILTRATION:DESIGNFLOWRATE",
                         Name=zone_name + "ZoneInfiltration",
                         Zone_or_ZoneList_Name=zone_name,
                         Schedule_Name="Retail Infil Half On",
                         Design_Flow_Rate_Calculation_Method="Flow/Area",
                         Flow_per_Zone_Floor_Area=0.000226568446)

def add_outdoor_air (zone_name):
    if "vivienda" in zone_name:
        idf.newidfobject("DESIGNSPECIFICATION:OUTDOORAIR",
                        Name = zone_name + "OutdoorAirCntrl",
                        Outdoor_Air_Method = "Sum",
                        Outdoor_Air_Flow_per_Person = 0,
                        Outdoor_Air_Flow_per_Zone_Floor_Area = 0)
    elif "comun" in zone_name:
        idf.newidfobject("DESIGNSPECIFICATION:OUTDOORAIR",
                         Name=zone_name + "OutdoorAirCntrl",
                         Outdoor_Air_Method="Sum",
                         Outdoor_Air_Flow_per_Person=0,
                         Outdoor_Air_Flow_per_Zone_Floor_Area=0.0003048006)
    elif "comercio" in zone_name:
        idf.newidfobject("DESIGNSPECIFICATION:OUTDOORAIR",
                         Name=zone_name + "OutdoorAirCntrl",
                         Outdoor_Air_Method="Sum",
                         Outdoor_Air_Flow_per_Person=0.00353925,
                         Outdoor_Air_Flow_per_Zone_Floor_Area=0.0006096012)

def add_hvac_thermostat (zone_name):
    if "vivienda" in zone_name:
        idf.newidfobject("HVACTEMPLATE:THERMOSTAT",
                        Name = zone_name + "_HVAC",
                        Heating_Setpoint_Schedule_Name = "MidriseApartment Apartment HtgSetp",
                        Cooling_Setpoint_Schedule_Name = "MidriseApartment Apartment ClgSetp"
                        )
    elif "comercio" in zone_name:
        idf.newidfobject("HVACTEMPLATE:THERMOSTAT",
                        Name = zone_name + "_HVAC",
                        Heating_Setpoint_Schedule_Name = "Retail HtgSetp",
                        Cooling_Setpoint_Schedule_Name = "Retail ClgSetp")
    elif "comun" in zone_name:
        idf.newidfobject("HVACTEMPLATE:THERMOSTAT",
                        Name = zone_name + "_HVAC",
                        Heating_Setpoint_Schedule_Name = "MidriseApartment Corridor HtgSetp",
                        Cooling_Setpoint_Schedule_Name = "MidriseApartment Corridor ClgSetp")

def add_hvac_template(zone_name):
    idf.newidfobject("HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM",
                     Zone_Name = zone_name,
                     Template_Thermostat_Name = zone_name + "_HVAC",
                     Maximum_Heating_Supply_Air_Temperature = 40,
                     Maximum_Heating_Supply_Air_Humidity_Ratio = 0.008,
                     Minimum_Cooling_Supply_Air_Humidity_Ratio = 0.0085,
                     Cooling_Limit = "LimitFlowRate",
                     Maximum_Cooling_Air_Flow_Rate = "autosize",
                     Outdoor_Air_Method = "DetailedSpecification",
                     Design_Specification_Outdoor_Air_Object_Name = zone_name + "OutdoorAirCntrl",
                     Outdoor_Air_Economizer_Type = "DifferentialDryBulb")

def _is_window(subsurface):
    if subsurface.key.lower() in {"window", "fenestrationsurface:detailed"}:
        return True

def window_vertices_given_wall(wall, wwr):
    # type: (EpBunch, float) -> Polygon3D
    """Calculate window vertices given wall vertices and glazing ratio.
    :: For each axis:
        1) Translate the axis points so that they are centred around zero
        2) Either:
            a) Multiply the z dimension by the glazing ratio to shrink it vertically
            b) Multiply the x or y dimension by 0.995 to keep inside the surface
        3) Translate the axis points back to their original positions
    :param wall: The wall to add a window on. We expect each wall to have four vertices.
    :param wwr: Window to wall ratio.
    :returns: Window vertices bounding a vertical strip midway up the surface.
    """
    vertices = wall.coords
    average_x = sum([x for x, _y, _z in vertices]) / len(vertices)
    average_y = sum([y for _x, y, _z in vertices]) / len(vertices)
    average_z = sum([z for _x, _y, z in vertices]) / len(vertices)
    # move windows in 0.5% from the edges so they can be drawn in SketchUp
    window_points = [
        [
            ((x - average_x) * 0.999) + average_x,
            ((y - average_y) * 0.999) + average_y,
            ((z - average_z) * wwr) + average_z,
        ]
        for x, y, z in vertices
    ]

    return Polygon3D(window_points)

def custom_wwr (wwr_zones, construction=None):

    try:
        ggr = idf.idfobjects["GLOBALGEOMETRYRULES"][0]  # type: Optional[Idf_MSequence]
    except IndexError:
        ggr = None
    external_walls = filter(
        lambda x: x.Outside_Boundary_Condition.lower() == "outdoors",
        idf.getsurfaces("wall"),
    )
    subsurfaces = idf.getsubsurfaces()

    for wall in external_walls:
        # get any subsurfaces on the wall
        wall_subsurfaces = list(
            filter(lambda x: x.Building_Surface_Name == wall.Name, subsurfaces)
        )
        if not all(_is_window(wss) for wss in wall_subsurfaces) and not force:
            raise ValueError(
                'Not all subsurfaces on wall "{name}" are windows. '
                "Use `force=True` to replace all subsurfaces.".format(name=wall.Name)
            )

        if wall_subsurfaces and not construction:
            constructions = list(
                {wss.Construction_Name for wss in wall_subsurfaces if _is_window(wss)}
            )
            if len(constructions) > 1:
                raise ValueError(
                    'Not all subsurfaces on wall "{name}" have the same construction'.format(
                        name=wall.Name
                    )
                )
            construction = constructions[0]
        # remove all subsurfaces
        for ss in wall_subsurfaces:
            idf.removeidfobject(ss)

        for i in wwr_zones.keys():
            if i in wall.Zone_Name:
                name = i
                wwr = wwr_zones[name]

        if not wwr:
            print ("error in adding windows")
            return

        coords = window_vertices_given_wall(wall, wwr)
        window = idf.newidfobject(
                    "FENESTRATIONSURFACE:DETAILED",
                    Name="%s window" % wall.Name,
                    Surface_Type="Window",
                    Construction_Name=construction or "",
                    Building_Surface_Name=wall.Name,
                    View_Factor_to_Ground="autocalculate")
        window.setcoords(coords, ggr)

#######################################################################################################################
# Making H building

# Extracting the elements
paths_H = find_paths('H')
H_root = get_roots(paths_H)[0]
polygons = extract_polygon_elements(H_root)[1:]
polygons.reverse() # sorting from top floor to bottom

folders = []
coordinates = []
zone_folder = []
balconies_coordinates = []
balconies_level = []

for folder in polygons:
    placemarks = []
    zone_names = []
    balconies_coordinates = []
    for placemark in folder:
        placemark[2] = element_to_coordinates(placemark[2])
        placemark[2] = [row [0:2] for row in placemark[2]]
        if placemark [0] != "Terraza":
            if placemark[0:3] not in placemarks:
                placemarks.append(placemark[0:3])
                if "COMUN" in placemark[0]:
                    zone_names.append("comun")
                elif "Vivienda" in placemark[0]:
                    zone_names.append("vivienda")
                elif "Local" in placemark[0]:
                    zone_names.append("comercio")
                for i in placemark[2]:
                    coordinates.append(i)
        elif placemark[0] == "Terraza":
            if placemark[2] not in balconies_coordinates:
                balconies_coordinates.append(placemark[2])
    balconies_level.append(balconies_coordinates)
    folders.append(placemarks)
    zone_folder.append(zone_names)

for folder in range(len(folders)):
    for placemark in range(len(folders[folder])):
        zone_name = zone_folder[folder][placemark]
        b_name = "{}{}_{}".format(zone_name, len(folders)-folder, placemark)
        idf.add_block(
            name=b_name,
            coordinates=folders[folder][placemark][2],
            height=3)
    idf.translate([0,0,3])

idf.translate([0,0,-3*len(folders)])

for i in range(len(balconies_level)):
    for j in range(len(balconies_level[i])):
        idf.add_shading_block(
            name = "Terrace{}_{}".format(i,j),
            coordinates = balconies_level[i][j],
            height = 1.5)
        terrace_floor = idf.newidfobject(
            'SHADING:SITE:DETAILED',
            Name= "TerraceFloor{}_{}".format(i,j)
        )
        terrace_floor.setcoords(balconies_level[i][j])
    idf.translate([0,0,3])
idf.translate([0,0,-3])

zones = idf.idfobjects["ZONE"]
for i in zones:
    a = i.Name.split()[1]
    a = a.upper()
    i.Name = a

srfs = idf.getsurfaces()
for i in srfs:
    name = (i.Zone_Name)
    name = name.split()
    i.Zone_Name = name[1]

for zone in zones:
    i = zone.Name
    i = i.lower()
    add_electric_equipment(i)
    add_light(i)
    add_people(i)
    add_zone_infiltration(i)
    add_outdoor_air(i)
    add_hvac_thermostat(i)
    add_hvac_template(i)

print ("- Made H Blocks")
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

print ("- Made L Blocks")
#######################################################################################################################
# Move to origin, default construction and intersect match

move_to_origin(coordinates)
idf.set_default_constructions() # INSTEAD OF THIS I NEED TO ASSIGN MATERIALS FOR EACH SURFACE
idf.match()

print ("- Set Construction and Match")
#######################################################################################################################
# adding external windows for non adjacent to shading blocks

wwr_zones = {"vivienda":0.2, "comercio":0.7, "comun":0.2}
custom_wwr(wwr_zones, construction="Project External Window")

shading_srfs = idf.getshadingsurfaces()
block_srfs = idf.getsurfaces("Wall")
windows = idf.getsubsurfaces("window")

shading_block = []
for i in shading_srfs:
    if 'L_block' in i.Name: shading_block.append(i)

adj_walls = []
for i in range(len(block_srfs)):
    for j in shading_block:
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

print ("- Made Windows")
#######################################################################################################################
# Outputs

# idf.printidf()
idf.to_obj(r"C:\Users\Coroush\Desktop\git-noumena\bcn-energy\result2\test-zones.obj")
print ("- Exported OBJ")
# idf.view_model()
idf.saveas(r"C:\Users\Coroush\Desktop\git-noumena\bcn-energy\result2\test-zones.idf")
idf.run(expandobjects = True, output_directory = r"C:\Users\Coroush\Desktop\git-noumena\bcn-energy\result2")