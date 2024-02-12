import numpy as np
import pandas as pd
import loads
import math
import pygame
import allFuncs as aF
import random

global sub_nodes, sub_members, GLOBAL_CENTER, GLOBAL_SCALE
sub_nodes = []
sub_members = []  


class Reaction:
    def __init__(self, _type, magnitude, node):
        self.type = _type
        self.magnitude = round(magnitude,2)
        self.node = node      
        self.color = (0, 255, 0)
        self.arrow_length = 50
        # self.shape = self.def_shape()

    def draw_arc(self, screen):
        x = self.node.screen[0] - 25
        y = self.node.screen[1] - 25
        pygame.draw.arc(screen, self.color, (*(x, y), 50, 50), math.radians(90), 0, width=1)
        # pygame.draw.circle(screen, black, coordinate, 5)
        if self.magnitude >= 0:
            arr = [(x+48, y+20), (x+53, y+30), (x+43, y+30)]
            text_loc = (self.node.screen[0]+50, self.node.screen[1]-25)
        else:
            arr = [(x+35, y), (x+25, y+5), (x+25, y-5)]
            text_loc = (self.node.screen[0]+70, self.node.screen[1]-25)
        pygame.draw.polygon(screen, self.color, arr)

        # Create a font
        font = pygame.font.Font(None, 25)

        # Render the text
        text_surface = font.render(f"{self.magnitude}", True, self.color)
        text_rect = text_surface.get_rect()
        text_rect.midright = text_loc


        # Draw the text
        screen.blit(text_surface, text_rect)

    def get_angle(self):
        if self.type == "Rx": 
            if self.magnitude >= 0:
                return 0
            else:
                return 180
        elif self.type == "Ry":
            if self.magnitude >= 0:
                return 90
            else:
                return 270
        elif self.type == "Mu":
            return "Mu"
        
        

    def draw(self, screen):
        if self.type == "Rx" or "Ry":
            angle = self.get_angle()
            if angle != "Mu":
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
    
    no_of_divisions = 2
    screen_increment = (member.length / no_of_divisions) * GLOBAL_SCALE
    global_increment = (member.length / no_of_divisions)
    member.sub_nodes.append(member.start_node)
    for i in range(1, no_of_divisions):
        s_start_x, s_start_y = member.start_node.screen
        g_start_x, g_start_y = member.start_node.point
        x_s = s_start_x + (i * screen_increment * math.cos(math.radians(member.angle)))
        y_s = s_start_y - (i * screen_increment * math.sin(math.radians(member.angle)))
        _sub_node = aF.Node(1, (x_s, y_s), "sub") 
        member.sub_nodes.append(_sub_node)
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
        
def sub_moments(member):
    for force in member.moment:
        sub_length = member.sub_members[0].length
        sub_mem_num_4_force = int(force.loc / sub_length)
        if sub_mem_num_4_force >= len(member.sub_members):
            sub_mem_num_4_force -= 1
        loc = force.loc - (sub_mem_num_4_force * sub_length)
        # point_Of_Force = aF.calculate_force_point(member.sub_members[sub_mem_num_4_force].start_node.screen, member.sub_members[sub_mem_num_4_force].angle, loc)
        member.sub_members[sub_mem_num_4_force].moment.append(loads.Moment(force.no, force.magnitude, loc, force.screen_cood))

def sub_point_forces(member):
    for force in member.point_forces:
        sub_length = member.sub_members[0].length
        sub_mem_num_4_force = int(force.loc / sub_length)
        if sub_mem_num_4_force >= len(member.sub_members):
            sub_mem_num_4_force -= 1
        loc = force.loc - (sub_mem_num_4_force * sub_length)
        # point_Of_Force = aF.calculate_force_point(member.sub_members[sub_mem_num_4_force].start_node.screen, member.sub_members[sub_mem_num_4_force].angle, loc)
        member.sub_members[sub_mem_num_4_force].point_forces.append(loads.Point_Force(force.no, member.sub_members[sub_mem_num_4_force].start_node, force.angle, loc, force.mag, force.screen, member.sub_members[sub_mem_num_4_force].color))        


