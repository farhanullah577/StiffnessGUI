import numpy as np
import pandas as pd
import loads
import math
import pygame
import allFuncs as aF
import random

global sub_nodes, sub_members
sub_nodes = []
sub_members = []  


class Reaction:
    def __init__(self, _type, magnitude, node):
        self.type = _type
        self.magnitude = round(magnitude,3)
        self.node = node      
        self.color = (0, 255, 0)
        self.arrow_length = 50
        # self.shape = self.def_shape()

    def draw_arc(self, screen):
        green = (0, 255, 0)
        x = self.node.screen[0] - 25
        y = self.node.screen[1] - 25
        pygame.draw.arc(screen, green, (*(x, y), 50, 50), math.radians(90), 0, width=1)
        # pygame.draw.circle(screen, black, coordinate, 5)
        if self.magnitude >= 0:
            arr = [(x+48, y+20), (x+53, y+30), (x+43, y+30)]
            text_loc = (self.node.screen[0]+50, self.node.screen[1]-25)
        else:
            arr = [(x+35, y), (x+25, y+5), (x+25, y-5)]
            text_loc = (self.node.screen[0]+70, self.node.screen[1]-25)
        pygame.draw.polygon(screen, green, arr)

        # Create a font
        font = pygame.font.Font(None, 25)

        # Render the text
        text_surface = font.render(f"{self.magnitude}", True, green)
        text_rect = text_surface.get_rect()
        text_rect.midright = text_loc


        # Draw the text
        screen.blit(text_surface, text_rect)

    def get_angle(self):
        if self.type == "Rx": 
            if self.magnitude >= 0:
                angle = 0
            else:
                angle = 180
        elif self.type == "Ry":
            if self.magnitude >= 0:
                angle = 90
            else:
                angle = 270
        elif self.type == "Mu":
            angle = 45
        
        return angle

    def draw(self, screen):
        if self.type == "Rx" or "Ry":
            angle = self.get_angle()
            if angle != 45:
                arrow_head_width = 10

                # Calculate the start point for the arrow
                start_x = self.node.screen[0] - self.arrow_length * math.cos(math.radians(angle))
                start_y = self.node.screen[1] + self.arrow_length * math.sin(math.radians(angle))

                # Draw the arrow shaft
                pygame.draw.line(screen, self.color, (start_x, start_y), (self.node.screen[0], self.node.screen[1]), 1)

                # Draw the arrowhead
                angle_rad = math.radians(angle)
                pygame.draw.polygon(screen, self.color, [
                    (self.node.screen[0], self.node.screen[1]),
                    (self.node.screen[0] - arrow_head_width * math.cos(angle_rad - math.pi / 6), self.node.screen[1] + arrow_head_width * math.sin(angle_rad - math.pi / 6)),
                    (self.node.screen[0] - arrow_head_width * math.cos(angle_rad + math.pi / 6), self.node.screen[1] + arrow_head_width * math.sin(angle_rad + math.pi / 6))
                ])

                # Create a font
                font = pygame.font.Font(None, 25)

                # Render the text
                text_surface = font.render(f"{self.magnitude}", True, self.color)
                text_rect = text_surface.get_rect()
                text_rect.midright = (start_x, start_y)
                if angle == 180:
                    text_rect.midleft = (start_x, start_y)

                # Draw the text
                screen.blit(text_surface, text_rect)
        if self.type == "Mu":
            self.draw_arc(screen)


def find_sub_coods(member, node_arr):
    global sub_nodes, sub_members
    scale = aF.GLOBAL_SCALE
    no_of_divisions = 4
    increment = member.length / no_of_divisions
    member.sub_nodes.append(member.start_node)
    for i in range(1, no_of_divisions):
        start_x, start_y = member.start_node.screen
        x = start_x + (i * increment * math.cos(math.radians(member.angle))) * scale
        y = start_y - (i * increment * math.sin(math.radians(member.angle))) * scale
        member.sub_nodes.append(aF.Node(0, (x, y), "sub"))
    member.sub_nodes.append(member.end_node)

        

def develop_sub_nodes(node_arr, member_arr):
    global sub_nodes, sub_members 
    for member in member_arr:
        find_sub_coods(member, node_arr)
        for node in member.sub_nodes:
            if node not in sub_nodes:
                sub_nodes.append(node)
    for i in range(len(sub_nodes)):
        sub_nodes[i].sub_id = i+1
        
def sub_point_forces(member):
    for force in member.point_forces:
        sub_length = member.sub_members[0].length
        sub_mem_num_4_force = int(force.loc / len(member.sub_members))
        loc = force.loc - (sub_mem_num_4_force * sub_length)
        # point_Of_Force = aF.calculate_force_point(member.sub_members[sub_mem_num_4_force].start_node.screen, member.sub_members[sub_mem_num_4_force].angle, loc)
        member.sub_members[sub_mem_num_4_force].point_forces.append(loads.Point_Force(force.no, member.sub_members[sub_mem_num_4_force].start_node, force.angle, loc, force.mag, force.screen, member.sub_members[sub_mem_num_4_force].color))
        
        
        
