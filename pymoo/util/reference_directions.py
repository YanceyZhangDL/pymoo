import copy
import numpy as np
from scipy import special
from scipy.spatial.distance import cdist


def get_ref_dirs_from_section(n_obj, n_sections):

    if n_obj == 1:
        return np.array([1.0])

    # all possible values for the vector
    sections = np.linspace(0, 1, num=n_sections + 1)[::-1]

    ref_dirs = []
    ref_recursive([], sections, 0, n_obj, ref_dirs)
    return np.array(ref_dirs)


# returns the closest possible number of references lines to given one
def get_ref_dirs_from_n(n_obj, n_refs, max_sections=100):
    n_sections = np.array([get_number_of_reference_directions(n_obj, i) for i in range(max_sections)])
    idx = np.argmin((n_sections < n_refs).astype(np.int))
    M = get_ref_dirs_from_section(n_obj, idx-1)
    M[M==0] = 0.000001
    return M


def ref_recursive(v, sections, level, max_level, result):
    v_sum = np.sum(np.array(v))

    # sum slightly above or below because of numerical issues
    if v_sum > 1.0001:
        return
    elif level == max_level:
        if 1.0 - v_sum < 0.0001:
            result.append(v)
    else:
        for e in sections:
            next = list(v)
            next.append(e)
            ref_recursive(next, sections, level + 1, max_level, result)


def get_number_of_reference_directions(n_obj, n_sections):
    return int(special.binom(n_obj + n_sections - 1, n_sections))


# def get_ref_dirs_from_points(ref_point, n_obj, pop_size, alpha=0.1, method='uniform'):
#     """
#     This function takes user specified reference points, and creates smaller sets of equidistant
#     Das-Dennis points around the projection of user points on the Das-Dennis hyperplane
#     :param ref_point: List of user specified reference points
#     :param n_obj: Number of objectives to consider
#     :param alpha: Shrinkage factor (0-1), Smaller = tigher convergence, Larger= larger convergence
#     :return: Set of reference points
#     """
#     ref_dirs = []
#     n_vector = np.ones(n_obj)/ np.sqrt(n_obj)  # Normal vector of Das Dennis plane
#     point_on_plane = np.eye(n_obj)[0]  # Point on Das-Dennis
#     pop_size = pop_size/len(ref_point)  # Limit the number of Das-Dennis points
#     if method == 'uniform':
#         reference_directions = get_ref_dirs_from_n(n_obj, pop_size)  # Das-Dennis points
#     elif method == 'random':
#         reference_directions = np.random.rand(int(pop_size), int(n_obj))
#         reference_directions = reference_directions - np.dot(reference_directions - point_on_plane, n_vector)[:, None] * n_vector
#     elif method =='nested':
#         reference_directions = get_ref_dirs_from_section(n_obj, 3)  # Das-Dennis points
#         # ref_dirs.extend(reference_directions)
#         nested = get_ref_dirs_from_section(n_obj, 2)
#         nested = 0.3333333 + 0.5 * (nested - 0.3333333)  # Shrink the nested region
#         nested = (nested - np.dot(nested - point_on_plane, n_vector)[:, None] * n_vector)
#         reference_directions = np.vstack((reference_directions, nested))
#         # return np.array(ref_dirs)
#
#     for point in ref_point:
#         ref_proj = point - np.dot(point - point_on_plane, n_vector) * n_vector
#         if (ref_proj>0).min() == False:
#             A, B = np.eye(n_obj)[np.argsort(cdist([ref_proj], np.eye(n_obj)).T, axis=0)][:2]
#             A, B = A[0], B[0]
#             ref_proj = A + (np.dot(ref_proj - A, B - A) / np.dot(B - A, B - A)) * (B - A)
#         # TODO: Compute which is faster, a copy.deepcopy, or recomputing all the points from get_ref_dirs_from_n
#         ref_dir = copy.deepcopy(reference_directions)  # Copy of computed reference directions
#         for i in range(n_obj):  # Shrink Das-Dennis points by a factor of alpha
#             # ref_dir[:, i] = point[i] + alpha * (ref_dir[:, i] - point[i])
#             ref_dir[:, i] = ref_proj[i] + alpha * (ref_dir[:, i] - ref_proj[i])
#         for d in ref_dir:  # Project shrunked Das-Dennis points back onto original Das-Dennis hyperplane
#             ref_dirs.append(d - np.dot(d - point_on_plane, n_vector) * n_vector)
#     # TODO: Extreme points are only extreme of the scale is normalized between 0-1, how to make them truly extreme?
#     ref_dirs.extend(np.eye(n_obj))  # Add extreme points
#     # extreme = get_ref_dirs_from_n(n_obj, 24)
#     # ref_dirs.extend(extreme)
#     return np.array(ref_dirs)
def get_ref_dirs_from_points(ref_point, n_obj, pop_size, alpha=0.1, method='uniform', p=None):
    """
    This function takes user specified reference points, and creates smaller sets of equidistant
    Das-Dennis points around the projection of user points on the Das-Dennis hyperplane
    :param ref_point: List of user specified reference points
    :param n_obj: Number of objectives to consider
    :param alpha: Shrinkage factor (0-1), Smaller = tigher convergence, Larger= larger convergence
    :return: Set of reference points
    """
    def get_directions(method, n_obj, pop_size):
        if method == 'uniform':
            if p is None:
                reference_directions = get_ref_dirs_from_n(n_obj, pop_size)  # Das-Dennis points
            else:
                reference_directions = get_ref_dirs_from_section(n_obj, p)

        elif method == 'random':
            reference_directions = np.random.rand(int(pop_size), int(n_obj))
            reference_directions = reference_directions - np.dot(reference_directions - point_on_plane, n_vector)[:,
                                                          None] * n_vector
        elif method == 'nested':
            reference_directions = get_ref_dirs_from_section(n_obj, 2)  # Das-Dennis points
            # ref_dirs.extend(reference_directions)
            nested = get_ref_dirs_from_section(n_obj, 2)
            nested = 0.3333333 + 0.5 * (nested - 0.3333333)  # Shrink the nested region
            nested = (nested - np.dot(nested - point_on_plane, n_vector)[:, None] * n_vector)
            reference_directions = np.vstack((reference_directions, nested))
            # return np.array(ref_dirs)
        return reference_directions
    ref_dirs = []
    n_vector = np.ones(n_obj)/ np.sqrt(n_obj)  # Normal vector of Das Dennis plane
    point_on_plane = np.eye(n_obj)[0]  # Point on Das-Dennis
    pop_size = pop_size/len(ref_point)  # Limit the number of Das-Dennis points
    reference_directions = get_directions(method, n_obj, pop_size)
    for point in ref_point:
        ref_proj = point - (np.dot(point - point_on_plane, n_vector) * n_vector)
        if (ref_proj>0).min() == False:
            ref_proj[ref_proj<0] = 0
            ref_proj = ref_proj/sum(ref_proj)
            # while (ref_proj>=0).min() == False:
            #     A, B = np.eye(n_obj)[np.argsort(cdist([ref_proj], np.eye(n_obj)).T, axis=0)][:2]
            #     A, B = A[0], B[0]
            #     ref_proj = A + (np.dot(ref_proj - A, B - A) / np.dot(B - A, B - A)) * (B - A)
            #     ref_proj[ref_proj<1e-6] = 0

        ref_dir = copy.deepcopy(reference_directions)  # Copy of computed reference directions
        # ref_dir = alpha * (ref_dir - ref_proj)
        ref_dir = alpha * ref_dir
        # ref_dir = alpha * ref_dir
        cent = np.mean(ref_dir, axis=0)  # Find centeroid of shrunken reference points
        # Project shrunken Das-Dennis points back onto original Das-Dennis hyperplane
        intercept = line_plane_intersection(np.zeros(n_obj), point, point_on_plane, n_vector)
        shift = intercept - cent  # shift vector

        ref_dir += shift
        # TODO: reflect the points outside the unit simplex back onto it
        if (ref_dir>0).min() == False:
            ref_dir[ref_dir<0] = 0
            ref_proj = ref_dir/sum(ref_dir)

        # ref_dir = np.delete(ref_dir, np.where(ref_dir < 0)[0], axis=0)  # Delets the outlying points
        ref_dirs.extend(ref_dir)

    # TODO: Extreme points are only extreme of the scale is normalized between 0-1, how to make them truly extreme?
    ref_dirs.extend(np.eye(n_obj))  # Add extreme points
    return np.array(ref_dirs)

