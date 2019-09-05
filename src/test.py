from geomeppy import IDF
from geomeppy import extractor

IDF.setiddname('/Applications/EnergyPlus-8-8-0/Energy+.idd')
idf = IDF('/Applications/EnergyPlus-8-8-0/ExampleFiles/Minimal.idf')
idf.epw = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

newidf = IDF('/Applications/EnergyPlus-8-8-0/ExampleFiles/Minimal.idf')
newidf.epw = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

idf.add_block(
    name='Boring hut',
    coordinates=[(10,0),(10,10),(0,10),(0,0)],
    height=3.5)

idf.add_shading_block(
    name='shading',
    coordinates=[(20,0),(20,10),(10,10),(10,0)],
    height=3.5)
idf.add_shading_block(
    name='shading2',
    coordinates=[(10,10),(10,20),(00,20),(00,10)],
    height=3.5)

idf.set_default_constructions()
idf.intersect_match()
idf.set_wwr(
    wwr=0.4,
    construction="Project External Window"
    )

# I need to find the duplicated surfaces from blocks surfaces and shading surfaces, then get the windows on those wall and remove them
# To find the duplicated surfaces I can use vertices (i.coords) but the order of points in a surface can be different, so I can use average or center point!

def get_centroid(coords): # coords is a list of coordinates of surface
    srf_center = [0, 0, 0]
    for coord in coords:
        srf_center[0] = srf_center[0] + coord[0]
        srf_center[1] = srf_center[1] + coord[1]
        srf_center[2] = srf_center[2] + coord[2]
    for i in range(3):
        srf_center[i] = srf_center[i] / 4
    return srf_center

shading_srfs = idf.getshadingsurfaces()
block_srfs = idf.getsurfaces("Wall")

shading_centers = []
for i in shading_srfs:
    srf_coords = i.coords
    center = get_centroid(srf_coords)
    shading_centers.append(center)

srf_centers = []
for i in block_srfs:
    srf_coords = i.coords
    center = get_centroid(srf_coords)
    srf_centers.append(center)

x = 0
for i in range(len(srf_centers)):
    for shading in shading_centers:
        if srf_centers[i] == shading:
            idf.popidfobject("FENESTRATIONSURFACE:DETAILED",i-x)
            x += 1
idf.intersect_match()
# idf.printidf()
idf.to_obj("test04.obj")

# idf.view_model()
# idf.run()