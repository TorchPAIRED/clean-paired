import numpy as np

ROOT_DIR_BIS = None
def set_root_dir(dir):  # so friggin janky
    global ROOT_DIR_BIS
    ROOT_DIR_BIS = dir

def get_root_dir():
    return ROOT_DIR_BIS

class MinigridConfiguration:
    def __init__(self, encoding, agent_pos, agent_dir, goal_pos, carrying, passable, size, name="generic"):
        self.encoding, self.agent_pos, self.agent_dir, self.goal_pos, self.carrying, self.passable, self.size = encoding, agent_pos, agent_dir, goal_pos, carrying, passable, size
        self.name = name

        # print(f"Is passable? {self.passable}")

    def get_goal_xy(self):
        temp = self.encoding[:,:,0]
        x = np.argwhere(temp == temp.max()).T
        y, x = x
        return x, y

    def get_configuration(self):
        return self.encoding.copy(), self.agent_pos, self.agent_dir, self.goal_pos, self.carrying

    def get_passable(self):
        return self.passable

    def get_size(self):
        return self.size

    def get_name(self):
        return self.name

    def to_filestring(self):
        str = f"""
        {numpy2ascii(self.encoding)}
        {self.agent_pos[0]},{self.agent_pos[1]}
        {self.agent_dir}
        {self.goal_pos[0]},{self.goal_pos[1]}
        {self.carrying}
        {self.passable}
        {self.size}
        {self.name}
        """.strip()

        str = "\n".join(map(lambda x: x.strip(), str.split("\n")))

        return str

    @staticmethod
    def from_filestring(string):
        string = string.split("\n")

        encoding = ascii2numpy(string[0])
        agent_pos = tuplestr2tupleint(string[1])
        agent_dir = int(string[2])
        goal_pos = tuplestr2tupleint(string[3])
        carrying = str2bool(string[4])
        passable = str2bool(string[5])
        size = int(string[6])
        name = string[7]

        return MinigridConfiguration(encoding, agent_pos, agent_dir, goal_pos, carrying, passable, size, name)

def numpy2ascii(numpy_arr):
    s = np.array_str(numpy_arr)
    return s.replace('\n', ',')

def ascii2numpy(ascii_str):
    # Remove space after [
    import re
    s = re.sub('\[ +', '[', ascii_str.strip())
    # Replace commas and spaces
    s = re.sub('[,\s]+', ', ', s)
    import ast
    return np.array(ast.literal_eval(s))

def tuplestr2tupleint(tuplestr):
    tupledstr = tuplestr.split(",")
    return tuple(map(int, tupledstr))

def str2bool(boolstr):
    boolstr = boolstr.lower()
    for x in ["false", "0", "no"]:
        if boolstr == x:
            return False

    for x in ["true", "1", "yes"]:
        if boolstr == x:
            return True


    raise Exception("Wrong string format")