import imageio
import matplotlib.pyplot as plt
import numpy as np
import sys


link_line_style = {'color': 'gray', 'linestyle': 'dashed', 'linewidth': 1, 'zorder': 1}


def progress(count, total):
    bar_len = 60
    filled_len = int(round(bar_len * count / total))
    percents = round(100 * count / total, 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] (%s%s)\r' % (bar, percents, '%'))
    sys.stdout.flush()


def affine(a, b, t):
    return a + (b - a) * t


def init_figure(fig_size):
    fig = plt.figure(figsize=fig_size)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.gca().set_aspect('equal')
    return fig


def draw_base(degree, points, lerp_0):
    for i in range(degree):
        plt.plot(points[i:i + 2, 0], points[i:i + 2, 1], **link_line_style)
    for i in range(degree + 1):
        plt.plot([points[i][0], lerp_0[i][0]], [points[i][1], lerp_0[i][1]], **link_line_style)
    plt.scatter(points[:, 0], points[:, 1], c='blue', zorder=2)
    plt.scatter(center[0], center[1], c='#ec407a', marker='+', zorder=2)


def draw_lerp(lerp, i):
    colors = ['c', 'm']
    plt.scatter(lerp[:, 0], lerp[:, 1], c='green', s=10, zorder=2)
    for j in range(lerp.shape[0] - 1):
        plt.plot(lerp[j:j + 2, 0], lerp[j:j + 2, 1], color=colors[i % 2], linewidth=1, zorder=1)


def eval_point(degree, lerp, t):
    for i in range(1, degree + 1):
        draw_lerp(lerp, i)
        lerp = np.array([affine(*lerp[j:j + 2], t) for j in range(0, degree - i + 1)])
    return lerp[0]


def draw_eval_points(eval_points, new_point):
    plt.scatter(new_point[0], new_point[1], c='y', s=10, zorder=2)
    plt.plot(eval_points[:, 0], eval_points[:, 1], 'k-', zorder=1)
    plt.scatter(eval_points[-1][0], eval_points[-1][1], s=15, edgecolors='k', facecolors='none', zorder=2)
    plt.plot([eval_points[-1][0], new_point[0]], [eval_points[-1][1], new_point[1]], **link_line_style)


def fig2img(fig):
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8)
    return img.reshape((h, w, 3))


def main(points, center, delta, outfile, out_size, fps):
    out_mp4 = imageio.get_writer(outfile + '.mp4', fps=fps)
    out_gif = imageio.get_writer(outfile + '.gif', fps=fps)

    degree = points.shape[0] - 1
    lerp_0 = np.array([np.concatenate((affine(center, _[:2], _[2]), _[2:])) for _ in points])

    ts = np.concatenate((np.arange(0, 1, delta), [1]))
    total = ts.shape[0]

    eval_points = np.array([]).reshape((0, 2))
    for i, t in enumerate(ts):
        progress(i, total)
        fig = init_figure((out_size[0] / 100, out_size[1] / 100))
        draw_base(degree, points, lerp_0)

        new_point = eval_point(degree, lerp_0, t)
        eval_points = np.concatenate((eval_points, [affine(center, new_point[:2], 1. / new_point[2])]))
        draw_eval_points(eval_points, new_point)

        img = fig2img(fig)
        out_mp4.append_data(img)
        out_gif.append_data(img)
        plt.close(fig)
    progress(total, total)

    out_mp4.close()
    out_gif.close()


if __name__ == '__main__':
    # x, y, weight
    points = np.array([
        [0, 2, 1],
        [0, 5.5, 1.5],
        [2.5, 8, 0.5],
        [6, 8, 1.5],
        [8, 8, 0.5],
        [8, 3, 1.5],
        [12, 3, 1]
    ])
    center = np.array([6, 2])
    delta = 0.01
    outfile = 'output'
    # width, height
    out_size = (1280, 1024)
    fps = 10

    main(points, center, delta, outfile, out_size, fps)
