import glob
import os
import xml.etree.ElementTree as et
import re
import pyproj
import vtk
from geomeppy import IDF

#DEFINE HERE THE MAIN PATH
path = "C:\\Users\Aldo Sollazzo\Desktop\datakml"
IDF.setiddname('C:\\EnergyPlusV9-1-0\Energy+.idd')
#idf = IDF("C:\\Users\Aldo Sollazzo\Desktop\bcn-energy\src\db-energyPlus-ExampleFiles\Minimal.idf")
idf = IDF("C:\\EnergyPlusV9-1-0\ExampleFiles\Minimal.idf")

idf.epw = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

#FUNCTION TO CONVERT LON LAT INTO XYZ COORDINATES
def gps_to_xy_pyproj(lon, lat):
    crs_wgs = pyproj.Proj(init='epsg:4326') # assuming you're using WGS84 geographic
    crs_bng = pyproj.Proj(init='epsg:5649') # use a locally appropriate projected CRS https://epsg.io/map#srs=5649&x=31431725.375401&y=4583225.826214&z=13&layer=streets
    x, y = pyproj.transform(crs_wgs, crs_bng, lon, lat)
    return x, y

ListH = []

for Hbld in glob.glob(os.path.join(path, '*H.kml')):
    ListH.append(Hbld)
    filePath = Hbld
    tree = et.parse(filePath)
    root = tree.getroot()
    print(root)

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

    result = []
    CordLen = []
    splitList = []
    coordList = []
    listX = []
    listY = []
    listZ = []
    polylineList = []

    for i in range(0, len(CoordL)):
        lineString = CoordL[i]

        for x in lineString:
            coordinates = x.text
            coordSpl = re.split(';|,| |\n| \n', coordinates)
            cList = list(filter(None, coordSpl))
            result.append(cList)
            CordLen.append(int(len(cList) / 3))

    print(result[0])
    # print(len(CordLen))
    # print(CordLen)  ##################### TO USE TO DIVIDE COORDINATES LIST

    # for i in range(0, len(result)):
    #     pointsList = []
    #     cList = result[i]
    #     #print(cList)
    #
    #     x = [float(i) for i in cList[::3]]
    #     y = [float(i) for i in cList[1::3]]
    #     z = [float(i) for i in cList[2::3]]





















        # print("//////////////////NEW POINT LIST//////////////////")
        # points = vtk.vtkPoints()
        # points.SetNumberOfPoints(len(x))
        # lines = vtk.vtkCellArray()
        # lines.InsertNextCell(len(x))
        # polygon = vtk.vtkPolyData()
        #
        # for j in range(0,len(x)):
        #    xyCord = gps_to_xy_pyproj(x[j], y[j])
        #    LX = (xyCord[0])
        #    LY = (xyCord[1])
        #    listX.append(LX)
        #    listY.append(LY)
        #    listZ.append(z[j])
        #
        #    # Create the geometry of a point (the coordinate)
        #    point = (LX,LY,z[j])
        #    print(point)
        #    points.SetPoint(j,point)
        #
        #    # VTKCellArray to create cell connectivity
        #    lines.InsertCellPoint(j)
        #
        #    # Create Polygon
        #    polygon.SetPoints(points)
        #    polygon.SetLines(lines)
        #
        #    # Create a list of polygon
        #    polylineList.append(polygon)
        #    print(polylineList)
        #
        #
        # #polygon.SetPolys(lines)
        #
        # # vtkPolyDataMapper is a class that maps polygonal data (i.e., vtkPolyData)
        # # to graphics primitives
        # polygonMapper = vtk.vtkPolyDataMapper()
        # if vtk.VTK_MAJOR_VERSION <= 5:
        #    polygonMapper.SetInputConnection(polygon.GetProducerPort())
        # else:
        #    polygonMapper.SetInputData(polygon)
        #    polygonMapper.Update()
        #
        # # Create an actor to represent the polygon. The actor orchestrates rendering of
        # # the mapper's graphics primitives. An actor also refers to properties via a
        # # vtkProperty instance, and includes an internal transformation matrix. We
        # # set this actor's mapper to be polygonMapper which we created above.
        # polygonActor = vtk.vtkActor()
        # polygonActor.SetMapper(polygonMapper)
        #
        # # Create the Renderer and assign actors to it. A renderer is like a
        # # viewport. It is part or all of a window on the screen and it is
        # # responsible for drawing the actors it has.  We also set the
        # # background color here.
        # ren1 = vtk.vtkRenderer()
        # ren1.AddActor(polygonActor)
        # ren1.SetBackground(0.1, 0.2, 0.4)
        #
        # # Automatically set up the camera based on the visible actors.
        # # The camera will reposition itself to view the center point of the actors,
        # # and move along its initial view plane normal
        # # (i.e., vector defined from camera position to focal point) so that all of the
        # # actors can be seen.
        # ren1.ResetCamera()
        #
        # # Finally we create the render window which will show up on the screen
        # # We put our renderer into the render window using AddRenderer. We
        # # also set the size to be 300 pixels by 300.
        # renWin = vtk.vtkRenderWindow()
        # renWin.AddRenderer(ren1)
        # renWin.SetSize(800, 800)
        #
        # # The vtkRenderWindowInteractor class watches for events (e.g., keypress,
        # # mouse) in the vtkRenderWindow. These events are translated into
        # # event invocations that VTK understands (see VTK/Common/vtkCommand.h
        # # for all events that VTK processes). Then observers of these VTK
        # # events can process them as appropriate.
        # iren = vtk.vtkRenderWindowInteractor()
        # iren.SetRenderWindow(renWin)
        # iren.Initialize()
        # iren.Start()
        #
        #
        #





# ListL = []
#
# for Lbld in glob.glob(os.path.join(path, '*L.kml')):
#     Lbldname = os.path.basename(Lbld)
#     ListL.append(Lbldname)
#
#     # READ KML FILE TREE AND EXTRACT DATA IN COORDINATES BRANCH
#     filePath = Lbld
#     tree = et.parse(filePath)
#     lineStrings = tree.findall('.//{http://www.opengis.net/kml/2.2}coordinates')
#     #print(lineStrings)


# print(ListH)
# print(ListL)