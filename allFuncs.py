import math
import tkinter as tk
from tkinter import Entry, Button, Checkbutton, BooleanVar
import pygame
import numpy as np
import loads

global members, active_member, GLOBAL_SCALE, set_initial_scale, GLOBAL_CENTER, HEIGHT, node_no, nodes

active_member = None
members = []
GLOBAL_SCALE = 1
GLOBAL_CENTER = (0, 0)
set_initial_scale = False
node_no = 1
nodes = []
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

SNAP_RADIUS = 20  # The radius for snapping in pixels
ANGLE_INCREMENT = 1  # The angle increment for drawing lines



def transfer_vars(scale, center, HEIGHT_):
    global GLOBAL_SCALE, GLOBAL_CENTER, HEIGHT
    HEIGHT = HEIGHT_
    GLOBAL_SCALE = scale
    GLOBAL_CENTER = center


class Node:
    def __init__(self, id, screen, _type="main", sub_id = 0):
        self.screen = screen
        self.id = id
        self.point = s2g(self.screen)
        self.support = None
        self.dof = []
        self.Fx = np.nan
        self.Fy = np.nan
        self.Mu = np.nan
        self.type = _type
        self.sub_id = sub_id
    
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
    
    def update_Reacts(self):
        if self.support == "Fix":
            self.Fx = "Rx"
            self.Fy = "Ry"
            self.Mu = "Mu"
        elif self.support == "Pin":
            self.Fx = "Rx"
            self.Fy = "Ry"
        elif self.support == "Roller":
            self.Fy = "Ry"

    def draw(self, screen):
        if self.support == "Fix":
            fix_rect = pygame.Rect(self.screen[0]-20, self.screen[1], 40, 20)
            pygame.draw.rect(screen, RED, fix_rect, 1)
        elif self.support == "Pin":
            vertices = [self.screen, (self.screen[0]-15, self.screen[1]+15), (self.screen[0]+15, self.screen[1]+15)]
            pygame.draw.polygon(screen, RED, vertices, 1)
        elif self.support == "Roller":
            pygame.draw.circle(screen, RED, (self.screen[0], self.screen[1]+10), 10, 1)
            pygame.draw.line(screen, RED, (self.screen[0]-10, self.screen[1]+20), (self.screen[0]+10, self.screen[1]+20))


    def sub_draw(self, screen):    
        pygame.draw.circle(screen, (255, 0, 0), self.screen, 3)
        pygame.draw.circle(screen, (0, 0, 0), self.screen, 3, 1)
        # Create a font
        font = pygame.font.Font(None, 20)

        # Render the text
        text_surface = font.render(f"{self.sub_id}", True, (0, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.midright = (self.screen)

        # Draw the text
        screen.blit(text_surface, text_rect)
    
        
class Member:
    def __init__(self, id, node1, node2, color, sub = False):
        self.id = id
        self.start_node = node1
        self.end_node = node2
        self.color = color
        self.A = 1
        self.E = 1
        self.I = 1
        self.calculate_length_and_angle()
        self.calculate_mid()
        self.point_forces = []
        self.dof = []
        self.FER = self.calculate_FER()
        self.sub_nodes = []
        self.sub_members = []
        self.sub = sub
    
    def calculate_mid(self):
        x_mid = (self.start_node.screen[0]+self.end_node.screen[0])/2
        y_mid = (self.start_node.screen[1]+self.end_node.screen[1])/2
        self.mid = (x_mid, y_mid)

    def calculate_length_and_angle(self):
        dx = self.end_node.point[0] - self.start_node.point[0]
        dy = self.end_node.point[1] - self.start_node.point[1]
        length = math.sqrt(dx ** 2 + dy ** 2)
        angle = math.degrees(math.atan2(dy, dx))
        self.length = length
        self.angle = angle

    def update_color(self, color):
        self.color = color
    
    def update_A(self, value):
        self.A = value
    
    def update_E(self, value):
        self.E = value
    
    def update_I(self, value):
        self.I = value

    def finalize_calcs(self):
        self.calc_transform_matrix()
        self.calc_k_matrix()
        self.stiffness = np.transpose(self.transform_matrix).dot(self.k_matrix).dot(self.transform_matrix)
        self.FER = self.calculate_FER()

    def calc_transform_matrix(self):
        l = math.cos(math.radians(self.angle))
        m = math.sin(math.radians(self.angle))
        matrix = [[l, m, 0, 0, 0, 0],
                  [-m, l, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0],
                  [0, 0, 0, l, m, 0],
                  [0, 0, 0, -m, l, 0],
                  [0, 0, 0, 0, 0, 1]]
        self.transform_matrix = np.matrix(matrix, dtype=float)
    
    def calc_k_matrix(self):
        ael = self.A * self.E / self.length
        eil3 = self.E * self.I / (self.length ** 3)
        eil2 = self.E * self.I / (self.length ** 2)
        eil = self.E * self.I / self.length
        k = [[ael, 0, 0, -ael, 0, 0],
             [0, 12 * eil3, 6 * eil2, 0, -12 * eil3, 6 * eil2],
             [0, 6 * eil2, 4 * eil, 0, -6 * eil2, 2 * eil],
             [-ael, 0, 0, ael, 0, 0],
             [0, -12 * eil3, -6 * eil2, 0, 12 * eil3, -6 * eil2],
             [0, 6 * eil2, 2 * eil, 0, -6 * eil2, 4 * eil]]
        self.k_matrix = np.matrix(k, dtype=float)

    def calculate_FER(self):
        def get_angle(f, m):
            ang = f - m
            if ang < 0:
                ang += 360
            return ang

        def transform_force(fy, fx):
            ang = np.degrees(np.arctan2(fx, fy))
            if ang < 0:
                ang += 360
            f = np.sqrt(fx**2 + fy **2)
            ang += self.angle
            ang = np.radians(ang)
            x, y = f * np.sin(ang), f * np.cos(ang)
            return x, y
        rax = 0
        ray = 0
        rbx = 0
        rby = 0
        ma = 0
        mb = 0
        #                                           0                         1                          2
        # point_forces.append([forces_df.iloc[i]['perp'], forces_df.iloc[i]['loc'], forces_df.iloc[i]['angle']])
        for force in self.point_forces:
            a, b = force.loc, self.length - force.loc
            f_angle = math.radians(get_angle(force.angle, self.angle))
            rax += force.mag * math.cos(f_angle) * b / self.length
            rbx += force.mag * math.cos(f_angle) * a / self.length
            ray += force.mag * math.sin(f_angle) * b / self.length
            rby += force.mag * math.sin(f_angle) * a / self.length
            ma +=  force.mag* math.sin(f_angle) * a * (b ** 2) / self.length ** 2
            mb +=  force.mag* math.sin(f_angle) * a ** 2 * b * -1 / self.length ** 2
        
        ray += (ma + mb) / self.length
        rby -= (ma + mb) / self.length

        rax, ray = transform_force(ray, rax)
        rbx, rby = transform_force(rby, rbx)

        self.FER = np.array([-rax, ray, ma, -rbx, rby, mb], dtype=float)
    

    def display_id(self, screen):
        # Create a font
        font = pygame.font.Font(None, 20)

        # Render the text
        text_surface = font.render(f"{self.id}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.midright = (self.mid)

        # Draw the text
        screen.blit(text_surface, text_rect)
    
    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.start_node.screen, self.end_node.screen, 2)

        if len(self.point_forces) > 0:
            for force in self.point_forces:
                force.draw(screen)
        # if len(self.sub_members) > 0:
        #     for member in self.sub_members:
        #         if member.sub:
        #             pygame.draw.line(screen, member.color, member.start_node.screen, member.end_node.screen, 2)

                    
        
        
    
def s2g(screen_pos):
    # Convert screen coordinates to global coordinates
    x, y = screen_pos
    global_x = (x - GLOBAL_CENTER[0]) / GLOBAL_SCALE
    global_y = ((y - GLOBAL_CENTER[1]) / GLOBAL_SCALE) * -1
    return global_x, global_y


def snap_to_existing_nodes(mouse_pos):
    global node_no
    for node in nodes:
        start_x, start_y = node.screen
        # Check if the mouse cursor is within SNAP_RADIUS pixels of any endpoint
        if math.sqrt((mouse_pos[0] - start_x) ** 2 + ((mouse_pos[1]) - start_y) ** 2) <= SNAP_RADIUS:
            return node, True

    # If no snapping occurred, return the original mouse position
    a = Node(node_no, mouse_pos)
    nodes.append(a)
    node_no += 1
    return a, False


def snap_to_existing_nodes_for_support(mouse_pos):
    for node in nodes:
        start_x, start_y = node.screen
        # Check if the mouse cursor is within SNAP_RADIUS pixels of any endpoint
        if math.sqrt((mouse_pos[0] - start_x) ** 2 + ((mouse_pos[1]) - start_y) ** 2) <= SNAP_RADIUS:
            return node, True

    # If no snapping occurred, return the original mouse position
    return mouse_pos, False

def calculate_length_and_angle(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.sqrt(dx ** 2 + dy ** 2)
    angle = math.degrees(math.atan2(dy, dx))
    return length, angle


def snap_to_45_degree_angle(start, end):
    # Calculate the length and angle from the start to end points
    length, angle = calculate_length_and_angle(start, end)
   
    # Calculate the nearest multiple of 45 degrees
    snapped_angle = round(angle / ANGLE_INCREMENT) * ANGLE_INCREMENT
   
    # Convert the snapped angle back to radians
    snapped_angle_rad = math.radians(snapped_angle)
   
    # Calculate the new end point based on the snapped angle
    new_dx = length * math.cos(snapped_angle_rad)
    new_dy = length * math.sin(snapped_angle_rad)
    snapped_end = (start[0] + new_dx, start[1] + new_dy)
   
    return snapped_end


def change_coordinates(pos):
    new_pos = (pos[0], HEIGHT - pos[1])
    return new_pos


def round_coordinates(pos):
    return (round(pos[0], 3), round(pos[1], 3))


def edit_members(active, _members):
    global members
    global active_member
    active_member = active
    members = _members
    # Create a new tkinter window each time Enter is pressed
    root = tk.Tk()
    root.title(f"Modify Member {active_member.id}")

    change_A = BooleanVar()
    change_A.set(False)

    change_E = BooleanVar()
    change_E.set(False)

    change_I = BooleanVar()
    change_I.set(False)

    label1 = tk.Label(root, text="Length:")
    label1.grid(row=0, column=0)
    entry1 = Entry(root)
    entry1.insert(0, f"{active_member.length}")
    entry1.grid(row=0, column=1)
    unit1 = tk.Label(root, text="Feet")
    unit1.grid(row=0, column=2)

    
    label2 = tk.Label(root, text="Angle:")
    label2.grid(row=1, column=0)
    entry2 = Entry(root)
    entry2.insert(0, f"{active_member.angle}")
    entry2.grid(row=1, column=1)
    unit2 = tk.Label(root, text="Degree")
    unit2.grid(row=1, column=2)

    label3 = tk.Label(root, text="Section Area:")
    label3.grid(row=2, column=0)
    entry3 = Entry(root)
    entry3.insert(0, f"{active_member.A}")
    entry3.grid(row=2, column=1)
    unit3 = tk.Label(root, text="in²")
    unit3.grid(row=2, column=2)

    checkbox_A = Checkbutton(root, text="Change All Members Area", variable=change_A)
    checkbox_A.grid(row=3, columnspan=3)

    label4 = tk.Label(root, text="Mod of Elasticity:")
    label4.grid(row=4, column=0)
    entry4 = Entry(root)
    entry4.insert(0, f"{active_member.E}")
    entry4.grid(row=4, column=1)
    
    checkbox_E = Checkbutton(root, text="Change All Members E", variable=change_E)
    checkbox_E.grid(row=5, columnspan=3)

    label5 = tk.Label(root, text="Moment of Inertia:")
    label5.grid(row=6, column=0)
    entry5 = Entry(root)
    entry5.insert(0, f"{active_member.I}")
    entry5.grid(row=6, column=1)
    
    checkbox_I = Checkbutton(root, text="Change All Members I", variable=change_I)
    checkbox_I.grid(row=7, columnspan=3)


    def update_length():
        global active_member
        new_length = entry1.get()
        new_angle = entry2.get()
        new_A = entry3.get()
        new_E = entry4.get()
        new_I = entry5.get()
        __length = float(new_length)
        __angle = float(new_angle)
        area = float(new_A)
        elas = float(new_E)
        iner = float(new_I)
        def get_new_point(startNode, _length, angle):
            start = startNode.screen
            start_x, start_y = start
            end_x = start_x + GLOBAL_SCALE * _length * math.cos(math.radians(angle))
            end_y = start_y - GLOBAL_SCALE * _length * math.sin(math.radians(angle))
            end_screen = (end_x, end_y)
            end_global = s2g(end_screen)
            return end_screen, end_global

        active_member.length = __length
        active_member.angle = __angle
        end_screen, end_global = get_new_point(active_member.start_node, active_member.length, active_member.angle)
        snapped = False
        for node in nodes:
            if node != active_member.end_node:
                start_x, start_y = node.screen
                if math.sqrt((end_screen[0] - start_x) ** 2 + ((end_screen[1]) - start_y) ** 2) <= SNAP_RADIUS:
                    active_member.end_node.screen = node.screen
                    active_member.end_node.point = node.point
                    snapped = True
                
        if not snapped:
            active_member.end_node.screen = end_screen
            active_member.end_node.point = end_global
        
        [member.calculate_length_and_angle() for member in members if member != active_member]
        [member.calculate_mid() for member in members]

        for member in members:
            if len(member.point_forces) >0:
                for force in member.point_forces:
                    if force.loc >= member.length:
                        force.loc = member.length
                    force.screen = calculate_force_point(member.start_node.screen, member.angle, force.loc)

        if change_A.get():
            [member.update_A(area) for member in members]
        else:
            active_member.update_A(area)
        
        if change_E.get():
            [member.update_E(elas) for member in members]
        else:
            active_member.update_E(elas)
        
        if change_I.get():
            [member.update_I(iner) for member in members]
        else:
            active_member.I = iner
            
        # except ValueError:
        #     pass
        root.destroy()  # Close the tkinter window

    button = Button(root, text="Update Member", command=update_length)
    button.grid(row=8, column=1)

    root.mainloop()  # Start the tkinter mainloop for this window


def add_point_forces(active, _members):
    global members
    global active_member
    active_member = active
    members = _members
    # Create a new tkinter window each time Enter is pressed
    root = tk.Tk()
    root.title(f"Add/Edit Point Force to Member {active_member.id}")


    label1 = tk.Label(root, text="Magnitude:")
    label1.grid(row=0, column=0)
    entry1 = Entry(root)
    # entry1.insert(0, f"{active_member.length}")
    entry1.insert(0, f"")
    entry1.grid(row=0, column=1)
    unit1 = tk.Label(root, text="N")
    unit1.grid(row=0, column=2)

    
    label2 = tk.Label(root, text="Angle:")
    label2.grid(row=1, column=0)
    entry2 = Entry(root)
    # entry2.insert(0, f"{active_member.angle}")
    entry2.insert(0, f"")
    entry2.grid(row=1, column=1)
    unit2 = tk.Label(root, text="Degree")
    unit2.grid(row=1, column=2)

    label3 = tk.Label(root, text="Distance from Point A:")
    label3.grid(row=2, column=0)
    entry3 = Entry(root)
    # entry3.insert(0, f"{active_member.A}")
    entry3.insert(0, f"")
    entry3.grid(row=2, column=1)
    unit3 = tk.Label(root, text="Feet")
    unit3.grid(row=2, column=2)

    def update_force():
        global active_member
        _magnitude = entry1.get()
        _angle = entry2.get()
        _distFromA = entry3.get()

        try:
            magnitude = round(float(_magnitude),3)
            angle = round(float(_angle),3)
            distFromA = round(float(_distFromA),3)
            no = len(active_member.point_forces)+1
            point_Of_Force = calculate_force_point(active_member.start_node.screen, active_member.angle, distFromA)
            active_member.point_forces.append(loads.Point_Force(no, active_member.start_node, angle, distFromA, magnitude, point_Of_Force))
            active_member.calculate_FER()

        except ValueError:
            pass
        root.destroy()  # Close the tkinter window

    button = Button(root, text="Add Force", command=update_force)
    button.grid(row=5, column=1)

    root.mainloop()  # Start the tkinter mainloop for this window

def calculate_force_point(start, angle, dist):
    x, y = start
    x += dist * math.cos(math.radians(angle)) * GLOBAL_SCALE
    y -= dist * math.sin(math.radians(angle)) * GLOBAL_SCALE

    return (x, y)

def pre_def():
    global nodes
    node1 = (500, 400)
    node2 = (500, 200)
    node3 = (700, 200)
    node4 = (700, 400)
    nodes = [Node(1, node1), Node(2, node2), Node(3, node3), Node(4, node4)]
    members = [Member(1, nodes[0], nodes[1], YELLOW), Member(2, nodes[1], nodes[2], YELLOW), Member(3, nodes[2], nodes[3], YELLOW)]
    for member in members:
        member.update_I(1e-4)
        member.update_E(2e11)
        member.update_A(0.05)
    
    point_Of_Force = calculate_force_point(members[1].start_node.screen, members[1].angle, 6)    
    members[1].point_forces.append(loads.Point_Force(1, members[1].start_node, -90, 6, 40, point_Of_Force))
    members[1].calculate_FER()
    members[0].start_node.support = "Fix"
    members[0].start_node.Fx = "Rx"
    members[0].start_node.Fy = "Ry"
    members[0].start_node.Mu = "Mu"
    members[2].end_node.support = "Fix"
    members[2].end_node.Fx = "Rx"
    members[2].end_node.Fy = "Ry"
    members[2].end_node.Mu = "Mu"
    return members