# This program generates an FDS Simulation file based on the in
def write_header(file, chid):
    time_end = 100
    head = ""
    head += "! This FDS Simulation was generated using the blackline experiment script \n"
    head += "! based on Carl's initial recommendations of a 50m fireline \n"
    head += "! with ignition deployed from a drip torch at pace of a walking firefighter \n"
    head += "! firebreak is 0.6 meters wide to represent hand line\n"
    head += "\n&HEAD CHID = \'%s\', TITLE = \'Test Run of example blackline experiment\' / \n" % chid
    file.write(head)
    misc = "&MISC TERRAIN_CASE = .FALSE. /\n"
    time = "&TIME T_END = %d /\n" % time_end
    dump = "&DUMP DT_SLCF=0.1, DT_BNDF=0.1, SMOKE3D=.TRUE. /\n\n"
    misc_time_dump = misc + time + dump
    file.write(misc_time_dump)


def write_ignition_pattern(file, XB):
    """
    This function writes an ignition pattern into an FDS input file. It makes the following assumptions: a firefighter
    carrying a pack will walk at a set meters per second, and will lay down a strip 1 meter long. This
    simulates the swinging mechanics of a drip torch. Each ignition strip burns for 15 seconds and generates 1500 hrrpua
    The format of the FDS input file is:
        &SURF line with ignition ID, hrrpua, color, ramp_q
        &RAMP line with t = 0 and F = 0.
        &RAMP line with t = ignition_time - 1 and F = 0.
        &RAMP line with t = ignition_time and F = 1.
        &RAMP line with t = ignition_time + driptorch_burn_duration and F = 1.
        &RAMP line with t = ignition_time  + driptorch_burn_duration + 1 and F = 1
        &VENT line with XB = location of trip SURF_ID = ignition ID
    :param file: the simulation file to write to
    :param XB: domain size where XB[0], XB[1] are X min/max, XB[2] and XB[3] are Y min/max, etc.
    :return: void - the function writes the input lines to the FDS input file
    """
    speed_of_firefighter = 0.85  # Speed that a burden bearing fighter walks in m/s
    driptorch_burn_duration = 15  # Duration in seconds diesel/gas driptorch mix burns
    driptorch_hrrpua = 1500  # Reaction intensity from burning diesel/gas driptorch mix
    strip_length = 1.5  # in meters
    strip_width = 0.15 # in meters
    length_between_strips = 2  # in meters
    time = 11  # start ignitions at 10 seconds to allow for wind to normalize
    firefighter_location = XB[0] + 2  # firefighter begins 2 meters into unit. This keeps fire off the edges for
    # boundary concerns, and mimics real behavior
    header = "\n\n! Ignition Pattern\n"
    file.write(header)
    ignition_id = 0
    while firefighter_location < XB[1]:
        surf_line = "&SURF ID = 'IGN_%d\', HRRPUA = %d, COLOR = \'RED\', RAMP_Q = \'burner_%d\' /\n" % \
                    (ignition_id, driptorch_hrrpua, ignition_id)
        ramp_line_start = "&RAMP ID = \'burner_%s\', F = 0, T = 0 /\n" % str(ignition_id)
        ramp_line_pre_ignite = "&RAMP ID = \'burner_%s\', F = 0, T = %s /\n" % (str(ignition_id), str(time - 1))
        ramp_line_start_ignition = "&RAMP ID = \'burner_%s\', F = 1, T = %s /\n" % (str(ignition_id), str(time))
        ramp_line_end_ignition = "&RAMP ID = \'burner_%s\', F = 1, T = %s /\n" % \
                                 (str(ignition_id), str(time + driptorch_burn_duration))
        ramp_line_post_ignition = "&RAMP ID = \'burner_%s\', F = 0, T = %s /\n" % \
                                  (str(ignition_id), str(time + driptorch_burn_duration + 1))
        vent_line = "&VENT XB = %s, %s, %s, %s, %s, %s, SURF_ID = \'IGN_%s\' /\n" % \
                    (str(5), str(6), str(firefighter_location), str(firefighter_location + strip_length),
                     str(XB[4]), str(XB[4]), str(ignition_id))
        ramp_lines = ramp_line_start + ramp_line_pre_ignite + ramp_line_start_ignition + \
                     ramp_line_end_ignition + ramp_line_post_ignition
        ignition_line = surf_line + ramp_lines + vent_line
        file.write(ignition_line)
        # update time and firefighter location
        distance_travelled = strip_length + length_between_strips
        time_travelled = distance_travelled / speed_of_firefighter
        firefighter_location += distance_travelled
        time += time_travelled

        ignition_id += 1


