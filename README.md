# Social Segregation Simulator
This uses the [Schelling's model of segregation](https://en.wikipedia.org/wiki/Schelling's_model_of_segregation).
This simulates the model and save the images. You are able to set various parameters of it.

# How to use the simulator
## Dependencies
For the correct execution of the model, the packages listed in `requirements.txt` must be installed. You can use the following command:
```
$ pip install -r requirements.txt
```

## CLI
This repo operates mainly with the CLI. Use `python main.py --help` for more information.

## Options
- **Images path `--images_path`**: The folder to save the images in. Defaults to `/images`.
- **GIF path `--gif_path`**: The folder to save the result gif in. If not specified, the same folder as the images will be used.
- **No GIF `--no_gif`**: You can set this to `True` if you don't want to generate a GIF.
- **Grid width `--width`**: The width of the grid
- **Grid height `--height`**: The height of the grid
- **Palette `--palette`**: Specify this to use a different matplotlib cmap for the resulting images.

## Independent Variables
- **Number of agents `--num_colours`**: The total number of agent types (not including "empty" colour)
- **Iterations `--iterations`**: The number of times to update the grid. Set this to `-1` to run until all cells are happy.
- **Agent Density `--percent_empty`**: Change the density (number) of agents by specifying the percentage of empty cells in the grid.
- **Homophily `--same_neighbour`**: The percentage of same neighbours required for the cell to not move to another grid. The higher this number, agents segregate more, but more iterations are required.

## Dependent Variables
- **Percentage of happy agents**: this is displaed on every iteration.
- **Number of iterations required**: check the number of the last iteration for this.

The program exits when either every cell is happy, or the number of specified iterations are reached.