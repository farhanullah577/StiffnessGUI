import pygame
import math
import allFuncs as aF
import calcs as cL
import support as sup


# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (35, 35, 35)
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
pygame.display.set_caption("Structural Analysis by Me for Me")

# Create the info screen to the left
info_screen = pygame.Surface((INFO_SCREEN_WIDTH, HEIGHT))
info_screen.fill(GREY)

# Create fonts for text display
font = pygame.font.Font(None, 24)
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

global active_member, active_node, node_no

def s2g(screen_pos):
    # Convert screen coordinates to global coordinates
    x, y = screen_pos
    global_x = (x - GLOBAL_CENTER[0]) / GLOBAL_SCALE
    global_y = ((y - GLOBAL_CENTER[1]) / GLOBAL_SCALE) * 1
    return global_x, global_y


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
            for force in active_member.point_forces:
                info_text += f"{force.no}. {force.mag} N at {force.angle} degree\n at {force.loc} ft from A.\n\n"
            lines = info_text.split("\n")
            for i, line in enumerate(lines):
                text_line = font.render(line, True, text_color)
                info_screen.blit(text_line, (10, 10 + i * 30))
            
            return active_member

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
    text_line = font.render(line, True, RED)
    screen.blit(text_line, (INFO_SCREEN_WIDTH+10, 10))


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
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if drawing:
            if start:
                start = not start
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if scene == 1:
                    if drawing:
                        if start_point is None:
                            # Check if the mouse click is inside the info screen
                            if event.pos[0] < INFO_SCREEN_WIDTH:
                                continue
                            if start_id == 1:
                                GLOBAL_CENTER = event.pos
                                aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                            # Snap to existing points if within SNAP_RADIUS pixels
                            start_point, snapped = aF.snap_to_existing_nodes(event.pos)
                            
                            
                        else:
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

                elif scene in [2, 4]:
                    [member.update_color(YELLOW) for member in members]
                    last_click = pygame.mouse.get_pos()
                    active_member = min(members, key=lambda member: math.dist(last_click, (member.mid[0], member.mid[1])))

                elif scene == 3:
                    active_member = None
                    [member.update_color(YELLOW) for member in members]
                    node, snapped_node = aF.snap_to_existing_nodes_for_support(event.pos)
                    if snapped_node:
                        active_node = node
                    if active_node is not None:
                        active_node.support = None
                        for button in buttons:
                            if button.x <= event.pos[0] <= button.x + button.width and button.y <= event.pos[1] <= button.y + button.height:
                                active_node.support = button.support
                                active_node.update_Reacts()
                                active_node = None

            elif event.button == 2:
                x, y = event.pos
                panning = True
                offset[0] = x
                offset[1] = y

            elif event.button == 4:  # Scroll up to zoom in
                GLOBAL_SCALE *= d_scale
                if not calcs_done:
                    [node.zoomIn_coods(event.pos, d_scale) for node in aF.nodes]
                    for member in members:
                        if len(member.point_forces) > 0:
                            [force.zoomIn_coods(event.pos, d_scale) for force in member.point_forces]
                    GLOBAL_CENTER = members[0].start_node.screen
                    aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                else:
                    [node.zoomIn_coods(event.pos, d_scale) for node in cL.sub_nodes]
                    for member in cL.sub_members:
                        if len(member.point_forces) > 0:
                            [force.zoomIn_coods(event.pos, d_scale) for force in member.point_forces]
                    for member in members:
                        if len(member.point_forces) > 0:
                            [force.zoomIn_coods(event.pos, d_scale) for force in member.point_forces]
                    
                    GLOBAL_CENTER = members[0].start_node.screen
                    aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                    

            elif event.button == 5:  # Scroll down to zoom out
                GLOBAL_SCALE /= d_scale
                if not calcs_done:
                    [node.zoomOut_coods(event.pos, d_scale) for node in aF.nodes]
                    for member in members:
                        if len(member.point_forces) > 0:
                            [force.zoomOut_coods(event.pos, d_scale) for force in member.point_forces]
                    GLOBAL_CENTER = members[0].start_node.screen
                    aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                else:
                    [node.zoomOut_coods(event.pos, d_scale) for node in cL.sub_nodes]
                    for member in cL.sub_members:
                        if len(member.point_forces) > 0:
                            [force.zoomOut_coods(event.pos, d_scale) for force in member.point_forces]
                    for member in members:
                        if len(member.point_forces) > 0:
                            [force.zoomOut_coods(event.pos, d_scale) for force in member.point_forces]
                    GLOBAL_CENTER = members[0].start_node.screen
                    aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                    

        elif event.type == pygame.MOUSEMOTION:
            # print(event.pos)
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
                    GLOBAL_CENTER = members[0].start_node.screen
                    [member.calculate_mid() for member in members]
            else:
                if panning:
                    x, y = event.pos
                    offset_x = x - offset[0]
                    offset_y = y - offset[1]
                    offset = [x, y]
                    
                    [node.pan(offset_x, offset_y) for node in cL.sub_nodes]
                    [member.calculate_mid() for member in cL.sub_members]
                    [member.calculate_mid() for member in members]
                    for member in cL.sub_members:
                        if len(member.point_forces) > 0:
                            [force.pan(offset_x, offset_y) for force in member.point_forces]
                    for member in members:
                        if len(member.point_forces) > 0:
                            [force.pan(offset_x, offset_y) for force in member.point_forces]
                    GLOBAL_CENTER = members[0].start_node.screen
                    [member.calculate_mid() for member in cL.sub_members]
                            
                        
                    

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                aF.transfer_vars(GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT)
                panning = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # print(f"scene {scene}")
                if scene == 1:
                    scene += 1
                    drawing = not drawing  # Toggle drawing bool
                elif scene == 2:
                    active_member = None
                    for member in members:
                        [member.update_color(YELLOW) for member in members]
                    scene += 1
                elif scene == 3:
                    for member in members:
                        if member.angle < 0:
                            member.angle += 360
                        # member.finalize_calcs()
                    active_member = None
                    # [member.finalize_calcs() for member in members]
                    scene += 1
                elif scene == 4:
                    active_member = None
                    scene += 1
                elif scene == 5:
                    if not calcs_done:
                        active_member = None
                        reactions = cL.calculations(aF.nodes, members)
                        calcs_done = True
                        # [print(f"Node {node.sub_id} support {node.support}") for node in cL.sub_nodes]
                    
                                        
            elif event.key == pygame.K_RETURN:
                if scene == 1:
                    continue
                if scene == 2:
                    if active_member is not None: 
                        aF.edit_members(active_member, members)
                if scene == 4:
                    if active_member is not None:
                        aF.add_point_forces(active_member, members)
                    
                    
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
            
                

    # Clear the main screen
    screen.fill(BACKGROUND_COLOR)

    # Draw lines on the main screen
    if not calcs_done:
        [member.draw(screen) for member in members]
        [node.draw(screen) for node in aF.nodes]
    else:
        if len(cL.sub_members) > 0:
            [member.draw(screen) for member in cL.sub_members]
        if len(reactions) > 0:
            [reaction.draw(screen) for reaction in reactions]
        if len(cL.sub_nodes) > 0:
            [node.draw(screen) for node in cL.sub_nodes]
        if len(reactions) > 0:
            [reaction.draw(screen) for reaction in reactions]
    
    # Draw the current line (if still drawing)
    if start_point is not None and drawing:
        end_pos = pygame.mouse.get_pos()
        end_pos = aF.snap_to_45_degree_angle(start_point.screen, end_pos)
        pygame.draw.line(screen, BLUE, start_point.screen, end_pos, 2)

    
    # Blit the info screen onto the main screen
    screen.blit(info_screen, (0, 0))
    update_info_screen()
    show_screen_name()
    # Update the display
    pygame.display.flip()


# Quit Pygame
pygame.quit()


def goodFunction():
    print("Nice")