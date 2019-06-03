# RESOURCES https://www.datacamp.com/community/tutorials/python-xml-elementtree
# https://epsg.io/map#srs=5649&x=31431725.375401&y=4583225.826214&z=13&layer=streets
import xml.etree.ElementTree as et
import re
import pyproj
import math

#READ KML FILE TREE AND EXTRACT DATA IN COORDINATES BRANCH
filePath = r'G:\Mi unidad\_WORK\NOUMENA\2019\2019_01_ENERGYBCN\02-CODES\KMLs\eixample-sample1\[02.Eixample-115]_8821723DF2882B_H.kml'
tree = et.parse(filePath)
root = tree.getroot()

#FUNCTION TO CONVERT LON LAT INTO XYZ COORDINATES
def gps_to_xy_pyproj(lon, lat):
    crs_wgs = pyproj.Proj(init='epsg:4326') # assuming you're using WGS84 geographic
    crs_bng = pyproj.Proj(init='epsg:5649') # use a locally appropriate projected CRS https://epsg.io/map#srs=5649&x=31431725.375401&y=4583225.826214&z=13&layer=streets
    x, y = pyproj.transform(crs_wgs, crs_bng, lon, lat)
    return x, y

with open(filePath, 'rt', encoding="utf-8") as myfile:
    doc = myfile.read()

root = et.fromstring(doc)

PMList = []
PmCoordLenList = []
CoordL = []
FolderList = []

for Folder in root.findall(".//{http://www.opengis.net/kml/2.2}Folder"):
    current_list = []
    FolderList.append(Folder)

    PM = Folder.findall(".//{http://www.opengis.net/kml/2.2}Placemark")
    PMList.append(len(PM))

    for Placemark in Folder.findall(".//{http://www.opengis.net/kml/2.2}Placemark"):
        Coord = Placemark.findall(".//{http://www.opengis.net/kml/2.2}coordinates")
        PmCoordLenList.append(len(Coord))
        CoordL.append(Coord)


# print(len(FolderList))
# print(PMList)# GROUPS OF PLACEMARK IN EACH FOLDER
# print(PmCoordLenList)
# print(sum(PmCoordLenList))
#print(CoordL) # AMOUNT OF COORD FOR EACH PLACEMARK


result = []
CordLen = []

for i in range(0,len(CoordL)):
    lineString = CoordL[i]
    #print(lineString)
    for x in lineString:
        coordinates = x.text
        coordSpl = re.split(';|,| |\n| \n', coordinates)
        cList = list(filter(None, coordSpl))
        result.append(cList)
        CordLen.append(int(len(cList)/3))

#print(len(result))
# print(len(CordLen))
print(sum(CordLen))##################### TO USE TO DIVIDE COORDINATES LIST

# print(result[0])
# print(len(result[0]))

splitList = []
coordList = []
listX = []
listY = []
listZ = []

for i in range(0,len(result)):
    cList = result[i]
    #print(cList)

    x = [float(i) for i in cList[::3]]
    y = [float(i) for i in cList[1::3]]
    z = [float(i) for i in cList[2::3]]
    # print(len(x))
    # print(x)

    for j in range(0,len(x)):
        # print(j)
        # print(x[j], y[j])
        xyCord = gps_to_xy_pyproj(x[j], y[j])
        #print(xyCord[0])
        LX = (xyCord[0])
        LY = (xyCord[1])
        listX.append(LX)
        listY.append(LY)
        listZ.append(z[j])


