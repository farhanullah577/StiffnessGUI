import pygame
import math
from tkinter import messagebox
import allFuncs as aF
import calcs as cL
import support as sup
import numpy as np


# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (35, 35, 35)
MENUBAR_COLOR = (55, 55, 55)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
INFO_SCREEN_WIDTH = 250  # Width of the info screen
GREY = (220, 220, 220)
GLOBAL_SCALE = 10
offset_x = 0
offset_y = 0

global scene
scene = 1

GLOBAL_CENTER = (0, 0)
aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)

# Create the main screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
aF.screen = screen
pygame.display.set_caption("Structural Analysis by Me for Me")

# Create the info screen to the left
info_screen = pygame.Surface((INFO_SCREEN_WIDTH, HEIGHT))
info_screen.fill(GREY)

# Create fonts for text display
font = pygame.font.Font(None, 24)
font1 = pygame.font.Font(None, 21)
text_color = (0, 0, 0)

# Create a list to store instances of the Member class
members = []

# 2D array to store coordinates of lines
line_coordinates = []
all_nodes = []

# Variables to store start and end points
start_point = None
end_point = None
drawing = True  # Set to True initially to allow drawing

# Reaction Array
reactions = [] 

# Define Buttons of Support
support_types = ["Fix", "Pin", "Roller"]
button_spacing = 10
button_width = 50
button_height = 50
start_x = (INFO_SCREEN_WIDTH / 2) - (len(support_types) * button_width + (len(support_types) - 1) * button_spacing) / 2
start_y = (HEIGHT / 2) - (button_height / 2) 
buttons = []
for i in range(len(support_types)):
    buttons.append(sup.Support_Buttons(support_types[i], start_x, start_y, button_width, button_height))
    start_x += button_width + button_spacing

button_text = ["Member", "Support", "Loads", "Analysis"]
sub_button_texts = [["Draw", "Edit"],["Fix", "Pin", "Roller", "None"],["Point", "UDL", "UVL", "Moment"],["Run", "Reset"]]
main_buttons = aF.make_buttons(button_text, sub_button_texts)

global active_member, active_node, node_no

def check_status(button):
    text = button.text
                
    if text == "Draw":
        button.status = True
    elif text in ["Edit", "Fix", "Pin", "Roller"]:
        if len(members) > 0:
            button.status = True
        else:
            button.status = False
    elif text == "None":
        support_found = False
        for node in aF.nodes:
            if node.support != None:
                support_found = True
        if support_found:
            button.status = True
        else:
            button.status = False
            button.selected = False
    elif text == "Fix":
        if active_node == None:
            button.status = False
        else:
            button.status = True
    elif text in ["Point", "UDL", "UVL", "Moment"]:
        if len(members) > 0:
            button.status = True
        else:
            button.status = False
    elif text == "Run":
        if len(members) > 0:
            button.status = True
        else:
            button.status = False
        
        if calcs_done:
            button.status = False
    elif text == "Reset":
        if calcs_done:
            button.status = True
        else:
            button.status = False
    
    if scene == 999:
        if text != "Reset":
            button.status = False
        else:
            button.status = True    

def s2g(screen_pos):
    # Convert screen coordinates to global coordinates
    x, y = screen_pos
    global_x = (x - GLOBAL_CENTER[0]) / GLOBAL_SCALE
    global_y = ((y - GLOBAL_CENTER[1]) / GLOBAL_SCALE) * 1
    return global_x, global_y

def update_selected_button(text):
    for button in main_buttons:
        for sub_button in button.sub_buttons:
            if sub_button.text == text:
                sub_button.selected = True
            else:
                sub_button.selected = False


def update_del_button():
    global members, active_member
    
    if scene == 2 and active_member is not None:
        del_rect = pygame.Rect(WIDTH - 50, 30, 30, 30)
        pygame.draw.rect(screen, RED, del_rect)
        pygame.draw.rect(screen, YELLOW, del_rect, 2)
        pygame.draw.line(screen, BLACK, (WIDTH - 45, 35), (WIDTH - 25, 55), 3)
        pygame.draw.line(screen, BLACK, (WIDTH - 45, 55), (WIDTH - 25, 35), 3)
             
        
