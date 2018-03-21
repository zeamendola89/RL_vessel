import numpy as np


def local_to_global(x_local, y_local, heading_e_ccw):
    heading_n_cw = 90 - heading_e_ccw
    theta = np.radians(-heading_e_ccw)
    c, s = np.cos(theta), np.sin(theta)
    m = np.matrix(((c, -s), (s, c)))
    local_array = np.matrix([[x_local, y_local]]).T
    transformed = m * local_array
    #TODO Check why y signal goes inverted
    return transformed.item(0), -transformed.item(1), heading_n_cw


def global_to_local(x_global, y_global, heading_n_cw):
    heading_e_ccw = 90 - heading_n_cw
    theta = np.radians(heading_e_ccw)
    c, s = np.cos(theta), np.sin(theta)
    m = np.matrix(((c, -s), (s, c)))
    global_array = np.matrix([[x_global, y_global]]).T
    transformed = m * global_array
    return transformed.item(0), transformed.item(1), heading_e_ccw


def channel_angle_e_ccw(point_a, point_b):
    line = np.array(point_b) - np.array(point_a)
    support = np.array((point_a[0]+10,point_a[1])) - np.array(point_a)
    c = np.dot(line, support) / np.linalg.norm(line) / np.linalg.norm(support)  # -> cosine of the angle
    angle = np.arccos(np.clip(c, -1, 1))
    return 360 - np.rad2deg(angle)

if __name__ == "__main__":
    print(global_to_local(-1,-1,-135))
    print(local_to_global(1.41, 0, 225))
    N03 = (9191.6506, 4967.8532)
    N05 = (6897.7712, 4417.3295)
    print(channel_angle_e_ccw(N03,N05))
    print(local_to_global(1.5, 0, 194))