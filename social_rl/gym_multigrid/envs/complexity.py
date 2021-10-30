import itertools
import os
import sys

import cv2
import numpy as np
from matplotlib import image as mpimg


# complexity function taken from https://github.com/Naereen/Lempel-Ziv_Complexity/blob/master/src/lempel_ziv_complexity.py
from collections import OrderedDict



def lempel_ziv_decomposition(sequence):
    r""" Manual implementation of the Lempel-Ziv decomposition.
    It is defined as the number of different substrings encountered as the stream is viewed from begining to the end.
    As an example:
    >>> s = '1001111011000010'
    >>> lempel_ziv_decomposition(s)  # 1 / 0 / 01 / 11 / 10 / 110 / 00 / 010
    ['1', '0', '01', '11', '10', '110', '00', '010']
    Marking in the different substrings the sequence complexity :math:`\mathrm{Lempel-Ziv}(s) = 8`: :math:`s = 1 / 0 / 01 / 11 / 10 / 110 / 00 / 010`.
    - See the page https://en.wikipedia.org/wiki/Lempel-Ziv_complexity for more details.
    Other examples:
    >>> lempel_ziv_decomposition('1010101010101010')
    ['1', '0', '10', '101', '01', '010', '1010']
    >>> lempel_ziv_decomposition('1001111011000010000010')
    ['1', '0', '01', '11', '10', '110', '00', '010', '000']
    >>> lempel_ziv_decomposition('100111101100001000001010')
    ['1', '0', '01', '11', '10', '110', '00', '010', '000', '0101']
    - Note: it is faster to give the sequence as a string of characters, like `'10001001'`, instead of a list or a numpy array.
    - Note: see this notebook for more details, comparison, benchmarks and experiments: https://Nbviewer.Jupyter.org/github/Naereen/Lempel-Ziv_Complexity/Short_study_of_the_Lempel-Ziv_complexity.ipynb
    - Note: there is also a Cython-powered version, for speedup, see :download:`lempel_ziv_complexity_cython.pyx`.
    """
    sub_strings = OrderedDict()
    n = len(sequence)

    ind = 0
    inc = 1
    while True:
        if ind + inc > len(sequence):
            break
        sub_str = sequence[ind : ind + inc]
        # print(sub_str, ind, inc)
        if sub_str in sub_strings:
            inc += 1
        else:
            sub_strings[sub_str] = 0
            ind += inc
            inc = 1
            # print("Adding", sub_str)
    return list(sub_strings)


def lempel_ziv_complexity(sequence):
    r""" Manual implementation of the Lempel-Ziv complexity.
    It is defined as the number of different substrings encountered as the stream is viewed from begining to the end.
    As an example:
    >>> s = '1001111011000010'
    >>> lempel_ziv_complexity(s)  # 1 / 0 / 01 / 11 / 10 / 110 / 00 / 010
    8
    Marking in the different substrings the sequence complexity :math:`\mathrm{Lempel-Ziv}(s) = 8`: :math:`s = 1 / 0 / 01 / 11 / 10 / 110 / 00 / 010`.
    - See the page https://en.wikipedia.org/wiki/Lempel-Ziv_complexity for more details.
    Other examples:
    >>> lempel_ziv_complexity('1010101010101010')  # 1, 0, 10, 101, 01, 010, 1010
    7
    >>> lempel_ziv_complexity('1001111011000010000010')  # 1, 0, 01, 11, 10, 110, 00, 010, 000
    9
    >>> lempel_ziv_complexity('100111101100001000001010')  # 1, 0, 01, 11, 10, 110, 00, 010, 000, 0101
    10
    - Note: it is faster to give the sequence as a string of characters, like `'10001001'`, instead of a list or a numpy array.
    - Note: see this notebook for more details, comparison, benchmarks and experiments: https://Nbviewer.Jupyter.org/github/Naereen/Lempel-Ziv_Complexity/Short_study_of_the_Lempel-Ziv_complexity.ipynb
    - Note: there is also a Cython-powered version, for speedup, see :download:`lempel_ziv_complexity_cython.pyx`.
    """
    sub_strings = set()
    n = len(sequence)

    ind = 0
    inc = 1
    while True:
        if ind + inc > len(sequence):
            break
        sub_str = sequence[ind : ind + inc]
        if sub_str in sub_strings:
            inc += 1
        else:
            sub_strings.add(sub_str)
            ind += inc
            inc = 1
    return len(sub_strings)

