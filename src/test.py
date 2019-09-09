from geomeppy import IDF
from geomeppy.geom import surfaces
from geomeppy.geom.polygons import Polygon3D
from geomeppy.utilities import almostequal

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
    height=10)
idf.add_shading_block(
    name='shading2',
    coordinates=[(10,10),(10,20),(0,20),(0,10)],
    height=10)

idf.set_default_constructions()
idf.match()
idf.set_wwr(
    wwr=0.4,
    construction="Project External Window"
    )

shading_srfs = idf.getshadingsurfaces()
block_srfs = idf.getsurfaces("Wall")

shading_coords = []
for i in shading_srfs:
    shading_coords.append(i.coords)

srf_coords = []
for i in block_srfs:
    srf_coords.append(i.coords)

all = block_srfs + shading_srfs
a = surfaces.get_adjacencies(all)
b = a.keys()
c = list(b)

shadows = []
for i in range(len(c)):
    for j in c[i]:
        if "Storey" in j:
            x = int(j.split()[-1]) - 1
            # print (x[-1])
            print (j,x)
            shadows.append(x)
m = 0
for i in shadows:
    idf.popidfobject("FENESTRATIONSURFACE:DETAILED",i-m)
    m += 1

# idf.intersect_match()
# idf.printidf()
# idf.to_obj("test05.obj")

# idf.view_model()
idf.run()