from maze import EllerMazeGenerator, MazeWindow


def main():
    maze_generator = EllerMazeGenerator(15, 15)
    window = MazeWindow(maze_generator)
    window.show()


if __name__ == "__main__":
    main()
