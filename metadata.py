import pygame
import sys
import math

class Dist_Force:
    def __init__(self, a, b, c, _type, screen_start, screen_end, angle, start_mag, end_mag):
        self.a = a
        self.b = b
        self.c = c
        self.type = _type
        self.start = screen_start
        self.end = screen_end
        self.angle = angle
        self.start_mag = start_mag
        self.end_mag = end_mag
        self.start_arrow_length, self.end_arrow_length = self.get_arrow_lenghts()
    
    def get_arrow_lenghts(self):
        if self.type == "udl":
            return 50, 50
        elif self.type == "uivl":
            return 30, 50
        elif self.type == "udvl":
            return 50, 30

    def draw(self, screen):
                

def draw_arrowhead_with_text(screen, color, point_x, point_y, angle, arrow_length=50, text="Tail"):
    arrow_head_width = 10

    # Calculate the start point for the arrow
    start_x = point_x - arrow_length * math.cos(math.radians(angle))
    start_y = point_y + arrow_length * math.sin(math.radians(angle))

    # Draw the arrow shaft
    pygame.draw.line(screen, color, (start_x, start_y), (point_x, point_y), 1)

    # Draw the arrowhead
    angle_rad = math.radians(angle)
    pygame.draw.polygon(screen, color, [
        (point_x, point_y),
        (point_x - arrow_head_width * math.cos(angle_rad - math.pi / 6), point_y + arrow_head_width * math.sin(angle_rad - math.pi / 6)),
        (point_x - arrow_head_width * math.cos(angle_rad + math.pi / 6), point_y + arrow_head_width * math.sin(angle_rad + math.pi / 6))
    ])

    # Create a font
    font = pygame.font.Font(None, 36)

    # Render the text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midright = (start_x, start_y)

    # Draw the text
    screen.blit(text_surface, text_rect)

# Initialize Pygame
pygame.init()

# Set the screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the color, angle, and point for the arrowhead, and the text
arrow_color = (255, 0, 0)  # Red
arrow_angle = -90  # Angle in degrees
arrow_length = 50
arrow_point_x = 300
arrow_point_y = 300
text_to_display = "Arrow Tail"

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))  # Fill with black
    
    pygame.draw.line(screen, (255, 255, 255), (300, 300), (600, 300))

    # Draw the arrowhead with the arrowhead placed at the specified point and text
    # draw_arrowhead_with_text(screen, arrow_color, arrow_point_x, arrow_point_y, arrow_angle, arrow_length, text_to_display)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()