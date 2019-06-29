# -*- coding: utf-8 -*-
# NOUMENA
import os
import glob
from BCNEnergy.BCNEnergy import BCNEnergy


def main():
    path = '%s\\db-kml' % os.path.normpath(os.getcwd() + os.sep + os.pardir)
    for file_path in glob.glob(os.path.join(path, '*H.kml')):
        bcn_energy = BCNEnergy(file_path)

        bcn_energy.idd_file = 'C:\\EnergyPlusV9-1-0\\Energy+.idd'
        bcn_energy.epw = 'C:\\Users\\starsky\\stealingfired\\bcn-energy\\epw\\ESP_Barcelona.081810_IWEC.epw'
        bcn_energy.idf_path = '%s\\idf' % os.path.normpath(os.getcwd() + os.sep + os.pardir)
        bcn_energy.construct_idf()
        json = bcn_energy.get_db(json_path='%s\\json' % os.path.normpath(os.getcwd() + os.sep + os.pardir))


if __name__ == '__main__':
    main()