def update_info_screen():
    global active_member
    info_screen.fill(GREY)

    if scene == 1:
        [member.update_color(YELLOW) for member in members]
        text_line1 = font.render(f"Press space to", True, text_color)
        text_line2 = font.render(f"finish drawings", True, text_color)
        info_screen.blit(text_line1, (10, 10))
        info_screen.blit(text_line2, (10, 40))
    
    elif scene == 2:
        if active_member is None:
            for mem in members:
                 mem.update_color(YELLOW)
            text_line1 = font.render(f"Click any Member to edit.", True, text_color)
            info_screen.blit(text_line1, (10, 10))
    
        if active_member is not None:
            active_member.update_color(RED)
            info_text = f"Member {active_member.id}\nLength = {round(active_member.length, 3)}\nAngle = {round(active_member.angle, 0)}\nSection Area = {active_member.A}\nModulus of Elasticity = {active_member.E}\nMoment of Inertia = {active_member.I}\nStart no = {active_member.start_node.id}\nEnd no = {active_member.end_node.id}\nGlobal Start = {aF.round_coordinates(active_member.start_node.point)}\nGlobal End = {aF.round_coordinates(active_member.end_node.point)}\n\n\nPress Enter to edit.\n\nPress Backspace to \nReturn to Drawing"
            lines = info_text.split("\n")
            for i, line in enumerate(lines):
                text_line = font.render(line, True, text_color)
                info_screen.blit(text_line, (10, 10 + i * 30))
            return active_member
    
    elif scene == 3:
        if active_node is None:
            text_line1 = font.render(f"Click Any Node", True, text_color)
            info_screen.blit(text_line1, (10, 10))
            text_line2 = font.render(f"to Add Support.", True, text_color)
            info_screen.blit(text_line2, (10, 40))
        
        if active_node is not None:
            text_line1 = font.render(f"Add Support to ", True, text_color)
            info_screen.blit(text_line1, (10, 10))
            text_line2 = font.render(f"node {active_node.id}", True, text_color)
            info_screen.blit(text_line2, (10, 40))
            [button.draw(info_screen) for button in buttons]
            pygame.draw.circle(screen, RED, active_node.screen, 10)
            pygame.draw.circle(screen, BLACK, active_node.screen, 10, 2)
            
    
    elif scene == 4:
        if active_member is None:
            for mem in members:
                 mem.update_color(YELLOW)
            text_line1 = font.render(f"Click Any Member", True, text_color)
            info_screen.blit(text_line1, (10, 10))
            text_line2 = font.render(f"to Add Point Force.", True, text_color)
            info_screen.blit(text_line2, (10, 40))
    
        if active_member is not None:
            active_member.update_color(RED)
            info_text = f""
            if len(active_member.point_forces) > 0:
                for force in active_member.point_forces:
                    info_text += f"{force.no}. {force.mag} N at {force.angle} degree\n at {force.loc} ft from A.\n\n"
                lines = info_text.split("\n")
            else:
                info_text = f"No Point Forces Added to \nmember {active_member.id} yet."
                lines = info_text.split("\n")
            for i, line in enumerate(lines):
                text_line = font.render(line, True, text_color)
                info_screen.blit(text_line, (10, 10 + i * 30))
            
            return active_member
    
        
    elif scene == 100:
        text_line1 = font.render(f"Click Nodes to", True, text_color)
        info_screen.blit(text_line1, (10, 10))
        if selected_support == None:
            text_line2 = font.render(f"Remove Support.", True, text_color)
            info_screen.blit(text_line2, (10, 40))
        else:      
            text_line2 = font.render(f"Add {selected_support} Support.", True, text_color)
            info_screen.blit(text_line2, (10, 40))
    
        
    elif scene == 5000:
        if active_member is None:
            for mem in members:
                    mem.update_color(YELLOW)
            text_line1 = font.render(f"Click Any Member", True, text_color)
            info_screen.blit(text_line1, (10, 10))
            text_line2 = font.render(f"to Add UDL.", True, text_color)
            info_screen.blit(text_line2, (10, 40))
    
        if active_member is not None:
            active_member.update_color(RED)
            info_text = f""
            if len(active_member.udl) > 0:
                for force in active_member.udl:
                    info_text += f"{force.no}. {force.start_mag} N at {force.angle} degree\n from {force.a_distance} ft from A.\nto {force.b_distance}\n"
                lines = info_text.split("\n")
                
            else:
                info_text = f"No UDL Added to \nmember {active_member.id} yet."
                lines = info_text.split("\n")
            
            for i, line in enumerate(lines):
                text_line = font.render(line, True, text_color)
                info_screen.blit(text_line, (10, 10 + i * 30))
                
            
            return active_member
        
    elif scene == 6000:
        if active_member is None:
            for mem in members:
                    mem.update_color(YELLOW)
            text_line1 = font.render(f"Click Any Member", True, text_color)
            info_screen.blit(text_line1, (10, 10))
            text_line2 = font.render(f"to Add UVL.", True, text_color)
            info_screen.blit(text_line2, (10, 40))
    
        if active_member is not None:
            active_member.update_color(RED)
            info_text = f""
            if len(active_member.uvl) > 0:
                for force in active_member.uvl:
                    info_text += f"{force.no}. {force.start_mag} N/ft \nat {force.a_distance} ft from A\n to {force.end_mag} N/ft at {force.b_distance}\nat{force.angle} Degree"
                lines = info_text.split("\n")
            
            else:
                info_text = f"No UVL Added to \nmember {active_member.id} yet."
                lines = info_text.split("\n")
            
            for i, line in enumerate(lines):
                text_line = font.render(line, True, text_color)
                info_screen.blit(text_line, (10, 10 + i * 30))
            
            return active_member
        
    elif scene == 7000:
        if active_member is None:
            for mem in members:
                    mem.update_color(YELLOW)
            text_line1 = font.render(f"Click Any Member", True, text_color)
            info_screen.blit(text_line1, (10, 10))
            text_line2 = font.render(f"to Add Moment Force.", True, text_color)
            info_screen.blit(text_line2, (10, 40))
    
        if active_member is not None:
            active_member.update_color(RED)
            info_text = f""
            if len(active_member.moment) > 0:
                for force in active_member.moment:
                    info_text += f"{force.no}. {force.magnitude} N-ft at \n{force.loc} ft from A."
                lines = info_text.split("\n")
            else:
                info_text = f"No Moment Load Added to \nmember {active_member.id} yet."
                lines = info_text.split("\n")
                
            for i, line in enumerate(lines):
                text_line = font.render(line, True, text_color)
                info_screen.blit(text_line, (10, 10 + i * 30))
            
            return active_member
        
    elif scene == 999:
        active_member = None
        [mem.update_color(YELLOW) for mem in members]
        
        