def get_adjacent_pos(center_cell, shape):
    i, j = center_cell

    other_pos = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
    direction = [0,1,2,3]

    def filt(x):
        x = x[0]
        if x[0] < 0 or x[1] < 0 or x[0] >= shape[0] or x[1] >= shape[1]:
            return False
        return True

    other_pos = list(zip(*filter(filt, zip(other_pos, direction))))
    other_pos, direction = other_pos
    return other_pos, direction

def get_node_id(all_nodes, i, j):
    id = all_nodes.index((i, j))
    return id
def get_adjmat_encoding_nodes(encoding):

    wall = np.array((2, 5, 0)).mean()
    floor = np.array((1, 0, 0)).mean()
    goal = np.array((8, 1, 0)).mean()
    encoding = encoding.mean(axis=-1)
    encoding = encoding[1:-1, 1:-1]  # outer border is just walls, and is the same accross all envs

    encoding[encoding == wall] = 0  # walls mean that nothing is adjacent

    nb_nodes = encoding.shape[0] ** 2
    adjacency_mat = np.zeros((nb_nodes, nb_nodes), dtype=int)
    all_nodes = []
    for i in range(encoding.shape[0]):
        for j in range(encoding.shape[1]):
            all_nodes.append((i, j))



    for node_id, (i, j) in enumerate(all_nodes):
        if encoding[i, j] == 0:
            continue

        other_pos, _ = get_adjacent_pos((i,j), encoding.shape)

        for pos in other_pos:
            if encoding[pos[0], pos[1]] == 0:
                continue

            # pos and i,j are adjacent
            adjacency_mat[node_id, get_node_id(all_nodes, *pos)] = 1
    return adjacency_mat, encoding, all_nodes

def get_binary_str(adj_mat):
    # adjacency mat to binary string
    flat_adj_mat = adj_mat.flatten()
    with np.printoptions(threshold=sys.maxsize):
        binary_str = np.array_str(flat_adj_mat)
        binary_str = binary_str.replace("[", "").replace("]", "").replace("\n", "").replace(" ", "")
    return binary_str

def reward_complexity(adj_mat, encoding, all_nodes):
    # Build r_sa matrix. SxA (here, [64, 4])
    N_MINIGRID_ACTIONS = 4
    goal_location = np.argwhere(encoding == encoding.max()).flatten()
    local_cells, direction = get_adjacent_pos(goal_location, encoding.shape)
    r_sa = np.zeros((len(all_nodes),N_MINIGRID_ACTIONS))
    for cell, dir in zip(local_cells, direction):
        goal_location_id = get_node_id(all_nodes, *goal_location)
        cell_location_id = get_node_id(all_nodes, *cell)
        if adj_mat[cell_location_id, goal_location_id] == 1:
            r_sa[cell_location_id, dir] = 1

    beta = np.e
    preferences = np.power(beta, r_sa + 1e-6)
    preferences = preferences / preferences.sum(axis=0, keepdims=True)
    from scipy.stats import entropy
    h = entropy(preferences, np.ones_like(preferences) / N_MINIGRID_ACTIONS, axis=1)    # typo? axis was 0 here

    import networkx as nx
    g = nx.from_numpy_matrix(adj_mat)
    centrality = np.array([v for k, v in nx.algorithms.centrality.betweenness_centrality(g).items()])
    c = sum(h * centrality)
    #if c != 0:
    #    c = int(1/c)
    #else:
    #    c=0
    return c


def analyze_grid(encoding):
    adj_mat, encoding, all_nodes = get_adjmat_encoding_nodes(encoding)

    binary_str = get_binary_str(adj_mat)
    lz = lempel_ziv_complexity(binary_str)

    rw = reward_complexity(adj_mat, encoding, all_nodes)
    return (lz, rw)

