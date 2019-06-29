# RESOURCES https://www.datacamp.com/community/tutorials/python-xml-elementtree
# https://epsg.io/map#srs=5649&x=31431725.375401&y=4583225.826214&z=13&layer=streets
import xml.etree.ElementTree as et
import re
import pyproj
import math

#READ KML FILE TREE AND EXTRACT DATA IN COORDINATES BRANCH
filePath = r'[02.Eixample-113]_8522707DF2882B_L.kml'
tree = et.parse(filePath)
lineStrings = tree.findall('.//{http://www.opengis.net/kml/2.2}coordinates')
print(lineStrings)

#FUNCTION TO CONVERT LON LAT INTO XYZ COORDINATES
def gps_to_xy_pyproj(lon, lat):
    crs_wgs = pyproj.Proj(init='epsg:4326') # assuming you're using WGS84 geographic
    crs_bng = pyproj.Proj(init='epsg:5649') # use a locally appropriate projected CRS https://epsg.io/map#srs=5649&x=31431725.375401&y=4583225.826214&z=13&layer=streets
    x, y = pyproj.transform(crs_wgs, crs_bng, lon, lat)
    return x, y

#ORGANIZE DATA IN LIST SEPARETED LIST FOR EACH GEOMETRY
result=[]
listLen=[]

for attributes in lineStrings:
    coordinates = attributes.text
    #print(coordinates)
    coordinates = coordinates.strip()
    coordinates = re.split(';|,| |\n| \n', coordinates)
    result.append(coordinates)

#ORGANIZE DATA IN GROUPS OF 3 ITEMS PER LIST / CREATE A POINT
splitList = []
lenList = []
coordList = []

for i in range(0,len(result)):
    list = result[i]
    lenL = (len(list))
    lenList.append(lenL)

    for x in range(0, len(list), 3): #organize list every three items
        cutList = list[x:x+3]
        cutList=[float(i) for i in cutList]
        splitList.append(cutList)
        xyCord= gps_to_xy_pyproj(cutList[0], cutList[1])
        xyzCord = xyCord + (cutList[2],)
        coordList.append(xyzCord)



listX = [x[0] for x in coordList]
listY = [x[1] for x in coordList]
listZ = [x[2] for x in coordList]


#################################################################################
# #ORGANIZE BACK LIST
# x = 3
# lenList =  [i // x for i in lenList]
#
# Index=[]
#
# for i in range(len(lenList)):
#     if i==0:
#         ind = lenList[i]
#         Index.append(ind)
#     else:
#         ind = Index[i-1]+lenList[i]
#         Index.append(ind)
#
# Index = Index[:-1]
#
#
# #PARTITION THE LIST INTO CHUNCKS
# def partition(alist, Index):
#     return [alist[i:j] for i, j in zip([0]+Index, Index+[None])]
#     return (j)
#
#
# XYZlist = partition(coordList, Index)
#print(XYZlist)


#print(result)
#print(lenList)
#print(splitList)



#################################################################################
#SPLIT X Y Z


# #create list for X Y Z
# X = []
# Y = []
# Z = []
#
# for i in range(len(result)):
#     list = result[i]
#     listX = (list[::3])
#     X.append(listX)
#     listY = (list[1::3])
#     Y.append(listY)
#     listZ = (list[2::3])
#     Z.append(listZ)
#
#
# print(X)
# print("- - - - - - - - - - - - - - - -")
# print(Y)
# print("- - - - - - - - - - - - - - - -")
# print(Z)
