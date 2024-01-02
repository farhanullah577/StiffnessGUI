import pygame
import math

def draw_arc(coordinate, magnitude):
    x = coordinate[0] - 25
    y = coordinate[1] - 25
    # pygame.draw.circle(screen, black, coordinate, 5)
    angle = 90
    if magnitude >= 0:
        angle = 90
        arr = [(x+48, y+20), (x+53, y+30), (x+43, y+30)]
    else:
        angle = -90
        arr = [(x+35, y), (x+25, y+5), (x+25, y-5)]
    pygame.draw.arc(screen, black, (*(x, y), 50, 50), 90, 270, 1)
    pygame.draw.arc()
    # pygame.draw.arc(screen, black, (*(x, y), 50, 50), math.radians(angle), 0, width=1)
    # pygame.draw.polygon(screen, black, arr)

    # Create a font
    font = pygame.font.Font(None, 36)

    # Render the text
    text_surface = font.render(f"{magnitude}", True, black)
    text_rect = text_surface.get_rect()
    text_rect.midright = coordinate

    # Draw the text
    screen.blit(text_surface, text_rect)
    

pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Reload Icon")

# Set up colors
white = (255, 255, 255)
black = (0, 0, 0)

# Wait for the user to close the window
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        

    # Clear screen
    screen.fill(white)

    draw_arc((200, 200), -5)
    # Update display
    pygame.display.flip()

pygame.quit()