def show_screen_name():
    line = f""
    if scene == 1:
        line = f"Draw Members."
    elif scene == 2:
        line = f"Edit Members"
    elif scene == 3:
        line = f"Add Supports to Nodes"
    elif scene == 4:
        line = f"Add Point Forces"
    elif scene == 5:
        line = f"Press space to Do Calculations"
    elif scene == 4:
        line = f"Select member and Press Enter to Add Point Force"
    elif scene == 5000:
        line = f"Select member and Press Enter to Add UDL"
    elif scene == 6000:
        line = f"Select member and Press Enter to Add UVL"
    elif scene == 7000:
        line = f"Select member and Press Enter to Add Moment Load"
        
    text_surface = font.render(line, True, RED)
    text_rect = text_surface.get_rect()
    text_rect.midright = (WIDTH, HEIGHT-5)
    screen.blit(text_surface, text_rect)


def g2s(global_pos):
    # Convert screen coordinates to global coordinates
    x, y = global_pos
    screen_x = (x - GLOBAL_CENTER[0]) * GLOBAL_SCALE
    screen_y = ((y - GLOBAL_CENTER[1]) * GLOBAL_SCALE) * 1
    return screen_x, screen_y


# Define variables for dragging
panning = False
offset = [0, 0]

calcs_done = False

