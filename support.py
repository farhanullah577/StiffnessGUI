import pygame
BLACK = (0, 0, 0)

class Support_Buttons:
    def __init__(self, support, x, y, width=50, height=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.support = support

    def draw(self, info_screen):
        pygame.draw.rect(info_screen, BLACK, self.rect, 5)