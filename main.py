import os
import sys
import shutil
import random
import itertools
from pathlib import Path
from typing import Optional

from tap import Tap
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import imageio.v3 as iio
import numpy as np


class ArgParser(Tap):
    """Run Schelling's model of segregation with your set parameters, and save the images."""

    # fmt: off
    images_path: Optional[str] = "images"  # The folder to save the images in. Defaults to /images.
    no_gif: Optional[bool] = False  # Whether to save the GIF.
    gif_path: Optional[str] = None  # The folder to save the result gif in. Defaults to the same folder as the images.
    width: Optional[int] = 60  # The width of the grid
    height: Optional[int] = 60  # The height of the grid
    agent_types: Optional[int] = 2  # The total amount of agent types
    iterations: Optional[int] = -1  # The number of times to update the grid. Set this to -1 to run until all cells are happy.
    percent_empty: Optional[float] = 0.5  # the percentage of empty cells in the grid
    same_neighbour: Optional[float] = 0.4  # the percentage of same neighbours required for the cell to not move
    palette: Optional[str] = "GnBu" # the cmap of the resulting image. Passed onto `plt.cm`. If the cmap does not exists, "GnBu" will be used.
    # fmt: on

    def process_args(self) -> None:
        if self.percent_empty < 0 or self.percent_empty >= 1:
            raise ValueError("The percentage of empty cells must be between 0 and 1.")
        if self.same_neighbour < 0 or self.same_neighbour >= 1:
            raise ValueError("The percentage of same cells must be between 0 and 1.")

        if not Path(self.images_path).exists():
            raise ValueError("The target directory of images_path does not exist.")
        for filename in os.listdir(self.images_path):
            file_path = os.path.join(self.images_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except OSError as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
                sys.exit(1)

        if self.gif_path is None:
            self.gif_path = self.images_path
        if not Path(self.gif_path).exists():
            raise ValueError("The target directory of gifs_path does not exist.")


class SocialSegregation:
    def __init__(self, args: ArgParser) -> None:
        self.args = args
        # initialise the grid
        self.grid: np.ndarray = np.random.randint(
            2, args.agent_types + 2, size=(args.height, args.width)
        )
        # make sure n% of the grid is 0
        num_empty = int(args.percent_empty * self.grid.size)
        empty_indice = np.arange(0, self.grid.size, 1)
        np.random.shuffle(empty_indice)
        empty_indice = empty_indice[:num_empty]
        self.grid.flat[empty_indice] = -1

        self.iteration = 0

        self.cmap = getattr(plt.cm, args.palette, plt.cm.GnBu)
        self.cmap.set_under("#000", 0.2)
        self.norm = Normalize(0)

    def run(self) -> None:
        iterator = (
            range(1, self.args.iterations + 1) if self.args.iterations != -1 else itertools.count(1)
        )
        for i in iterator:
            self.iteration = i
            print(f"Iteration {i:<4}", end=" ")
            self._save_img()
            num_unhappy_cells = self._update()
            all_cells = self.grid.size
            percent_happy_cells = round((all_cells - num_unhappy_cells) / all_cells * 100, 2)
            print(f"done ({percent_happy_cells}% cells are happy)")
        if not self.args.no_gif:
            self._save_gif()
        print("All iterations are finished.")

    def _save_img(self):
        """Generate a simple image of a grid."""
        plt.figure(figsize=(10, 10))
        plt.imshow(self.grid, cmap=self.cmap, interpolation="nearest", norm=self.norm)
        plt.axis("off")
        fname = str(self.iteration).rjust(3, "0")
        path = f"{self.args.images_path}/{fname}.png"
        # save the image
        plt.savefig(path, bbox_inches="tight")
        plt.close()

    def _save_gif(self):
        """Saves all the images as a gif."""
        images = []
        for filename in os.listdir(self.args.images_path):
            images.append(iio.imread(f"{self.args.images_path}/{filename}"))
        iio.imwrite(f"{self.args.gif_path}/res.gif", images)

    def _get_neighbours(self, row_number: int, column_number: int):
        """Get all the neighbour cells of a grid."""
        return [
            self.grid[i][j]
            for i in range(row_number - 1, row_number + 2)
            for j in range(column_number - 1, column_number + 2)
            if i >= 0
            and j >= 0
            and i < len(self.grid)
            and j < len(self.grid[0])
            and (i != row_number or j != column_number)
        ]

    def _find_unhappy_cells(self):
        """Find all the unhappy cells - with more than `same_neighbour`% of different colours as neighbours."""
        unhappy_cells = []
        for y_index, row in enumerate(self.grid):
            for x_index, x in enumerate(row):
                if x == -1:
                    continue
                current = x
                neighbours = self._get_neighbours(y_index, x_index)
                not_empty_neighbours = [i for i in neighbours if i != -1]
                if (
                    sum(i == current for i in not_empty_neighbours if i != -1)
                    < len(not_empty_neighbours) * self.args.same_neighbour
                ):
                    unhappy_cells.append((y_index, x_index))
        if not unhappy_cells:
            print("There are no unhappy cells. The grid will not change. Exiting program...")
            if not self.args.no_gif:
                self._save_gif()
            sys.exit(0)  # all cells are happy, they will not move anymore
        random.shuffle(unhappy_cells)
        return unhappy_cells

    def _get_empty_cells(self):
        """Returns all the currently empty cells in the grid."""
        return [
            (y_index, x_index)
            for y_index, row in enumerate(self.grid)
            for x_index, x in enumerate(row)
            if x == -1
        ]

    def _update(self) -> int:
        """Updates the grid and returns the number of unhappy cells."""
        unhappy_cells = self._find_unhappy_cells()
        empty_spots = self._get_empty_cells()
        for y_index, x_index in unhappy_cells:
            try:
                new_y, new_x = random.choice(empty_spots)
            except IndexError:
                empty_spots = self._get_empty_cells()
                new_y, new_x = random.choice(empty_spots)
            self.grid[new_y][new_x] = self.grid[y_index][x_index]
            self.grid[y_index][x_index] = -1
            empty_spots.remove((new_y, new_x))
        return len(unhappy_cells)


if __name__ == "__main__":
    matplotlib.use("Agg")

    args = ArgParser().parse_args()
    model = SocialSegregation(args)
    model.run()
