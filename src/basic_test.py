from geomeppy import IDF

IDF.setiddname('/Applications/EnergyPlus-8-8-0/Energy+.idd')
idf = IDF('/Applications/EnergyPlus-8-8-0/ExampleFiles/Minimal.idf')
IDF.setiddname("C:/EnergyPlusV8-8-0/Energy+.idd")
idf = IDF("C:/EnergyPlusV8-8-0/ExampleFiles/Minimal.idf")
idf.epw = 'C:/ladybug/ESP_Barcelona.081810_IWEC/ESP_Barcelona.081810_IWEC.epw'

idf.add_block(
    name='viviendo0',
    coordinates=[(5,0),(15,0),(15,5),(5,5)],
    height=3
)

idf.add_block(
    name='viviendo1',
    coordinates=[(5,5),(15,5),(15,10),(5,10)],
    height=3
)

idf.translate([0,0,3])

idf.add_block(
    name='commercio0',
    coordinates=[(0,0),(10,0),(10,5),(0,5)],
    height=3
)

idf.add_block(
    name='commercio1',
    coordinates=[(0,5),(10,5),(10,10),(0,10)],
    height=3
)

idf.intersect_match()
idf.set_default_constructions()
# idf.view_model()
# idf.printidf()
# idf.saveas("basic_test.idf")
idf.run()