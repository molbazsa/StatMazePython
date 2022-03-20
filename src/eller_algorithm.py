from enum import Enum, auto
import random
import numpy as np


def decision(probability):
    return random.random() < probability


class CellIndex(Enum):
    SET_ID = 0
    WALL_ABOVE = auto()
    WALL_LEFT = auto()


class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = np.zeros((height, width, len(CellIndex)), dtype=int)
        self.exit = None

    @property
    def walls(self):
        walls = np.ones((2 * self.height + 1, 2 * self.width + 1), dtype=int)

        for row in range(self.height):
            for col in range(self.width):
                if not self.cells[row][col][CellIndex.WALL_ABOVE.value]:
                    walls[2 * row][2 * col + 1] = 0

            for col in range(self.width):
                walls[2 * row + 1][2 * col + 1] = 0
                if not self.cells[row][col][CellIndex.WALL_LEFT.value]:
                    walls[2 * row + 1][2 * col] = 0

        exit_side, exit_row, exit_col = self.exit

        if exit_side == "top" or exit_side == "bottom":
            walls[2 * exit_row][2 * exit_col + 1] = 0
        elif exit_side == "left" or exit_side == "right":
            walls[2 * exit_row + 1][2 * exit_col] = 0

        return walls


JOIN_PROBABILITY = 0.5
CONNECTION_PROBABILITY = 0.2


def fillRow(maze, row, set_id):
    for col in range(maze.width):
        maze.cells[row][col][CellIndex.SET_ID.value] = set_id
        maze.cells[row][col][CellIndex.WALL_ABOVE.value] = True
        maze.cells[row][col][CellIndex.WALL_LEFT.value] = True
        set_id += 1

    return set_id


def replaceSetID(maze, row, set_id, new_set_id):
    for col in range(maze.width):
        if maze.cells[row][col][CellIndex.SET_ID.value] == set_id:
            maze.cells[row][col][CellIndex.SET_ID.value] = new_set_id


def joinCells(maze, row):
    for col in range(1, maze.width):
        left_set_id = maze.cells[row][col - 1][CellIndex.SET_ID.value]
        right_set_id = maze.cells[row][col][CellIndex.SET_ID.value]
        if left_set_id != right_set_id and (decision(JOIN_PROBABILITY)):
            replaceSetID(maze, row, right_set_id, left_set_id)
            maze.cells[row][col][CellIndex.WALL_LEFT.value] = False


def connectRow(maze, row):
    set_id_list = (
        maze.cells[row - 1][col][CellIndex.SET_ID.value] for col in range(maze.width)
    )
    sets = set(set_id_list)

    for set_id in sets:
        connected = False
        while not connected:
            for col in range(maze.width):
                if (maze.cells[row - 1][col][CellIndex.SET_ID.value] == set_id) and (
                    decision(CONNECTION_PROBABILITY)
                ):
                    maze.cells[row][col][CellIndex.SET_ID.value] = set_id
                    maze.cells[row][col][CellIndex.WALL_ABOVE.value] = False
                    connected = True


def joinLastRow(maze, row):
    for col in range(1, maze.width):
        left_set_id = maze.cells[row][col - 1][CellIndex.SET_ID.value]
        right_set_id = maze.cells[row][col][CellIndex.SET_ID.value]
        if left_set_id != right_set_id:
            replaceSetID(maze, row, right_set_id, left_set_id)
            maze.cells[row][col][CellIndex.WALL_LEFT.value] = False


def exitPoint(width, height):
    side = random.choice(["top", "right", "bottom", "left"])

    if side == "top":
        row = 0
        col = random.choice(range(width // 2, width))
    elif side == "right":
        row = random.choice(range(height))
        col = width
    elif side == "bottom":
        row = height
        col = random.choice(range(width))
    elif side == "left":
        row = random.choice(range(height // 2, height))
        col = 0

    return side, row, col


def eller_maze(width, height):
    maze = Maze(width, height)

    set_id = 1

    row = 0
    maze.current_row = row
    set_id = fillRow(maze, row, set_id)
    joinCells(maze, row)
    maze.cells[0][0][CellIndex.WALL_ABOVE.value] = False

    for row in range(1, maze.width - 1):
        maze.current_row = row
        set_id = fillRow(maze, row, set_id)
        connectRow(maze, row)
        joinCells(maze, row)

    row = maze.width - 1
    maze.current_row = row
    set_id = fillRow(maze, row, set_id)
    connectRow(maze, row)
    joinLastRow(maze, row)

    maze.exit = exitPoint(width, height)

    return maze
