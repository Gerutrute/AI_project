import numpy as np
import matplotlib.pyplot as plt


def plot_distance_contours():
    """Visualize equidistant contours for Manhattan and Euclidean metrics."""
    x = np.linspace(-5, 5, 400)
    y = np.linspace(-5, 5, 400)
    X, Y = np.meshgrid(x, y)

    l1 = np.abs(X) + np.abs(Y)
    l2 = np.sqrt(X ** 2 + Y ** 2)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.contour(X, Y, l1, levels=[1, 2, 3, 4], colors="red", linestyles="--")
    ax.contour(X, Y, l2, levels=[1, 2, 3, 4], colors="blue")
    ax.set_title("Manhattan vs Euclidean Distance Contours")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", "box")

    handles = [
        plt.Line2D([0], [0], color="red", linestyle="--", label="Manhattan (L1)"),
        plt.Line2D([0], [0], color="blue", label="Euclidean (L2)")
    ]
    ax.legend(handles=handles, loc="upper right")

    fig.savefig("manhattan_distance_contours.png")
    print("Plot saved as manhattan_distance_contours.png")


if __name__ == "__main__":
    plot_distance_contours()
