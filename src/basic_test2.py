from geomeppy import IDF

IDF.setiddname('/Applications/EnergyPlus-8-8-0/Energy+.idd')
idf = IDF('/Users/soroush/Desktop/Noumena/bcn-energy/src/gh_template.idf')
# IDF.setiddname ("C:/EnergyPlusV8-8-0/Energy+.idd")
# idf = IDF ("C:/Users/Coroush/Desktop/git_noumena/Comparison/gh_result3/basic_test_gh/EnergyPlus/basic_test2.idf")
idf.epw = '/Users/soroush/Documents/ESP_Barcelona.081810_IWEC.epw'

idf.add_block(
    name='vivienda0',
    coordinates=[(5,0),(15,0),(15,5),(5,5)],
    height=3
)

idf.add_block(
    name='vivienda1',
    coordinates=[(5,5),(15,5),(15,10),(5,10)],
    height=3
)

idf.translate([0,0,3])

idf.add_block(
    name='comercio0',
    coordinates=[(0,0),(10,0),(10,5),(0,5)],
    height=3
)

idf.add_block(
    name='comercio1',
    coordinates=[(0,5),(10,5),(10,10),(0,10)],
    height=3
)

# idf.intersect_match()
# idf.set_default_constructions()

zones = idf.idfobjects["ZONE"]
target_zone_names = ["vivienda0", "vivienda1", "comercio0", "comercio1"]
initial_zone_names = []
for i in range(len(zones)):
    zones[i].Name = target_zone_names[i]
    initial_zone_names.append(zones[i].Name)
srfs = idf.getsurfaces('')
for srf in srfs:
    for index in range(len(initial_zone_names)):
        if target_zone_names[index] in srf.Zone_Name:
            srf.Zone_Name = target_zone_names[index]


# idf.view_model()

# idf.printidf()
# idf.saveas("basic_test2.idf")
# idf.run()