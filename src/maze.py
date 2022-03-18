from enum import Enum, auto
import random
import numpy as np
import time
import pygame
from pygame.locals import KEYDOWN, K_s, K_t, K_r, K_q


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
        self.current_row = None
        self.exit = None


class EllerMazeGenerator:
    JOIN_PROBABILITY = 0.5
    CONNECTION_PROBABILITY = 0.2

    def __init__(self, width, height):
        self.width = width
        self.height = height

    @staticmethod
    def fillRow(maze, row, set_id):
        for col in range(maze.width):
            maze.cells[row][col][CellIndex.SET_ID.value] = set_id
            maze.cells[row][col][CellIndex.WALL_ABOVE.value] = True
            maze.cells[row][col][CellIndex.WALL_LEFT.value] = True
            set_id += 1

        return set_id

    @staticmethod
    def replaceSetID(maze, row, set_id, new_set_id):
        for col in range(maze.width):
            if maze.cells[row][col][CellIndex.SET_ID.value] == set_id:
                maze.cells[row][col][CellIndex.SET_ID.value] = new_set_id

    @staticmethod
    def joinCells(maze, row):
        for col in range(1, maze.width):
            left_set_id = maze.cells[row][col - 1][CellIndex.SET_ID.value]
            right_set_id = maze.cells[row][col][CellIndex.SET_ID.value]
            if left_set_id != right_set_id and (
                decision(EllerMazeGenerator.JOIN_PROBABILITY)
            ):
                EllerMazeGenerator.replaceSetID(maze, row, right_set_id, left_set_id)
                maze.cells[row][col][CellIndex.WALL_LEFT.value] = False

    @staticmethod
    def connectRow(maze, row):
        set_id_list = (
            maze.cells[row - 1][col][CellIndex.SET_ID.value]
            for col in range(maze.width)
        )
        sets = set(set_id_list)

        for set_id in sets:
            connected = False
            while not connected:
                for col in range(maze.width):
                    if (
                        maze.cells[row - 1][col][CellIndex.SET_ID.value] == set_id
                    ) and (decision(EllerMazeGenerator.CONNECTION_PROBABILITY)):
                        maze.cells[row][col][CellIndex.SET_ID.value] = set_id
                        maze.cells[row][col][CellIndex.WALL_ABOVE.value] = False
                        connected = True

    @staticmethod
    def joinLastRow(maze, row):
        for col in range(1, maze.width):
            left_set_id = maze.cells[row][col - 1][CellIndex.SET_ID.value]
            right_set_id = maze.cells[row][col][CellIndex.SET_ID.value]
            if left_set_id != right_set_id:
                EllerMazeGenerator.replaceSetID(maze, row, right_set_id, left_set_id)
                maze.cells[row][col][CellIndex.WALL_LEFT.value] = False

    @staticmethod
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

    def iterate(self):
        maze = Maze(self.width, self.height)

        set_id = 1

        row = 0
        maze.current_row = row
        set_id = EllerMazeGenerator.fillRow(maze, row, set_id)
        EllerMazeGenerator.joinCells(maze, row)
        maze.cells[0][0][CellIndex.WALL_ABOVE.value] = False
        yield maze

        for row in range(1, maze.width):
            maze.current_row = row
            set_id = EllerMazeGenerator.fillRow(maze, row, set_id)
            EllerMazeGenerator.connectRow(maze, row)
            yield maze
            EllerMazeGenerator.joinCells(maze, row)
            yield maze

        EllerMazeGenerator.joinLastRow(maze, row)
        yield maze
        maze.exit = EllerMazeGenerator.exitPoint(self.width, self.height)
        yield maze

    def frames(self):
        frame_maze = Maze(self.width, self.height)

        for maze in self.iterate():
            frame_maze.current_row = maze.current_row
            frame_maze.exit = maze.exit
            for col in range(maze.width):
                cell = maze.cells[maze.current_row][col]
                frame_maze.cells[maze.current_row][col] = cell
                yield frame_maze

    def generate(self):
        *_, last = self.iterate()
        return last


def print_maze(maze):
    BLOCK = 3 * "█"
    SPACE = 3 * " "

    print()

    for row in range(maze.height):
        for col in range(maze.width):
            print(BLOCK, end="")
            if (
                maze.cells[row][col][CellIndex.WALL_ABOVE.value]
                or not maze.cells[row][col][CellIndex.SET_ID.value]
            ):
                print(BLOCK, end="")
            else:
                print(SPACE, end="")
        print(BLOCK)

        for col in range(maze.width):
            if (
                maze.cells[row][col][CellIndex.WALL_LEFT.value]
                or not maze.cells[row][col][CellIndex.SET_ID.value]
            ):
                print(BLOCK, end="")
            else:
                print(SPACE, end="")
            print("{:3d}".format(maze.cells[row][col][CellIndex.SET_ID.value]), end="")
        print(BLOCK)

    print((2 * maze.width + 1) * BLOCK)


