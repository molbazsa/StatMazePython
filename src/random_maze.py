from eller_algorithm import eller_maze


def main():
    maze = eller_maze(15, 15)

    print(maze.walls)

    BLOCK = 3 * "█"
    SPACE = 3 * " "
    for row in maze.walls:
        for col in row:
            if col:
                print(BLOCK, end="")
            else:
                print(SPACE, end="")
        print()


if __name__ == "__main__":
    main()
