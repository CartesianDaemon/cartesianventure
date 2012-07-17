# Room definition files
import data

def load_room(filename):
    return data.__dict__[filename].room.make_room()