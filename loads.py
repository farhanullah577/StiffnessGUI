import pygame
import math

RED = (255, 0, 0)

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
        
class Dist_Load:
    def __init__(self, no, _type, start_mag, end_mag, angle, a_distance, b_distance, parent):
        self.no = no
        self.type = _type
        self.start_mag = start_mag
        self.end_mag = end_mag
        self.angle = angle
        self.a_distance = a_distance
        self.b_distance = b_distance
        self.parent = parent
        self.color = RED

    print('lol')
    
    def draw(self, screen, scale):
        start_arrow_length = 50
        end_arrow_length = 50
        if self.type == 'udl':
            start_arrow_length = 50
            end_arrow_length = 50
        if self.type == 'uvl':
            if self.start_mag > self.end_mag:
                start_arrow_length = 50
                end_arrow_length = 10
            else:
                start_arrow_length = 10
                end_arrow_length = 50
        
        dl = end_arrow_length - start_arrow_length
        start_x, start_y = self.parent.start_node.screen
        x_inc = scale * self.a_distance * math.cos(math.radians(self.parent.angle))
        start_x += x_inc
        y_inc = scale * self.a_distance * math.sin(math.radians(self.parent.angle))
        start_y -= y_inc
        no_of_divisions = 10
        increment = self.b_distance / no_of_divisions
        arrow_starts = [(start_x, start_y)]
        
        for i in range(1, no_of_divisions-1, 1):
            x = start_x + (i * increment * math.cos(math.radians(self.parent.angle))) * scale
            y = start_y - (i * increment * math.sin(math.radians(self.parent.angle))) * scale
            arrow_starts.append((x, y))
        
        
        for i in range(len(arrow_starts)):
            arrow_length = start_arrow_length + (dl / no_of_divisions) * i
            end_x, end_y = arrow_starts[i][0] + arrow_length * math.cos(math.radians(self.angle)), arrow_starts[i][1] - arrow_length * math.sin(math.radians(self.angle))
            pygame.draw.line(screen, self.color, arrow_starts[i], (end_x, end_y), 1)
            arrow_head_width = 5
            angle_rad = math.radians(self.angle)
            pygame.draw.polygon(screen, self.color, [
                (end_x, end_y),
                (end_x - arrow_head_width * math.cos(angle_rad - math.pi / 6), end_y + arrow_head_width * math.sin(angle_rad - math.pi / 6)),
                (end_x - arrow_head_width * math.cos(angle_rad + math.pi / 6), end_y + arrow_head_width * math.sin(angle_rad + math.pi / 6))
            ])    
            if self.type == 'udl':
                if i == 4:
                    # Create a font
                    font = pygame.font.Font(None, 36)
                    # Render the text
                    text_surface = font.render(f"{self.start_mag} N/ft", True, (255, 255, 255))
                    text_rect = text_surface.get_rect()
                    text_rect.center = (end_x + (arrow_length+5) * math.cos(math.radians(self.angle)), end_y - (arrow_length+5) * math.sin(math.radians(self.angle)))
                    # Draw the text
                    screen.blit(text_surface, text_rect)
            elif self.type == 'uvl':
                if i == 0:
                    # Create a font
                    font = pygame.font.Font(None, 36)
                    # Render the text
                    text_surface = font.render(f"{self.start_mag} N/ft", True, (255, 255, 255))
                    text_rect = text_surface.get_rect()
                    text_rect.center = (end_x + (arrow_length+5) * math.cos(math.radians(self.angle)), end_y - (arrow_length+5) * math.sin(math.radians(self.angle)))
                    # Draw the text
                    screen.blit(text_surface, text_rect)
                if i == len(arrow_starts)-1:
                    # Create a font
                    font = pygame.font.Font(None, 36)
                    # Render the text
                    text_surface = font.render(f"{self.end_mag} N/ft", True, (255, 255, 255))
                    text_rect = text_surface.get_rect()
                    text_rect.center = (end_x + (arrow_length+5) * math.cos(math.radians(self.angle)), end_y - (arrow_length+5) * math.sin(math.radians(self.angle)))
                    # Draw the text
                    screen.blit(text_surface, text_rect)
                       
        