def analyze_grid_and_log(encoding):
    lz, rw = analyze_grid(encoding)

    from tensorflow.python.training.summary_io import SummaryWriter
    tb = SummaryWriter(logdir)
    for i, complexity in enumerate(zip(lz_compl, rw_compl)):
        tb.add_scalar("Designer/lz_complexity", complexity[0], i)
        tb.add_scalar("Designer/rw_complexity", complexity[1], i)


def main(dir, logdir):
    dir = dir.replace("//", "/")

    sorted_files = get_all_file_names_sorted(dir, ".grid", full_path=True)
    sorted_files = np.array(sorted_files)#[:1000] # debug


    analyze_grid(sorted_files[0]) #debug (uncomment)

    complexities = []
    from tqdm import tqdm
    from multiprocessing import Pool
    from tqdm.contrib.concurrent import process_map
    result = np.array(process_map(analyze_grid, sorted_files, max_workers=7, chunksize=1000))

    lz_compl = result[:,0]
    rw_compl = result[:,1]




   # lz_compl = list(filter(lambda x: x!=0, lz_compl))
   # rw_compl = list(filter(lambda x: x!=0, rw_compl))

    def do_hist(compl, name):
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        import seaborn as sns
        f, ax = plt.subplots(figsize=(7, 5))
        ax.set(xlabel=name)
        sns.despine(f)
        sns.histplot(data = compl)
        #plt.show() # debug
        plt.savefig(logdir+"/"+name+".png")
        plt.close(f)

    do_hist(lz_compl, "lz_complexity")
    do_hist(rw_compl, "rw_complexity")

    return lz_compl, rw_compl


if __name__ == "__main__":
    def do_bar(dico, name):
        keys = np.array(list(dico.keys()), dtype=int)

        if 0 in keys:   # 0 is aberrant
            keys[keys == 0] = np.max(keys)

        min = np.min(keys)
        max = np.max(keys)
        for i in range(min, max, 2):
            if i not in dico:
                dico[i] = 0

        import matplotlib as mpl
        import matplotlib.pyplot as plt
        import seaborn as sns
        f, ax = plt.subplots(figsize=(7, 5))
        ax.set(xlabel=name)
        sns.despine(f)
        x_data = list(dico.keys())
        y_data = list(dico.values())
        sns.barplot(x=x_data, y=y_data)
        # plt.show() # debug
        plt.savefig(logdir + "/" + name + ".png")
        plt.close(f)


    def do_hist2(compl, name):
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        import seaborn as sns
        f, ax = plt.subplots(figsize=(7, 5))
        ax.set(xlabel=name)
        sns.despine(f)
        sns.histplot(data=compl, stat="percent")
        # plt.show() # debug
        plt.savefig(logdir + "/" + name + ".png")
        plt.close(f)

    import seaborn as sns
    sns.set_palette("muted")
    args = get_args()
    assert args.load_curriculum

    IS_MULTIPLE_MULITPLEX = True
    if IS_MULTIPLE_MULITPLEX:
        all_loads = map(lambda x: f"{args.load_curriculum}/{x}", os.listdir(args.load_curriculum))
    else:
        all_loads = [args.load_curriculum]

    for load in all_loads:
        rw_complexities = []
        lz_complexities = []

        all_subfolders = load_curriculum_multiplex(load)
        for subfolder in all_subfolders:

            logdir = "results/designer/tb"  # to debug, comment line bellow...
            logdir = subfolder + "/designer/tb"

            lz, rw = main(subfolder, logdir)

            lz_complexities.extend(lz)
            rw_complexities.extend(rw)

            def bin_it(dico, arr):
                for c in arr:
                    val = int(c / 2)

                    if val in dico:
                        dico[val] += 1
                    else:
                        dico[val] = 1

            #bin_it(rw_complexities, rw)
            #bin_it(lz_complexities, lz)


        logdir = "results/designer/tb"  # to debug, comment line bellow...
        logdir = load #+ "/designer/tb"
        do_hist2(rw_complexities, "rw_aggregate")
        do_hist2(lz_complexities, "lz_aggregate")
        do_hist2(list(map(lambda x: 1/x, filter(lambda x:x>=0.0001, rw_complexities))), "rw_aggregate_no0")
        print("ONE DONE")
        #exit()


        #do_bar(rw_complexities, "rw_aggregate")
       # do_bar(lz_complexities, "lz_aggregate")