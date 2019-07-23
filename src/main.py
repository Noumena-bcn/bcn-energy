#!/usr/bin/python
# -*- coding: utf-8 -*-
# !/usr/bin/python
# NOUMENA

import os
import glob
from bcn_energy import BcnEnergy


def main():
    path_unix = '%s' % os.path.normpath(os.getcwd() + os.sep + os.pardir)
    # path_unix_vm_energy_plus = '/usr/local/EnergyPlus-9-0-1/Energy+.idd'
    path_unix_epw = '%s/epw/ESP_Barcelona.081810_IWEC.epw' % path_unix
    BcnEnergy.run_examples_files(path_unix_epw)

    # path_unix_idf = '%s/idf' % path_unix
    #
    # path_unix_json = '%s/json' % path_unix
    #
    # path_db = path_unix_db
    # path_energy_plus = path_unix_vm_energy_plus
    # path_epw = path_unix_epw
    # path_idf = path_unix_idf
    # path_json = path_unix_json
    #
    # for file_path in glob.glob(os.path.join(path_db, '*H.kml')):
    #     # bcn_energy = BcnEnergy(file_path, os_system="unix")
    #     bcn_energy = BcnEnergy(os_system="unix")
    #     #
    #     bcn_energy.idd_file = path_energy_plus
    #     bcn_energy.epw = path_epw
    #     bcn_energy.run_examples_files(output_path=path_idf)
    #     # bcn_energy.idf_path = path_idf
    #     # bcn_energy.construct_idf()
    #     # bcn_energy.get_db(json_path=path_json)


if __name__ == '__main__':
    main()
