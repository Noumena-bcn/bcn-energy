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




idf.add_block(
    name='Boring hut',
    coordinates=[(10,0),(10,10),(0,10),(0,0)],
    height=3.5)


idf.match()
idf.set_default_constructions()


for i in idf.model.dt['CONSTRUCTION']:
    if i[1] == "Project Wall":
        i[2] = "A2 - 4 IN DENSE FACE BRICK"

# idf.set_wwr(
#     wwr=0.4,
#     construction="Project External Window")
idf.printidf()

print ("-------------------------------------------------------------------------------------------------------------")



srfs = idf.getsurfaces('wall')
for srf in srfs:
    srf.Construction_Name = "Project Wall"

print (srfs)

# idf.printidf()