# This program generates an FDS Simulation file based on the in
def write_header(file, chid):
    head = ""
    head += "! This FDS Simulation was generated using the blackline experiment script \n"
    head += "! based on Carl's initial recommendations of a 50m fireline \n"
    head += "! with ignition deployed from a drip torch at pace of a walking firefighter \n"
    head += "! firebreak is 0.6 meters wide to represent hand line\n"
    head += "HEAD CHID = \'%s\', TITLE = \'Test Run of example blackline experiment\' / \n" % chid
    file.write(head)


def write_ignition_pattern(file):
    file.write("pass")
    pass


def generate_sim(file, chid):
    write_header(file, chid)
    write_ignition_pattern(file)


if __name__ == '__main__':
    chid = "blackline_experiment_test"
    with open("input_" + chid + ".fds", 'w') as file:
        generate_sim(file, chid)
