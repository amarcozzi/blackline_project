# This program generates an FDS Simulation file based on the in
def write_header(file, chid):
    head = ""
    head += "! This FDS Simulation was generated using the blackline experiment script \n"
    head += "! based on Carl's initial recommendations of a 50m fireline \n"
    head += "! with ignition deployed from a drip torch at pace of a walking firefighter \n"
    head += "! firebreak is 0.6 meters wide to represent hand line\n"
    head += "\n&HEAD CHID = \'%s\', TITLE = \'Test Run of example blackline experiment\' / \n" % chid
    file.write(head)


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
    speed_of_firefighter = 1  # Speed that a burden bearing fighter walks in m/s
    driptorch_burn_duration = 15  # Duration in seconds diesel/gas driptorch mix burns
    driptorch_hrrpua = 1500  # Reaction intensity from burning diesel/gas driptorch mix
    length_of_strip = 1  # in meters
    length_between_strips = 2  # in meters
    time = 11  # start ignitions at 10 seconds to allow for wind to normalize
    firefighter_location = XB[0] + 2  # firefighter begins 2 meters into unit. This keeps fire off the edges for
    # boundary concerns, and mimics real behavior
    ignition_id = 0
    while firefighter_location < XB[1]:
        surf_line = "&SURF ID = 'IGN_%d\', HRRPUA = %d, COLOR = \'RED\', RAMP_Q = \'burner_%d\' /\n" % \
            (ignition_id, driptorch_hrrpua, ignition_id)
        ramp_line_start = "&RAMP ID = \'burner_%s\', F = 0, T = 0 /\n" % str(ignition_id)
        ramp_line_pre_ignite = "&RAMP ID = \'burner_%s\', F = 0, T = %s /\n" % (str(ignition_id), str(time - 1))
        ramp_line_start_ignition = "&RAMP ID = \'burner_%s\', F = 1, T = %s /\n" % (str(ignition_id), str(time))
        ramp_line_end_ignition = "&RAMP ID = \'burner_%s\', F = 1, T = %s /\n" %  \
            (str(ignition_id), str(time + driptorch_burn_duration))
        ramp_line_post_ignition = "&RAMP ID = \'burner_%s\', F = 0, T = %s /\n" % \
            (str(ignition_id), str(time + driptorch_burn_duration + 1))
        vent_line = "&VENT XB = %s, %s, %s, %s, %s, %s, SURF_ID = \'burner_%s\' /\n" % \
            (str(XB[0]), str(XB[1]), str(XB[2]), str(XB[3]), str(XB[4]), str(XB[5]), str(ignition_id))
        ramp_lines = ramp_line_start + ramp_line_pre_ignite + ramp_line_start_ignition + \
            ramp_line_end_ignition + ramp_line_post_ignition
        ignition_line = surf_line + ramp_lines + vent_line
        file.write(ignition_line)
        # update time and firefighter location
        distance_travelled = length_of_strip + length_between_strips
        time_travelled = distance_travelled / speed_of_firefighter
        firefighter_location += distance_travelled
        time += time_travelled

        ignition_id += 1


def generate_sim(file, chid, XB):
    write_header(file, chid)
    write_ignition_pattern(file, XB)


if __name__ == '__main__':
    chid = "blackline_experiment_test"
    XB = [0, 50, 0, 50, 0, 25]
    with open("input_" + chid + ".fds", 'w') as file:
        generate_sim(file, chid, XB)
