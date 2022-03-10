import time
import pygame


class MazeWindow:
    SCREENSIZE = WIDTH, HEIGHT = 600, 400
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    POLLRATE = 0.01

    def show(self):
        pygame.init()
        pygame.display.set_caption("Maze")
        self.screen = pygame.display.set_mode(MazeWindow.SCREENSIZE)

        self.screen.fill(MazeWindow.WHITE)
        self.drawLine()
        pygame.display.update()

        while self.checkEvents():
            time.sleep(MazeWindow.POLLRATE)

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def drawLine(self):
        pygame.draw.line(
            self.screen,
            MazeWindow.BLACK,
            (0, MazeWindow.HEIGHT / 2),
            (MazeWindow.WIDTH, MazeWindow.HEIGHT / 2),
            2,
        )
