from geomeppy import IDF
from geomeppy.geom.polygons import Polygon3D

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

idf.intersect_match()


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

wwr_zones = {"vivienda":0.2, "comercio":0.7, "comun":0.2}

def _is_window(subsurface):
    if subsurface.key.lower() in {"window", "fenestrationsurface:detailed"}:
        return True

def window_vertices_given_wall(wall, wwr):
    # type: (EpBunch, float) -> Polygon3D
    """Calculate window vertices given wall vertices and glazing ratio.
    :: For each axis:
        1) Translate the axis points so that they are centred around zero
        2) Either:
            a) Multiply the z dimension by the glazing ratio to shrink it vertically
            b) Multiply the x or y dimension by 0.995 to keep inside the surface
        3) Translate the axis points back to their original positions
    :param wall: The wall to add a window on. We expect each wall to have four vertices.
    :param wwr: Window to wall ratio.
    :returns: Window vertices bounding a vertical strip midway up the surface.
    """
    vertices = wall.coords
    average_x = sum([x for x, _y, _z in vertices]) / len(vertices)
    average_y = sum([y for _x, y, _z in vertices]) / len(vertices)
    average_z = sum([z for _x, _y, z in vertices]) / len(vertices)
    # move windows in 0.5% from the edges so they can be drawn in SketchUp
    window_points = [
        [
            ((x - average_x) * 0.999) + average_x,
            ((y - average_y) * 0.999) + average_y,
            ((z - average_z) * wwr) + average_z,
        ]
        for x, y, z in vertices
    ]

    return Polygon3D(window_points)

def custom_wwr (wwr_zones, construction=None):

    try:
        ggr = idf.idfobjects["GLOBALGEOMETRYRULES"][0]  # type: Optional[Idf_MSequence]
    except IndexError:
        ggr = None
    external_walls = filter(
        lambda x: x.Outside_Boundary_Condition.lower() == "outdoors",
        idf.getsurfaces("wall"),
    )
    subsurfaces = idf.getsubsurfaces()

    for wall in external_walls:
        # get any subsurfaces on the wall
        wall_subsurfaces = list(
            filter(lambda x: x.Building_Surface_Name == wall.Name, subsurfaces)
        )
        if not all(_is_window(wss) for wss in wall_subsurfaces) and not force:
            raise ValueError(
                'Not all subsurfaces on wall "{name}" are windows. '
                "Use `force=True` to replace all subsurfaces.".format(name=wall.Name)
            )

        if wall_subsurfaces and not construction:
            constructions = list(
                {wss.Construction_Name for wss in wall_subsurfaces if _is_window(wss)}
            )
            if len(constructions) > 1:
                raise ValueError(
                    'Not all subsurfaces on wall "{name}" have the same construction'.format(
                        name=wall.Name
                    )
                )
            construction = constructions[0]
        # remove all subsurfaces
        for ss in wall_subsurfaces:
            idf.removeidfobject(ss)

        for i in wwr_zones.keys():
            if i in wall.Zone_Name:
                name = i
                wwr = wwr_zones[name]

        if not wwr:
            print ("error in adding windows")
            return

        coords = window_vertices_given_wall(wall, wwr)
        window = idf.newidfobject(
                    "FENESTRATIONSURFACE:DETAILED",
                    Name="%s window" % wall.Name,
                    Surface_Type="Window",
                    Construction_Name=construction or "",
                    Building_Surface_Name=wall.Name,
                    View_Factor_to_Ground="autocalculate")
        window.setcoords(coords, ggr)


idf.set_default_constructions()
custom_wwr(wwr_zones, construction="Project External Window")
idf.to_obj('test2.obj')

idf.run()