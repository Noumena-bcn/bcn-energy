from geomeppy import IDF

IDF.setiddname('/Applications/EnergyPlus-8-8-0/Energy+.idd')
idf = IDF('/Applications/EnergyPlus-8-8-0/ExampleFiles/Minimal.idf')
idf.epw = 'USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw'

idf.newidfobject(
    "MATERIAL",
    Name="A2 - 4 IN DENSE FACE BRICK",
    Roughness="Rough",
    Thickness=0.1014984,
    Conductivity=1.245296,
    Density=2082.4,
    Specific_Heat=920.48,
    Thermal_Absorptance = 0.90,
    Solar_Absorptance = 0.93,
    Visible_Absorptance = 0.93
)

idf.newidfobject(
    "MATERIAL",
    Name="C2 - 4 IN LW CONCRETE BLOCK",
    Roughness="MediumRough",
    Thickness=0.1014984,
    Conductivity=0.3805070,
    Density=608.7016,
    Specific_Heat=836.8000,
    Thermal_Absorptance = 0.90,
    Solar_Absorptance = 0.65,
    Visible_Absorptance = 0.65
)

idf.add_block(
    name='First_A',
    coordinates=[(10,0),(10,10),(0,10),(0,0)],
    height=3.5
)

idf.translate([0,0,3.5])

idf.add_block(
    name='Ground_A',
    coordinates=[(10,0),(10,10),(0,10),(0,0)],
    height=3.5)

idf.add_block(
    name='Ground_B',
    coordinates=[(20,0),(20,10),(10,10),(10,0)],
    height=3.5)

idf.intersect_match()
idf.set_default_constructions()

for i in idf.model.dt['CONSTRUCTION']:
    if i[1] == "Project Wall":
        i[2] = "A2 - 4 IN DENSE FACE BRICK"

for i in idf.model.dt['CONSTRUCTION']:
    if i[1] == "Project Partition":
        i[2] = "C2 - 4 IN LW CONCRETE BLOCK"

idf.set_wwr(
    wwr=0.4,
    construction="Project External Window")

# idf.view_model()
idf.printidf()
idf.saveas("basic_test.idf")

