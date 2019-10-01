from geomeppy import IDF

IDF.setiddname('/Applications/EnergyPlus-8-8-0/Energy+.idd')
idf = IDF('/Users/soroush/Desktop/Noumena/bcn-energy/src/gh_template.idf')


idf.epw = '/Users/soroush/Desktop/Noumena/bcn-energy/src/ESP_Barcelona.081810_IWEC.epw'


constructions = idf.getobject("CONSTRUCTION",
                              '')
print (constructions)
# idf.printidf()