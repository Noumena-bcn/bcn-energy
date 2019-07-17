# !/usr/bin/python
# NOUMENA
"""
This module contains the implementation of `BCNEnergy module`.
"""
import os
import json
import xml.etree.ElementTree as ET
import re
import pyproj
import numpy as np
from six import StringIO
from eppy.iddcurrent import iddcurrent
from geomeppy import IDF


class BcnEnergy:

    def __init__(self, file_path=None, os_system="win"):
        """"""

        self._api_opengis = ".//{http://www.opengis.net/kml/2.2}"
        self._opengis_folder = "%sFolder" % self._api_opengis
        self._opengis_description = "%sdescription" % self._api_opengis
        self._opengis_placemark = "%sPlacemark" % self._api_opengis
        self._opengis_name = "%sname" % self._api_opengis
        self._opengis_coordinates = "%scoordinates" % self._api_opengis

        self._slash = BcnEnergy._set_os_system(os_system)

        # file handle
        self._file_path = file_path
        self._xml_document = None

        if file_path:
            self._file_name = os.path.basename(file_path)
            self._open_file()
            self._idf_filename = self._file_name

        # energy plus
        self.idd_file = None
        self.epw = None
        self.idf_path = None
        self._idf = None


        # build a json describing the geometry form xml
        self._json = {}
        self._FILEPATH = 'filePath'
        self._DB = 'db'
        self._ZONES = 'zones'
        self._FLOOR_NAME = 'floorName'
        self._FLOOR_DESCRIPTION = 'floorDescription'
        self._ZONE_NAME = 'zoneName'
        self._XY_COORDINATES = 'xyCoordinates'
        self._HEIGHTS = 'heights'
        self._BLOCK_HEIGHT = 'block_height'
        self._BLOCK_LOCALIZATION = 'block_localization'
        self._Z_MAX = 'zMax'
        self._Z_MIN = 'zMin'
        self._KML_DB = 'kmlDataBase'
        self._GEO_DB = 'geoDataBase'
        self._GEODETIC_COORDINATES = 'geodeticCoordinates'
        self._CARTESIAN_COORDINATES = 'cartesianCoordinates'
        self._CARTESIAN_COORDINATES_FLOOR = 'cartesianCoordinatesFloor'

        # JSON OUTPUT
        self._json[self._FILEPATH] = self._file_path
        self._json[self._DB] = []

        # get the necessary markups to rebuild the geometry
        if file_path:
            self._get_markups()

        self._error_exception = []

    def get_db(self, json_path='', json_file_name="test"):
        """
        Get the database generate for this class. this data base is formatted in JSON file.
        get_db() is a public method

        :param json_path: A path for to store database as a JSON file.
        :param json_file_name: A name for the JSON file. default='test
        """

        # joing the json path with the file name. the extension of the file is implement here
        json_path = '%s%s%s.json' % (json_path, self._slash, json_file_name)

        # if path is not empty write or overwrite the JSON file with the given name and path
        try:
            with open(json_path, 'w') as outfile:
                json.dump(self._json, outfile)
        except Exception as e:
            # store the error on the inside the class
            self._error_exception.append({'function': 'private get_db()', 'error': str(e)})
            raise e

    def get_log(self):
        """
        Get the log files generate errors of exceptions raise for this class.

       TODO add every time to the self._error_exception any further erros to keep track the problems

        get_log() is a public method
        """
        return self._error_exception

    @staticmethod
    def _set_os_system(os):
        if os == "win":
            return "\\"
        elif os == "osx":
            return "/"
        elif os == "unix":
            return "/"

        else:
            return None

    def _open_file(self):
        """
        Open the kml or xml file to be parse.

        this method required the initialisation of the parameters:
        self._file_path: path where are store the kml files
        self._xml_document: variable where will be store the xml document to be parse

        _open_file() is a private method
        """
        try:
            # open the file with encoding : ISO-8859-1
            with open(self._file_path, 'rt', encoding='ISO-8859-1') as xml_file:
                xml_document = xml_file.read()

                # store the xml document
                self._xml_document = ET.fromstring(xml_document)
        except Exception as e:
            # store the error on the inside the class
            self._error_exception.append({'function': 'private _open_file()', 'error': str(e)})
            raise e

    def _get_markups(self):
        """
        Parse and query markups on the self._xml_document with the API:
        [.//{http://www.opengis.net/kml/2.2}]

        The markups parse or implemented this method are:
        [Folder, description, Placemark, name, coordinates]

        this method required the initialisation of the parameters:
        self._open_file(): execute a running without errors
        self._file_path: path where are store the kml files
        self._xml_document: variable where will be store the xml document to be parse
        self._json: variable where is store the parse data from the kml

        _open_file() is a private method
        """
        # for every FOLDER=Building --> Floor execute or start to query for markups to be store
        for folder_markup in self._xml_document.findall(self._opengis_folder):

            # init__ the variable dict=floor to store the FLOORS
            floor = {self._ZONES: []}
            # query the name of FOLDER=Building to be store on the dict=floor as height level of the DICT
            name_markup = folder_markup.findall(self._opengis_name)
            floor[self._FLOOR_NAME] = name_markup[0].text
            # query the description of FOLDER=Building to be store on the dict=floor as height level of the DICT
            name_description = folder_markup.findall(self._opengis_description)
            floor[self._FLOOR_DESCRIPTION] = name_description[0].text

            # for every PLACEMARK=Floor --> zone execute or start to query for markups to be store
            for placemark_markup in folder_markup.findall(self._opengis_placemark):

                # init__ the variable dict=zone to store the ZONES=placemark <-- for every floor
                zone = {}

                # query the name of PLACEMARK=Floor to be store on the dict=zone as height level of the DICT
                name_markup = placemark_markup.findall(self._opengis_name)
                zone[self._ZONE_NAME] = name_markup[0].text

                # init__ the variable dict=kml_db to store the KML geometrical description of the every zone
                kml_db = {}
                # query the name of COORDINATES=Zone to be store as a list coord_markup
                coord_markup = placemark_markup.findall(self._opengis_coordinates)
                # store the coordinates inside the dict=kml_db as GEODETIC COORDINATES[lat, lon]
                kml_db[self._GEODETIC_COORDINATES] = self._get_coordinates(coord_markup)
                # store the coordinates inside the dict=kml_db as CARTESIAN COORDINATES[x, y, z]
                kml_db[self._CARTESIAN_COORDINATES] = self._get_coordinates(coord_markup, geodetic_to_cartesian=True)
                # store the kml_db inside the dict=zone as lower level. dict=zone{dic=kml_db}
                zone[self._KML_DB] = kml_db

                # init__ the variables dict=geo_db and dict=geo_db.
                # to store the IDF geometrical description of the every zone
                # the dict=geo_db is in the height level where is embedded the dict=geo_db
                geo_db = {}
                heights = {}
                # store the coordinates inside the xy_coordinates as PLANAR CARTESIAN COORDINATES[x, y]
                # store information inside the z_min and z_max as NUMERICAL VALUES z_min, z_max
                xy_coordinates, z_min, z_max = \
                    self._get_block(kml_db[self._CARTESIAN_COORDINATES], is_close=False, is_clean_of_duplicates=True)

                # store the coordinates inside the dict=geo_db as PLANAR CARTESIAN COORDINATES[x, y]
                geo_db[self._XY_COORDINATES] = xy_coordinates
                # store the maximal height of the zone inside the dict=geo_db=z_max as NUMERICAL VALUES z_max
                heights[self._Z_MAX] = z_max
                # store the minimal height of the zone inside the dict=geo_db=z_min as NUMERICAL VALUES z_min
                heights[self._Z_MIN] = z_min
                # store the localization  inside the dict=geo_db=z_min as NUMERICAL VALUES block_localization
                heights[self._BLOCK_LOCALIZATION] = z_min
                try:
                    # fin the height of the zone by subtracting the z_min and z_max
                    heights[self._BLOCK_HEIGHT] = z_max - z_min
                except Exception as e:
                    # if exception is raise se the NUMERICAL VALUES block_localization as None
                    heights[self._BLOCK_HEIGHT] = None
                    # store the error on the inside the class
                    self._error_exception.append({'function': 'private _get_markups()', 'error': str(e)})

                # store the heights inside the dict=geo_db as lower level. dict=geo_db{dic=heights}
                geo_db[self._HEIGHTS] = heights
                # store the geo_db inside the dict=zone as lower level. dict=zone{dic=geo_db}
                zone[self._GEO_DB] = geo_db
                # store the zone inside the dict=zone as lower level. dict=zone{dic=geo_db}
                floor[self._ZONES].append(zone)

            # store the floor inside the dict=_json as lower level. dict=_json{dic=_DB{dic=_DB}}
            self._json[self._DB].append(floor)

    @staticmethod
    def _clean_duplicates(points):
        """
        clean duplicates tuple items [points] from a sequence of coordinates.
        get_db() is a public method

        :param points: A list of points to be clean of duplicate.
        """
        # use a set to keep track of which elements are repeat
        # at the same time, populate the new list by a list comprehension
        clean = set()
        # this method relies on the fact that set.add() returns None.
        return [x for x in points if not (x in clean or clean.add(x))]

    @staticmethod
    def _get_coordinates(coordinates, geodetic_to_cartesian=False):

        result = []

        for i in range(0, len(coordinates)):
            line_string = coordinates[i].text
            line_string_2clean = re.split(';| | |\n| \n', line_string)
            line_string_points = list(filter(None, line_string_2clean))

            for j in range(0, len(line_string_points)):
                point = re.split('[,]', line_string_points[j])
                if len(point) == 3:
                    try:
                        if geodetic_to_cartesian:
                            # assuming you're using WGS84 geographic
                            crs_wgs = pyproj.Proj(init='epsg:4326')
                            # use a locally appropriate projected CRS
                            # https: // epsg.io / map  # srs=5649&x=31431725.375401&y=4583225.826214&z=13&layer=streets
                            crs_bng = pyproj.Proj(init='epsg:5649')
                            x, y = pyproj.transform(crs_wgs, crs_bng, float(point[0]), float(point[1]))
                            result.append([x, y, float(point[2])])
                        else:
                            result.append([float(point[0]), float(point[1]), float(point[2])])
                    except Exception as e:
                        print(e)
                        result.append([None, None, None])
                else:
                    result.append([None, None, None])
        return result

    @staticmethod
    def _get_block(coordinates, is_close=True, is_clean_of_duplicates=True):

        xy_coordinates = []
        z_coordinates = list(map(lambda xy: xy[2], coordinates))
        z_max, z_min = np.amax(z_coordinates), np.amin(z_coordinates)

        for i in range(len(coordinates)):
            if coordinates[i][2] == z_min:
                if coordinates[i] not in xy_coordinates:
                    xy_coordinates.append(tuple(coordinates[i][0:2]))

        if is_clean_of_duplicates:
            xy_coordinates = BcnEnergy._clean_duplicates(xy_coordinates)

        if is_close:
            xy_coordinates.append(xy_coordinates[0])

        return xy_coordinates, z_min, z_max

    def construct_idf(self):
        try:
            IDF.setiddname(self.idd_file)
            self._idf = IDF()
            self._idf.new(fname=('%s%s%s.idf' % (self.idf_path, self._slash, self._idf_filename)))
            self._idf.epw = self.epw

            for i in range(len(self._json[self._DB])):
                for zone in self._json[self._DB][i][self._ZONES]:
                    name = zone[self._ZONE_NAME]
                    coordinates_xy = zone[self._GEO_DB][self._XY_COORDINATES]
                    height = zone[self._GEO_DB][self._HEIGHTS][self._BLOCK_HEIGHT]
                    try:
                        if height > 1:
                            self._idf.add_block(
                                name=name, coordinates=coordinates_xy, height=height
                            )
                            self._idf.set_default_constructions()
                            self._idf.intersect_match()
                            self._idf.to_obj('%s%s%s_%s.obj' % (self.idf_path, self._slash, self._idf_filename, name))
                            print('%s%s%s_%s.obj' % (self.idf_path, self._slash,  self._idf_filename, name))
                            # self._idf.run()

                    except Exception as e:
                        self._error_exception.append(e)
        except Exception as e:
            self._error_exception.append(e)

    def run_examples_files(self, output_path, docker=True):
        """
        Open the kml or xml file to be parse.

        :param output_path: A path to Minimal.idf test file
        :param docker:
        """
        if docker:
            minimal_idf = '/usr/local/EnergyPlus-9-0-1/ExampleFiles/Minimal.idf'
        else:
            minimal_idf = ''
        try:
            IDF.setiddname(self.idd_file)
            self._idf = IDF(minimal_idf)
            self._idf.epw = self.epw
            self._idf.add_block(name='Minimal', coordinates=[(10, 0), (10, 10), (0, 10), (0, 0)], height=3.5)
            self._idf.set_default_constructions()
            self._idf.intersect_match()
            self._idf.set_wwr(wwr=0.25)
            self._idf.to_obj('%s%s%s%s.obj' % (self._slash, output_path, self._slash, 'Minimal'))
            self._idf.run()

        except Exception as e:
            self._error_exception.append(e)