class MazeWindow:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    POLLING_RATE = 0.01
    STEP_RATE = 0.03

    CELL_SIZE = 10
    PADDING = 20

    def __init__(self, maze_generator):
        self.maze_generator = maze_generator
        self.num_cells_horizontal = 2 * maze_generator.width + 1
        self.num_cells_vertical = 2 * maze_generator.height + 1

    def show(self, *, animate=False, console=False):
        maze_width = self.num_cells_horizontal * MazeWindow.CELL_SIZE
        width = maze_width + 2 * MazeWindow.PADDING
        maze_height = self.num_cells_vertical * MazeWindow.CELL_SIZE
        height = maze_height + 2 * MazeWindow.PADDING

        pygame.init()
        pygame.display.set_caption("Maze")
        icon = pygame.image.load("assets/jigsaw.png")
        pygame.display.set_icon(icon)
        self.screen = pygame.display.set_mode((width, height))

        self.should_animate = animate
        self.show_console = console
        self.startRender()

        while self.checkEvents():
            if self.animating:
                self.render()
            time.sleep(MazeWindow.POLLING_RATE)

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == KEYDOWN and event.key == K_q
            ):
                print()
                print("quit")
                return False
            elif event.type == KEYDOWN and event.key == K_s:
                self.animating = not self.animating
            elif event.type == KEYDOWN and event.key == K_t:
                self.animating = False
                self.render()
            elif event.type == KEYDOWN and event.key == K_r:
                print()
                print("reset")
                self.startRender()
        return True

    def startRender(self):
        self.animating = False

        self.screen.fill(MazeWindow.WHITE)
        pygame.display.update()

        self.animations = []
        self.step_counter = 0

        if self.should_animate:
            self.drawEmptyMaze()
            self.animations.append(self.animateMaze())
        else:
            maze = self.maze_generator.generate()
            self.drawMaze(maze)
            if self.show_console:
                print_maze(maze)

    def render(self):
        for animation in self.animations:
            try:
                next(animation)
            except StopIteration:
                pass

    def drawEmptyMaze(self):
        # horizontal
        left = MazeWindow.PADDING
        top = MazeWindow.PADDING
        width = self.num_cells_horizontal * MazeWindow.CELL_SIZE
        height = MazeWindow.CELL_SIZE

        for _ in range(self.maze_generator.height + 1):
            pygame.draw.rect(
                self.screen, MazeWindow.BLACK, pygame.Rect(left, top, width, height),
            )
            top += 2 * MazeWindow.CELL_SIZE

        # vertical
        left = MazeWindow.PADDING
        top = MazeWindow.PADDING
        width = MazeWindow.CELL_SIZE
        height = self.num_cells_vertical * MazeWindow.CELL_SIZE

        for _ in range(self.maze_generator.width + 1):
            pygame.draw.rect(
                self.screen, MazeWindow.BLACK, pygame.Rect(left, top, width, height),
            )
            left += 2 * MazeWindow.CELL_SIZE

        pygame.display.update()

    def clearWallAbove(self, row, col):
        left = MazeWindow.PADDING + (2 * col + 1) * MazeWindow.CELL_SIZE
        top = MazeWindow.PADDING + (2 * row) * MazeWindow.CELL_SIZE
        width = MazeWindow.CELL_SIZE
        height = MazeWindow.CELL_SIZE

        pygame.draw.rect(
            self.screen, MazeWindow.WHITE, pygame.Rect(left, top, width, height)
        )

    def clearWallLeft(self, row, col):
        left = MazeWindow.PADDING + (2 * col) * MazeWindow.CELL_SIZE
        top = MazeWindow.PADDING + (2 * row + 1) * MazeWindow.CELL_SIZE
        width = MazeWindow.CELL_SIZE
        height = MazeWindow.CELL_SIZE

        pygame.draw.rect(
            self.screen, MazeWindow.WHITE, pygame.Rect(left, top, width, height)
        )

    def drawMazeRows(self, maze, start_row=0):
        for row in range(start_row, maze.height):
            for col in range(maze.width):
                if not maze.cells[row][col][CellIndex.SET_ID.value]:
                    break
                if not maze.cells[row][col][CellIndex.WALL_ABOVE.value]:
                    self.clearWallAbove(row, col)
                if not maze.cells[row][col][CellIndex.WALL_LEFT.value]:
                    self.clearWallLeft(row, col)

        pygame.display.update()

    def drawMazeExit(self, maze):
        side, row, col = maze.exit
        if side == "top" or side == "bottom":
            self.clearWallAbove(row, col)
        elif side == "left" or side == "right":
            self.clearWallLeft(row, col)
        pygame.display.update()

    def drawMaze(self, maze):
        print("draw", end="\r")
        self.drawEmptyMaze()
        self.drawMazeRows(maze)
        self.drawMazeExit(maze)

    def animateMaze(self):
        for frame in self.maze_generator.frames():
            start = time.perf_counter()
            print(f"frame {self.step_counter}", end="\r")
            self.step_counter += 1
            self.drawMazeRows(frame, frame.current_row)
            if self.show_console:
                print_maze(frame)
            yield
            while time.perf_counter() - start < MazeWindow.STEP_RATE:
                yield
        self.drawMazeExit(frame)