def sub_dist_loads(member):
    dls = member.udl + member.uvl
    for force in dls:
        sM = force.start_mag
        eM = force.end_mag
        angle = force.angle
        a = force.a_distance
        b = force.b_distance
        c = a + b
        d = (eM - sM) / b #Delta force per lenght 
        start = 0
        for sub_member in member.sub_members:
            sL = sub_member.length
            _c = start + sL
            #if starts in sub
            if start <= a <= _c:
                _a = a - start
                #if starts in the sub and end after sub
                if c > _c:
                    _b = sL - _a
                    _eM = sM + d * _b
                    if force.type == "udl":
                        sub_member.udl.append(loads.Dist_Load(len(sub_member.udl)+1, "udl", sM, _eM, angle, _a, _b, sub_member))
                    else:
                        sub_member.uvl.append(loads.Dist_Load(len(sub_member.udl)+1, "uvl", sM, _eM, angle, _a, _b, sub_member))
                #if starts in the sub and end in the sub
                if c <= _c:
                    if force.type == "udl":
                        sub_member.udl.append(loads.Dist_Load(len(sub_member.udl)+1, "udl", sM, eM, angle, _a, b, sub_member))
                    else:
                        sub_member.uvl.append(loads.Dist_Load(len(sub_member.udl)+1, "uvl", sM, eM, angle, _a, b, sub_member))
            
            #if starts before sub
            if a < start:
                _a = 0
                _sM = sM + d * (start - a)
                #if starts before sub and ends after sub
                if c > _c:
                    _eM = sM + d * (_c - a)
                    _b = sL
                    if force.type == "udl":
                        sub_member.udl.append(loads.Dist_Load(len(sub_member.udl)+1, "udl", _sM, _eM, angle, _a, _b, sub_member))
                    else:
                        sub_member.uvl.append(loads.Dist_Load(len(sub_member.udl)+1, "uvl", _sM, _eM, angle, _a, _b, sub_member))
                #if starts before sub and ends in sub
                if c < _c:
                    _b = c - start
                    if force.type == "udl":
                        sub_member.udl.append(loads.Dist_Load(len(sub_member.udl)+1, "udl", _sM, eM, angle, _a, _b, sub_member))
                    else:
                        sub_member.uvl.append(loads.Dist_Load(len(sub_member.udl)+1, "uvl", _sM, eM, angle, _a, _b, sub_member))
                    
            start += sL
              
        
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
        sub_moments(member)
        sub_dist_loads(member)

def reset(members):
    global sub_nodes, sub_members
    sub_members = []
    sub_nodes = []
    for member in members:
        member.sub_members = []

def calculations(nodes, members, _GLOBAL_CENTER, _GLOBAL_SCALE):
    global sub_nodes, sub_members, GLOBAL_CENTER, GLOBAL_SCALE
    
    GLOBAL_CENTER = _GLOBAL_CENTER
    GLOBAL_SCALE = _GLOBAL_SCALE
    
    # [member.finalize_calcs() for member in members]
    """ Uncomment if sub-division """
    reset(members)
    develop_sub_nodes(nodes, members)
    develop_sub_members(members)
    
    nodes = sub_nodes
    members = sub_members
    
    # [member.finalize_calcs() for member in sub_members]
    for member in members:
        member.finalize_calcs()
        print(f"Member {member.id}:\nLenght={member.length} \nAngle={member.angle}\nstart={member.start_node.sub_id} {member.start_node.point}\nend={member.end_node.sub_id} {member.end_node.point}")
        
        if len(member.point_forces)>0:
            print(f"{member.point_forces[0].mag} at {member.point_forces[0].loc}")  
        print("\n")
    
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
                col += 1
            row += 1
        str_stiffness += new
        str_stiffness = np.matrix(str_stiffness)
    
       
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

    for i in new:
        joint += i

    # Reactions
    Reactions_def = []
    P = []
    for node in nodes:
        Pi = [node.Fx, node.Fy, node.Mu]
        P += Pi
        for i in range(len(Pi)):
            if Pi[i] == 'Rx' or Pi[i] == 'Ry' or Pi[i] == 'Mu':
                # Reactions_def.append(f"{P[i]} at node {node.id}")
                Reactions_def.append((Pi[i], node))
    
    # forces = []
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

    pk = np.matrix(pk)

    delta = np.linalg.inv(mat_mul).dot(pk.T)

    mat_mul = []
    row = 0
    for i in other:
        mat_mul.append([])
        for j in ind:
            x = str_stiffness[i, j]
            mat_mul[row].append(str_stiffness[i, j])
        row += 1

    mat_mul = np.matrix(mat_mul)

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

        reactions_arr.append(Reaction(typeOfReaction, reaction_magnitude, nodeOfReaction))
    return reactions_arr