def write_boundary_domain_wind(file, IJK, XB):
    # write mesh/spatial domain to input file
    mesh_header = "! MESH definition - This is your spatial domain\n"
    mesh = "&MESH IJK = %d, %d, %d, XB = %d, %d, %d, %d, %d, %d / \n" % \
           (IJK[0], IJK[1], IJK[2], XB[0], XB[1], XB[2], XB[3], XB[4], XB[5])
    file.write(mesh_header + mesh)
    # write wind to input file
    wind_head = "\n! Wind description \n"
    wind = "&SURF ID = \'WIND\', PROFILE = \'ATMOSPHERIC\', Z0 = 2, PLE = 0.143,VEL = -2.5 /\n"
    file.write(wind_head + wind)
    # write boundary conditions to input file
    boundary_header = "\n! Boundary Conditions \n"
    x_min = "&VENT MB = \'XMIN\', SURF_ID = \'WIND\' /\n"
    x_max = "&VENT MB = \'XMAX\', SURF_ID = \'OPEN\' /\n"
    y_min = "&VENT MB = \'YMIN\', SURF_ID = \'OPEN\' /\n"
    y_max = "&VENT MB = \'YMAX\', SURF_ID = \'OPEN\' /\n"
    z_max = "&VENT MB = \'ZMAX\', SURF_ID = \'OPEN\' /\n"
    file.write(boundary_header + x_min + x_max + y_min + y_max + z_max)


def write_fuels(file, XB):
    reac = "\n\n! Combustion\n&REAC\n\tID = \'WOOD\'\n\tFUEL = \'WOOD\'\n" \
           "\tFYI = \'Ritchie, et al., 5th IAFSS, C_3.4 H_6.2 O_2.5, dHc = 15MW/kg\'\n\tSOOT_YIELD = 0.02\n\tO = 2.5" \
           "\n\tC = 3.4\n\tH = 6.2\n\tHEAT_OF_COMBUSTION = 17700 / \n"
    file.write(reac)

    species = "\n\n! Species\n&SPEC ID='WATER VAPOR' /\n&SPEC ID='CARBON DIOXIDE'/\n"
    file.write(species)

    grass_properties = "\n! Grass properties of AU C064 Grass\n&SURF ID = \'GRASS\'\n\tVEGETATION = .TRUE." \
                       "\n\tVEG_DRAG_CONSTANT= 0.159\n\tVEG_UNIT_DRAG_COEFF = .TRUE.\n\tVEG_POSTFIRE_DRAG_FCTR = 0.1" \
                       "\n\tVEG_HCONV_CYLMAX = .FALSE.\n\tVEG_HCONV_CYLLAM = .TRUE.\n\tVEG_HCONV_CYLRE  = .FALSE." \
                       "\n\tVEG_H_PYR = 411\n\tVEG_LOAD = 0.313\n\tVEG_HEIGHT   = 0.51\n\tVEG_MOISTURE = 0.058\n\tVEG_SV= 12240" \
                       "\n\tVEG_CHAR_FRACTION  = 0.2\n\tVEG_DENSITY= 512\n\tEMISSIVITY = 0.99\n\tVEG_DEGRADATION = \'LINEAR\'" \
                       "\n\tFIRELINE_MLR_MAX = 0.074\n\tRGB        = 122,117,48 /\n"
    file.write(grass_properties)

    distribute_grass = "\n&VENT XB = %d, %d, %d, %d, %d, %d, SURF_ID='GRASS' /\n" \
                       % (XB[0], XB[1], XB[2], XB[3], XB[4], XB[4])
    file.write(distribute_grass)


def write_output_tail(file):
    outputs_head = "\n! Simulation outputs here"
    slice_outputs = "\n&SLCF PBY=0,QUANTITY='VELOCITY',VECTOR=.TRUE. /\n&SLCF PBY=0,QUANTITY='TEMPERATURE' /\n"    \
        "&SLCF PBZ=1,QUANTITY='VELOCITY',VECTOR=.TRUE. /\n&SLCF PBZ=2,QUANTITY='VELOCITY',VECTOR=.TRUE. /\n"         \
        "&SLCF PBY=0,QUANTITY='MASS FRACTION',SPEC_ID='WOOD'/\n"
    bndf_output = "\n&BNDF QUANTITY='WALL TEMPERATURE' /\n&BNDF QUANTITY='BURNING RATE' /\n"                         \
        "&BNDF QUANTITY='WALL THICKNESS' /\n&BNDF QUANTITY='CONVECTIVE HEAT FLUX' /\n"                             \
        "&BNDF QUANTITY='RADIATIVE HEAT FLUX' /\n"
    file.write(outputs_head+slice_outputs+bndf_output)


def write_fire_line(file, fireline_location):
    fireline = "\n! Fireline definition goes here\n"    \
        "&VENT XB = %d, %f, %d, %d, %d, %d, SURF_ID = 'FIRELINE', RGB = 115, 118, 83 /\n"                       \
        % (fireline_location[0], fireline_location[1], fireline_location[2], fireline_location[3],
           fireline_location[4], fireline_location[5])
    file.write(fireline)

def generate_sim(file, chid, IJK, XB, fireline_location):
    write_header(file, chid)
    write_boundary_domain_wind(file, IJK, XB)
    write_ignition_pattern(file, XB)
    write_fire_line(file, fireline_location)
    write_fuels(file, XB)
    write_output_tail(file)
    file.write("\n\n&TAIL\t/")


if __name__ == '__main__':
    chid = "blackline_experiment_test"
    IJK = [50, 50, 30]
    XB = [0, 50, 0, 50, 0, 30]
    fireline_width = 0.6
    fireline_location = [40, 40 + fireline_width, XB[2], XB[3], XB[4], XB[4]]
    print(fireline_location)
    with open("input_" + chid + ".fds", 'w') as file:
        generate_sim(file, chid, IJK, XB, fireline_location)
