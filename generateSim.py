# This program generates an FDS Simulation file based on the in
def writeHeader(file, chid):
    first_line = "! This FDS Simulation was generated using the blackline experiment script "
    head_line = "HEAD CHID = \'%s\', TITLE = \'Test Run of example blackline experiment\' / \n"
    misc
    file.write()


def generateSim(chid, IJK, XB):

    with open("input_"+chid+".fds", 'w') as file:
        writeHeader(file, chid)