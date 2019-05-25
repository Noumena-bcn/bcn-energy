# instructions for geomeppy https://geomeppy.readthedocs.io/en/latest/Start%20here.html#creating-a-model

import glob
import os
import xml.etree.ElementTree as et
import re
import pyproj
#from geomeppy import IDF

#DEFINE HERE THE MAIN PATH
path = "C:\\Users\Aldo Sollazzo\Desktop\datakml"

# IDF.setiddname('C:\\EnergyPlusV9-1-0\Energy+.idd')
# # idf = IDF("C:\\Users\Aldo Sollazzo\Desktop\bcn-energy\src\db-energyPlus-ExampleFiles\Minimal.idf")
# idf = IDF("C:\\EnergyPlusV9-1-0\ExampleFiles\Minimal.idf")
# idf.epw = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

####################################################################################################
#FUNCTION TO CONVERT LON LAT INTO XYZ COORDINATES
def gps_to_xy_pyproj(lon, lat):
    crs_wgs = pyproj.Proj(init='epsg:4326')  # assuming you're using WGS84 geographic
    crs_bng = pyproj.Proj(
        init='epsg:5649')  # use a locally appropriate projected CRS https://epsg.io/map#srs=5649&x=31431725.375401&y=4583225.826214&z=13&layer=streets
    x, y = pyproj.transform(crs_wgs, crs_bng, lon, lat)
    return x, y

####################################################################################################
#FUNCTION TO CONVERT LON LAT INTO XYZ COORDINATES
#my_dict = {"build":, "floor":, "height":, "coord":, "len":}

kml_TotDict={}
kml_dict={} #IT HAS TO BE A NESTED DICTIONARY


#EXTRACT COORDINATES H BUILDINGS FROM FOLDER
ListH = []

for Hbld in glob.glob(os.path.join(path, '*H.kml')):
    ListH.append(Hbld)
    filePath = Hbld
    tree = et.parse(filePath)
    root = tree.getroot()
    #print(root)

    with open(filePath, 'rt', encoding="utf-8") as myfile:
        doc = myfile.read()

    root = et.fromstring(doc)

    PMList = []
    PmCoordLenList = []
    CoordL = []
    FolderList = []
    PlantaList = []
    LenPlanta = []
    cnt = 0

    for Folder in root.findall(".//{http://www.opengis.net/kml/2.2}Folder"):
        current_list = []
        FolderList.append(Folder)

        PM = Folder.findall(".//{http://www.opengis.net/kml/2.2}Placemark")
        PMList.append(len(PM))

        Planta = Folder.findall(".//{http://www.opengis.net/kml/2.2}name")
        Planta.append(PlantaList)
        kml_dict = dict([("Floor", Planta[0].text)])

        for i in range (1,len(Planta)-1):
            cnt+=1
            kml_dict = {cnt: {"Floor":Planta[0].text, "Name" : Planta[i].text}}
            kml_TotDict.update(kml_dict)

        LenPlanta.append(len(Planta))
        #print(kml_dict)

        for Placemark in Folder.findall(".//{http://www.opengis.net/kml/2.2}Placemark"):
            Coord = Placemark.findall(".//{http://www.opengis.net/kml/2.2}coordinates")
            PmCoordLenList.append(len(Coord))
            CoordL.append(Coord)

    #print(kml_TotDict)

####################################################################################################
    # EXTRACT COORDINATE VALUES

    result = []
    CordLen = []
    PmLen = []

    #print(CoordL[0])

    for i in range(0, len(CoordL)):
        lineString = CoordL[i]
        # print(lineString)
        for x in lineString:
            #print(x)
            coordinates = x.text
            coordSpl = re.split(';|,| |\n| \n', coordinates)
            cList = list(filter(None, coordSpl))
            result.append(cList)
            CordLen.append(int(len(cList) / 3))
            PmLen.append(PmCoordLenList[i])

    #print(PmLen)
    #print(PmCoordLenList)
    #print(result)


####################################################################################################
    #EXTRACT COORDINATES FOR 3D GEOMETRIES
    brepCoord = []
    BrepLenList = []

    #print(PmCoordLenList)

    # ERASE ONLY FIRST PLANAR GROUP OF GEOMETRIES
    # for i in range(0,len(result)):
    #     if PmLen[i]>1:
    #         brepCoord.append(result[i])
    #
    # brepCoordLen = [item for item in PmCoordLenList if(item>1)] #ERASE FLAT GEOMETRIES
    # #print(brepCoordLen)


    totIndex=[]

    for i in range(0,len(PmCoordLenList)):
        if i == 0:
            totIndex.append(PmCoordLenList[i])
        else:
            b = PmCoordLenList[i]+totIndex[i-1]
            totIndex.append(b)

    totIndex.insert(0,0)
    totIndex.pop(-1)
    #print(totIndex)
    #print(len(totIndex))


    #EXTRACT COORDINATES ONLY FIRST HORIZONTAL LINES FOR EACH GEOMETRY
    brepBaseCoord = []
    pointXY = []
    lenPointXY = []


    for item in range(0,len(totIndex)):
        i=totIndex[item]
        brepBaseCoord.append(result[i])
    #print(brepBaseCoord)
    #print(len(brepBaseCoord))

    for i in range(0, len(brepBaseCoord)):
        cList = brepBaseCoord[i]
        lenPointXY.append(len(brepBaseCoord[i]))

        #print(cList)

        x = [float(i) for i in cList[::3]]
        y = [float(i) for i in cList[1::3]]
        z = [float(i) for i in cList[2::3]]
        #print(x)

        for j in range(0, len(x)):
            xyCord = gps_to_xy_pyproj(x[j], y[j])
            LX = {"x": round((xyCord[0]), 3)}
            LY = {"y": round((xyCord[1]), 3)}
            LZ = {"z": z[j]}
            #pointXY.extend([LX, LY])

            kml_TotDict[i + 1].update(LX)
            kml_TotDict[i + 1].update(LY)
            kml_TotDict[i + 1].update(LZ)

    print(kml_TotDict)