# Support String
all_supports = []


# Fixed zoom center point
global zoom_center
zoom_center = (155, 350)
d_scale = 1.01

# Game loop
running = True
start = True
start_id = 1
active_member = None
active_node = None
selected_support = None
selected_load = None
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if drawing:
            if start:
                start = not start
        for button in main_buttons:
            button.hover = False
            if button.x <= pygame.mouse.get_pos()[0] <= button.x + button.width and button.y <= pygame.mouse.get_pos()[1] <= button.y + button.height:
                button.hover = True
        clicked = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in main_buttons:
                    if button.state == "open":
                        if button.text == "Support":
                            active_member = None
                        for sub_button in button.sub_buttons:
                            if sub_button.x <= event.pos[0] <= sub_button.x + sub_button.width and sub_button.y <= event.pos[1] <= sub_button.y + sub_button.height:
                                #Sub button clicks here
                                if sub_button.status:
                                    update_selected_button(sub_button.text)
                                    if sub_button.text in ["Draw"]:
                                        if sub_button.status:
                                            active_member = None
                                            scene = sub_button.click()
                                            clicked = True
                                    if sub_button.text in ["Edit"]:
                                        if sub_button.status:
                                            scene = sub_button.click()
                                            clicked = True
                                    elif sub_button.text in ["Fix", "Pin", "Roller", "None"]:
                                        if sub_button.text == "None":
                                            selected_support = None
                                        else:    
                                            selected_support = sub_button.text
                                        scene = 100
                                        active_member = None
                                        [member.update_color(YELLOW) for member in members]
                                    elif sub_button.text in ["Point", "UDL", "UVL", "Moment"]:
                                        selected_load = sub_button.text
                                        if selected_load == "Point":
                                            scene = 4
                                            clicked = True
                                        elif selected_load == "UDL":
                                            scene = 5000
                                            clicked = True
                                        elif selected_load == "UVL":
                                            scene = 6000
                                            clicked = True
                                        elif selected_load == "Moment":
                                            scene = 7000
                                            clicked = True
                                        
                                    elif sub_button.text == "Run":
                                        clicked = True
                                        sub_button.status = True
                                        aF.members = members
                                        if aF.check_definite([node.support for node in aF.nodes]):
                                            if not calcs_done:
                                                active_member = None
                                                scene = 999
                                                aF.GLOBAL_SCALE = GLOBAL_SCALE
                                                GLOBAL_CENTER = members[0].start_node.screen
                                                reactions = cL.calculations(aF.nodes, members, GLOBAL_CENTER, GLOBAL_SCALE)
                                                calcs_done = True
                                                    
                                        else:
                                            messagebox.showinfo("Error", "The Structure in indeterminate. Please Recheck Support Conditions.")
                                            clicked = True
                                    elif sub_button.text == "Reset":
                                        if calcs_done:
                                            clicked = True
                                            calcs_done = False
                                            scene = 1
                                            reactions = []
                                            for member in members:
                                                member.sub_members = []
                                                member.sub_nodes = []
                                                member.FER = np.array([0, 0, 0, 0, 0, 0], dtype=float)
                                            for node in aF.nodes:
                                                node.dof = []
                                                node.Fx = np.nan
                                                node.Fy = np.nan
                                                node.Mu = np.nan
                                                if node.support == "Fix":
                                                    node.Fx = "Rx"
                                                    node.Fy = "Ry"
                                                    node.Mu = "Mu"
                                                elif node.support == "Pin":
                                                    node.Fx = "Rx"
                                                    node.Fy = "Ry"
                                                elif node.support == "Roller":
                                                    node.Fy = "Ry"
                                                
                                else:
                                    clicked = True
                    button.state = "close"
                    if button.x <= event.pos[0] <= button.x + button.width and button.y <= event.pos[1] <= button.y + button.height:
                        button.state = "open"
                
                if scene == 2 and active_member is not None:
                    if WIDTH-50 <= pygame.mouse.get_pos()[0] <= WIDTH - 50 + 30 and 30 <= pygame.mouse.get_pos()[1] <= 30 + 30:
                        members.remove(active_member)
                        active_member = None
                        clicked = True
                
                if scene == 100:
                    node, snapped_node = aF.snap_to_existing_nodes_for_support(event.pos)
                    if snapped_node:
                        active_node = node
                    if active_node is not None:
                        active_node.support = None
                        active_node.support = selected_support
                        active_node.update_Reacts()
                        active_node = None
                        start_point = None
                        drawing = False
                
                        
                if scene == 1:
                    if not clicked:    
                        if drawing:
                            if start_point is None:
                                # Check if the mouse click is inside the info screen
                                if event.pos[0] < INFO_SCREEN_WIDTH or event.pos[1]<=25:
                                    continue
                                if start_id == 1:
                                    GLOBAL_CENTER = event.pos
                                    aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                                # Snap to existing points if within SNAP_RADIUS pixels
                                start_point, snapped = aF.snap_to_existing_nodes(event.pos)
                                
                                
                            else:
                                if event.pos[0] < INFO_SCREEN_WIDTH or event.pos[1]<=25:
                                    continue 
                                # Snap to existing points if within SNAP_RADIUS pixels
                                end_point, snapped = aF.snap_to_existing_nodes(event.pos)
                                # Calculate the length and angle between start and end points
                                length, angle = aF.calculate_length_and_angle(start_point.screen, end_point.screen)
                                # Snap the end point to the nearest 45-degree angle
                                end_point.screen = aF.snap_to_45_degree_angle(start_point.screen, end_point.screen)
                                # Append the line's coordinates to the 2D array
                                member = aF.Member(start_id, start_point, end_point, YELLOW)
                                members.append(member)
                                start_id += 1
                                start_point = None
                                end_point = None

                elif scene in [2, 4, 5000, 6000, 7000]:
                    [member.update_color(YELLOW) for member in members]
                    if event.pos[1] > 25:
                        last_click = pygame.mouse.get_pos()
                        if not clicked:
                            active_member = min(members, key=lambda member: math.dist(last_click, (member.mid[0], member.mid[1])))

            elif event.button == 2:
                x, y = event.pos
                panning = True
                offset[0] = x
                offset[1] = y

            elif event.button == 4:  # Scroll up to zoom in
                if len(members) > 0:
                    GLOBAL_SCALE *= d_scale
                    if not calcs_done:
                        [node.zoomIn_coods(event.pos, d_scale) for node in aF.nodes]
                        for member in members:
                            if len(member.point_forces) > 0:
                                [force.zoomIn_coods(event.pos, d_scale) for force in member.point_forces]
                            if len(member.moment) > 0:
                                [force.zoomIn_coods(event.pos, d_scale) for force in member.moment]
                            
                        GLOBAL_CENTER = members[0].start_node.screen
                        aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                    else:
                        #If sub members wala khata
                        # [node.zoomIn_coods(event.pos, d_scale) for node in cL.sub_nodes]
                        # for member in cL.sub_members:
                        #     if len(member.point_forces) > 0:
                        #         [force.zoomIn_coods(event.pos, d_scale) for force in member.point_forces]
                        # for member in members:
                        #     if len(member.point_forces) > 0:
                        #         [force.zoomIn_coods(event.pos, d_scale) for force in member.point_forces]
                        
                        # GLOBAL_CENTER = members[0].start_node.screen
                        # aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                        
                        #Else
                        [node.zoomIn_coods(event.pos, d_scale) for node in aF.nodes]
                        for member in members:
                            if len(member.point_forces) > 0:
                                [force.zoomIn_coods(event.pos, d_scale) for force in member.point_forces]
                        GLOBAL_CENTER = members[0].start_node.screen
                        aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                        
            elif event.button == 5:  # Scroll down to zoom out
                if len(members) > 0:
                    GLOBAL_SCALE /= d_scale
                    if not calcs_done:
                        [node.zoomOut_coods(event.pos, d_scale) for node in aF.nodes]
                        for member in members:
                            if len(member.point_forces) > 0:
                                [force.zoomOut_coods(event.pos, d_scale) for force in member.point_forces]
                            if len(member.moment) > 0:
                                [force.zoomOut_coods(event.pos, d_scale) for force in member.moment]
                        GLOBAL_CENTER = members[0].start_node.screen
                        aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                    else:
                        #If sub members wala khata
                        # [node.zoomOut_coods(event.pos, d_scale) for node in cL.sub_nodes]
                        # for member in cL.sub_members:
                        #     if len(member.point_forces) > 0:
                        #         [force.zoomOut_coods(event.pos, d_scale) for force in member.point_forces]
                        # for member in members:
                        #     if len(member.point_forces) > 0:
                        #         [force.zoomOut_coods(event.pos, d_scale) for force in member.point_forces]
                        # GLOBAL_CENTER = members[0].start_node.screen
                        # aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                        
                        #Else
                        [node.zoomOut_coods(event.pos, d_scale) for node in aF.nodes]
                        for member in members:
                            if len(member.point_forces) > 0:
                                [force.zoomOut_coods(event.pos, d_scale) for force in member.point_forces]
                        GLOBAL_CENTER = members[0].start_node.screen
                        aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                    

        elif event.type == pygame.MOUSEMOTION:
            if not calcs_done:
                if panning and len(members) > 0:
                    x, y = event.pos
                    offset_x = x - offset[0]
                    offset_y = y - offset[1]
                    offset = [x, y]
                    [node.pan(offset_x, offset_y) for node in aF.nodes]
                    for member in members:
                        if len(member.point_forces) > 0:
                            [force.pan(offset_x, offset_y) for force in member.point_forces]
                        if len(member.moment) > 0:
                            [force.pan(offset_x, offset_y) for force in member.moment]
                    GLOBAL_CENTER = members[0].start_node.screen
                    [member.calculate_mid() for member in members]
            else:
                if panning and len(members) > 0:
                    #If submembers wala khata
                    # x, y = event.pos
                    # offset_x = x - offset[0]
                    # offset_y = y - offset[1]
                    # offset = [x, y]
                    # [node.pan(offset_x, offset_y) for node in cL.sub_nodes]
                    # [member.calculate_mid() for member in cL.sub_members]
                    # [member.calculate_mid() for member in members]
                    # for member in cL.sub_members:
                    #     if len(member.point_forces) > 0:
                    #         [force.pan(offset_x, offset_y) for force in member.point_forces]
                    # for member in members:
                    #     if len(member.point_forces) > 0:
                    #         [force.pan(offset_x, offset_y) for force in member.point_forces]
                    # GLOBAL_CENTER = members[0].start_node.screen
                    # [member.calculate_mid() for member in cL.sub_members]
                    
                    #Else
                    x, y = event.pos
                    offset_x = x - offset[0]
                    offset_y = y - offset[1]
                    offset = [x, y]
                    [node.pan(offset_x, offset_y) for node in aF.nodes]
                    for member in members:
                        if len(member.point_forces) > 0:
                            [force.pan(offset_x, offset_y) for force in member.point_forces]
                        if len(member.moment) > 0:
                            [force.pan(offset_x, offset_y) for force in member.moment]
                    GLOBAL_CENTER = members[0].start_node.screen
                    [member.calculate_mid() for member in members]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                panning = False

        elif event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_DELETE:
                if active_member is not None and scene == 2:
                    members.remove(active_member)
                    active_member = None

            if event.key == pygame.K_RETURN:
                if scene == 1:
                    continue
                if scene == 2:
                    if active_member is not None: 
                        aF.edit_members(active_member, members)
                if scene == 4:
                    if active_member is not None:
                        aF.add_point_forces(active_member, members)
                if scene == 5000:
                    if active_member is not None:
                        aF.add_udl(active_member, members)
                if scene == 6000:
                    if active_member is not None:
                        aF.add_uvl(active_member, members)
                if scene == 7000:
                    if active_member is not None:
                        aF.add_moment(active_member, members)
                    
                    
            elif event.key == pygame.K_ESCAPE:
                
                if scene == 1:
                    if  start_point:
                        if not snapped:
                            aF.node_no -= 1
                            aF.nodes.remove(start_point)
                        start_point = None
                        
                        
                elif scene in [2, 3, 4]:
                    active_member = None

            elif event.key == pygame.K_BACKSPACE:
                cL.reset(members)
                calcs_done = False
                if scene == 1:
                    pass
                elif scene == 2:
                    scene -= 1
                    active_member = None
                    drawing = True
                else:
                    active_member = None
                    active_node = None
                    scene -= 1
            
            elif event.key == pygame.K_F1:
                members = aF.pre_def()
                
            elif event.key == pygame.K_F2:
                members = aF.pre_def2()
                aF.GLOBAL_SCALE = GLOBAL_SCALE
                # reactions = cL.calculations(aF.nodes, members)
                # scene = 999
                # calcs_done = True
            
                

    # Clear the main screen
    screen.fill(BACKGROUND_COLOR)
    #menubar
    menubar_rect = pygame.Rect(0, 0, WIDTH, 25)
    
    for button in main_buttons:
        for s_button in button.sub_buttons:
            s_button.update_open(screen)
            s_button.update_close(screen)
    pygame.draw.rect(screen, MENUBAR_COLOR, menubar_rect)
    
    [button.draw(screen) for button in main_buttons]
    
    # Draw lines on the main screen
    if not calcs_done:
        [member.draw(screen) for member in members]
        [node.draw(screen) for node in aF.nodes]
    else:
        if scene == 999:
            [member.draw(screen) for member in members]
            [node.draw(screen) for node in aF.nodes]
            if len(reactions) > 0:
                [reaction.draw(screen) for reaction in reactions]
            if scene != 999:
                calcs_done = False
    
    if active_member is not None:
        # Create a font
        _font = pygame.font.Font(None, 25)
        # Render Node A
        A_text_surface = _font.render("A", True, BLACK)
        A_text_rect = A_text_surface.get_rect()
        A_text_rect.center = active_member.start_node.screen
        pygame.draw.circle(screen, YELLOW, active_member.start_node.screen, 10)
        pygame.draw.circle(screen, RED, active_member.start_node.screen, 10, 1)
        # Draw the text
        screen.blit(A_text_surface, A_text_rect)
        
        # Render Node B
        B_text_surface = _font.render("B", True, BLACK)
        B_text_rect = B_text_surface.get_rect()
        B_text_rect.center = active_member.end_node.screen
        pygame.draw.circle(screen, YELLOW, active_member.end_node.screen, 10)
        pygame.draw.circle(screen, RED, active_member.end_node.screen, 10, 1)
        # Draw the text
        screen.blit(B_text_surface, B_text_rect)
        

    # Draw the current line (if still drawing)
    if start_point is not None and drawing:
        end_pos = pygame.mouse.get_pos()
        end_pos = aF.snap_to_45_degree_angle(start_point.screen, end_pos)
        pygame.draw.line(screen, BLUE, start_point.screen, end_pos, 2)
    
       
    # Blit the info screen onto the main screen
    screen.blit(info_screen, (0, 0))
    update_info_screen()
    show_screen_name()
    update_del_button()
    
    for button in main_buttons:
        for sub_button in button.sub_buttons:
            check_status(sub_button)
    # Update the display
    pygame.display.flip()


# Quit Pygame
pygame.quit()
