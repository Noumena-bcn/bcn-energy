from geomeppy import IDF


IDF.setiddname('/Applications/EnergyPlus-8-8-0/Energy+.idd')
idf = IDF('/Applications/EnergyPlus-8-8-0/ExampleFiles/Minimal.idf')

idf.epw = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

idf.add_block(
    name='Boring hut',
    coordinates=[(10,0),(10,10),(0,10),(0,0)],
    height=3.5)

idf.set_default_constructions()
idf.match()
idf.set_wwr(
    wwr=0.4,
    construction="Project External Window")
# idf.printidf()

newmaterial = idf.newidfobject("MATERIAL")
newmaterial.Name = "Concrete"
newmaterial.Roughness = 1

windows = idf.getobject('CONSTRUCTION','Project External Window')
windows.Outside_Layer = "Concrete"

idf.printidf()
# print (windows)