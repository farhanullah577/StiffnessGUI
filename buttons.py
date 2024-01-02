import pygame
import math

BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MENUBAR_COLOR = (55, 55, 55)
MENUBAR_TEXT_COLOR = (115, 115, 115)
MENUBAR_HOVER_COLOR = (75, 75, 75)


class Main_Button:
    def __init__(self, text, x, y, width=50, height=20, color = MENUBAR_COLOR):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = color
        self.text = text
        self.mid = calc_mid(self.x, self.y, self.width, self.height)
        self.sub_buttons = []
        self.state = "close"
        self.hover = False
            
    def click(self):
        if self.state == "open":
            self.state = "close"
        else:
            self.state = "open"


    def draw(self, screen):
        font_color = MENUBAR_TEXT_COLOR
        if self.state == "open":
            self.color = (255, 0, 0)
            font_color = YELLOW
        else:
            if self.hover:
                self.color = MENUBAR_HOVER_COLOR
            else:
                self.color = MENUBAR_COLOR
        
            
        pygame.draw.rect(screen, self.color, self.rect)        
        # pygame.draw.rect(screen, BLACK, self.rect, 5)
        # Create a font
        font = pygame.font.Font(None, 18)

        # Render the text
        text_surface = font.render(self.text, True, font_color)
        text_rect = text_surface.get_rect()
        text_rect.center = self.mid

        # Draw the text
        screen.blit(text_surface, text_rect)


class Sub_Button:
    def __init__(self, text, x, y, start_y, parent, width=50, height=20, color=(0, 0, 0)):
        self.x = x
        self.max_y = y
        self.parent = parent
        self.start_y = start_y
        self.y = start_y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = color
        self.text = text
        self.mid = calc_mid(self.x, self.y, self.width, self.height)
        self.status = False
        self.selected = False
    
    # sub_button_texts = [["Draw", "Edit"],["Fix", "Pin", "Roller"],["Point", "UDL", "UVL", "Moment"],["Run"]]
    #Sub button Clicks
    def click(self):
        if self.text == "Draw":
            return 1
        elif self.text == "Edit":
            return 2
        
        
    def update_open(self, screen):
        if self.parent.state == "open":
            if self.y <= self.max_y:
                self.y += 2
                self.mid = calc_mid(self.x, self.y, self.width, self.height) 
                self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.draw(screen)
    
    def update_close(self, screen):
        if self.parent.state == "close":
            if self.y >= self.start_y:
                self.y -= 2
                self.mid = calc_mid(self.x, self.y, self.width, self.height) 
                self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.draw(screen)
        
        
    def draw(self, screen):
        if self.y != self.parent.y:
            color = YELLOW
            if self.status:
                color == YELLOW
            if not self.status:
                color = (140, 140, 140)
            if self.selected:
                color = (255, 0, 0)
            pygame.draw.rect(screen, color, self.rect)
            
            # Create a font
            font = pygame.font.Font(None, 17)

            # Render the text
            text_surface = font.render(self.text, True, self.color)
            text_rect = text_surface.get_rect()
            text_rect.center = self.mid

            # Draw the text
            screen.blit(text_surface, text_rect)
        
        
def calc_mid(x, y, width, height):
    x += width / 2
    y += height / 2
    return (x, y)       


