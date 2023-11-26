import pygame
import math


class Point_Force:
    def __init__(self, no,reference_coordinate, angle, loc, mag, screen_point, color = (255, 0, 0)):
        self.no = no
        self.angle = angle
        self.loc = loc #Distance
        self.ref_coord = reference_coordinate
        self.screen = screen_point
        self.mag = mag
        self.arrow_length = 50
        self.color = color
        

    def pan(self, offset_x, offset_y):
        self.screen = (self.screen[0] + offset_x, self.screen[1] + offset_y)
    
    def zoomOut_coods(self, mouse_pos, d_scale):
        center_x = mouse_pos[0]
        center_y = mouse_pos[1]
        old_x = self.screen[0]
        old_y = self.screen[1]
        new_x = center_x - (center_x - old_x) / d_scale
        new_y = center_y - (center_y - old_y) / d_scale
        self.screen = (new_x, new_y)
    
    def zoomIn_coods(self, mouse_pos, d_scale):
        center_x = mouse_pos[0]
        center_y = mouse_pos[1]
        old_x = self.screen[0]
        old_y = self.screen[1]
        new_x = center_x - (center_x - old_x) * d_scale
        new_y = center_y - (center_y - old_y) * d_scale
        self.screen = (new_x, new_y)


    def draw(self, screen):
        arrow_head_width = 10

        # Calculate the start point for the arrow
        start_x = self.screen[0] - self.arrow_length * math.cos(math.radians(self.angle))
        start_y = self.screen[1] + self.arrow_length * math.sin(math.radians(self.angle))

        # Draw the arrow shaft
        pygame.draw.line(screen, self.color, (start_x, start_y), (self.screen[0], self.screen[1]), 1)

        # Draw the arrowhead
        angle_rad = math.radians(self.angle)
        pygame.draw.polygon(screen, self.color, [
            (self.screen[0], self.screen[1]),
            (self.screen[0] - arrow_head_width * math.cos(angle_rad - math.pi / 6), self.screen[1] + arrow_head_width * math.sin(angle_rad - math.pi / 6)),
            (self.screen[0] - arrow_head_width * math.cos(angle_rad + math.pi / 6), self.screen[1] + arrow_head_width * math.sin(angle_rad + math.pi / 6))
        ])

        # Create a font
        font = pygame.font.Font(None, 36)

        # Render the text
        text_surface = font.render(f"{self.mag}", True, self.color)
        text_rect = text_surface.get_rect()
        text_rect.midright = (start_x, start_y)

        # Draw the text
        screen.blit(text_surface, text_rect)