def develop_sub_members(members):
    global sub_members
    sub_mem_id = 1
    for member in members:
        for i in range(len(member.sub_nodes) - 1):
            sub_member = aF.Member(sub_mem_id, member.sub_nodes[i], member.sub_nodes[i+1], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), sub=True)
            member.sub_members.append(sub_member)
            sub_mem_id += 1
            sub_members.append(sub_member)
        sub_point_forces(member)

def reset(members):
    global sub_nodes, sub_members
    sub_members = []
    sub_nodes = []
    for member in members:
        member.sub_members = []

def calculations(nodes, members):
    global sub_nodes, sub_members
    
    reset(members)
    
    # develop_sub_nodes(nodes, members)
    # develop_sub_members(members)`
    
    # [print(f"sub member {member.id} \nstart node {member.start_node.sub_id} \nend node {member.end_node.sub_id} \nlength {member.length} \nAngle {member.angle}") for member in sub_members]
    # [member.finalize_calcs() for member in sub_members]
    [member.finalize_calcs() for member in members]
    # nodes = sub_nodes
    # members = sub_members
    dof = 1
    allDel = []
    for node in nodes:
        node.dof = [dof, dof+1, dof+2]
        allDel += node.dof
        dof += 3
    
    str_stiffness = np.matrix([[0] * len(allDel)] * len(allDel), dtype=float)

    for member in members:
        new = np.matrix([[0] * len(allDel)] * len(allDel), dtype=float)
        deltasArr = member.start_node.dof + member.end_node.dof
        member.dof = deltasArr
        
        row = 0
        for j in deltasArr:
            col = 0
            for k in deltasArr:
                new[j - 1, k - 1] = member.stiffness[row, col]
                y = pd.DataFrame(new)
                col += 1
            row += 1
        # print(f"new = {new}")
        str_stiffness += new
        str_stiffness = np.matrix(str_stiffness)
    
    # print(f"str_stiffness = \n{str_stiffness}")
       
    # Make the joint FER matrix
    joint = np.array([0] * len(allDel), dtype=float)
    new = []
    f = 0
    for member in members:
        member.calculate_FER()
        count = 0
        new.append(np.array([0] * len(allDel), dtype=float))
        for i in member.dof:
            new[f][i - 1] = member.FER[count]
            count += 1
        f += 1

    # print(f"new = \n{new}")

    for i in new:
        joint += i
    # print(f"joint = \n{joint}")

    # Reactions
    Reactions_def = []
    P = []
    for node in nodes:
        Pi = [node.Fx, node.Fy, node.Mu]
        # print(f"Pi = {Pi}")
        P += Pi
        for i in range(len(Pi)):
            if Pi[i] == 'Rx' or Pi[i] == 'Ry' or Pi[i] == 'Mu':
                # Reactions_def.append(f"{P[i]} at node {node.id}")
                Reactions_def.append((P[i], node))
    
    # print(f"P = {P}")
    forces = []
    pk = []
    ind = []
    other = []
    for i in range(len(P)):
        # Add force on node if any
        try:
            x = float(P[i])
            if x is not np.nan:
                joint[i] += x

        except:
            pass

        if P[i] != 'Rx' and P[i] != 'Ry' and P[i] != 'Mu':
            pk.append(joint[i])
            ind.append(i)

        else:
            other.append(i)

    mat_mul = []
    row = 0
    for i in range(len(str_stiffness)):
        if i in ind:
            mat_mul.append([])
            for j in range(len(str_stiffness)):
                if j in ind:
                    mat_mul[row].append(str_stiffness[i, j])
            row += 1

    mat_mul = np.matrix(mat_mul)
    # print(f"mat_mul \n = {mat_mul}")

    pk = np.matrix(pk)
    # print(f"pk = {pk}")

    delta = np.linalg.inv(mat_mul).dot(pk.T)
    # print(f"mat_mul Inverse : {np.linalg.inv(mat_mul)}")
    # print(f"delta = {delta}")
    # print(f"str_stiffness = {str_stiffness}")
    mat_mul = []
    row = 0
    for i in other:
        mat_mul.append([])
        for j in ind:
            x = str_stiffness[i, j]
            mat_mul[row].append(str_stiffness[i, j])
        row += 1

    mat_mul = np.matrix(mat_mul)
    # print(f"mat_mul2 = \n{mat_mul}")
    p = []
    for i in other:
        p.append(joint[i])
    add = []
    for i in other:
        add.append(-1 * joint[i])
    add = np.matrix(add)
    add = np.transpose(add)

    reactions = np.matrix(mat_mul).dot(delta) + add
    result = pd.Series(reactions.T.tolist()[0], index=Reactions_def)

    reactions_arr = []
    for i in range(len(Reactions_def)):
        typeOfReaction = Reactions_def[i][0]
        nodeOfReaction = Reactions_def[i][1]
        reaction_magnitude = result.iloc[i]
        # reactions_arr.append(Reaction(typeOfReaction, reaction_magnitude, nodeOfReaction))
        
        reactions_arr.append(Reaction(typeOfReaction, reaction_magnitude, nodeOfReaction))
    return reactions_arr