def norm(F):
    F_min = F.min(axis=0)
    F_max = F.max(axis=0)

# intersection function

def line_plane_intersection(l0, l1, p0, p_no, epsilon=1e-6):
    """
    l0, l1: define the line
    p0, p_no: define the plane:
        p0 is a point on the plane (plane coordinate).
        p_no is a normal vector defining the plane direction;
             (does not need to be normalized).

    reference: https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
    return a Vector or None (when the intersection can't be found).
    """

    l = l1-l0
    dot = np.dot(l, p_no)

    if abs(dot) > epsilon:
        # the factor of the point between p0 -> p1 (0 - 1)
        # if 'fac' is between (0 - 1) the point intersects with the segment.
        # otherwise:
        #  < 0.0: behind p0.
        #  > 1.0: infront of p1.
        w = p0 - l0
        d = np.dot(w, p_no) / dot
        l = l * d
        return l0 + l
    else:
        # The segment is parallel to plane then return the perpendicular projection
        ref_proj = l1 - (np.dot(l1 - p0, p_no) * p_no)
        return ref_proj


if __name__ == '__main__':

    n_vector = np.ones(3) / np.sqrt(3)  # Normal vector of Das Dennis plane
    og = line_plane_intersection(np.array([0,0,0]), np.array([0,0,0]), np.array([1,0,0]), n_vector)

    print(og)

    # import time
    # pt = np.array([[0.4, 0.6, 0.2], [0.8, 0.6, 0.8]])
    # # pt = np.array([[0.1, 2, 1]])
    # start = time.time()
    # w = get_ref_dirs_from_points(pt, n_obj=3, pop_size=100)
    # print(f'{time.time()-start}')
    # import matplotlib.pyplot as plt
    #
    # fig = plt.figure()
    # from mpl_toolkits.mplot3d import Axes3D
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(w[:, 0], w[:, 1], w[:, 2])
    # ax.scatter(pt[:, 0], pt[:, 1], pt[:, 2])
    # for p in pt:
    #     p = p - np.dot(p - np.array([1,0,0]), np.ones(3)/ np.sqrt(3)) * np.ones(3)/ np.sqrt(3)
    #     p_p = p
    #     p_p[p < 0] = 0
    #     ax.scatter(p[0], p[1], p[2], c='r', marker='d')
    #     ax.scatter(p_p[0], p_p[1], p_p[2], c='r', marker='*')
    # plt.show()