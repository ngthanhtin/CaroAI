import pygame, itertools
import random

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)


class Box(object):
    state = 0
    
    def __init__(self, x, y, size, board):
        self.size = size
        self.line_width = int(self.size / 40) if self.size > 40 else 1
        self.radius = (self.size / 2) - (self.size / 8)
        self.rect = pygame.Rect(x, y, size, size)
        self.board = board
    
    def mark_x(self):
        pygame.draw.line(self.board.surface, RED, (self.rect.centerx - self.radius, self.rect.centery - self.radius), (self.rect.centerx + self.radius, self.rect.centery + self.radius), self.line_width)
        pygame.draw.line(self.board.surface, RED, (self.rect.centerx - self.radius, self.rect.centery + self.radius), (self.rect.centerx + self.radius, self.rect.centery - self.radius), self.line_width)
    
    def mark_o(self):
        pygame.draw.circle(self.board.surface, BLUE, (int(self.rect.centerx), int(self.rect.centery)), int(self.radius), self.line_width)


class Board(object):
    turn = 1 # X first
    
    def __init__(self, grid_size=3, is_ai=False, box_size=200, border=20, line_width=5):
        self.is_ai = is_ai
        self.grid_size = grid_size
        self.box_size = box_size
        self.border = border
        self.line_width = line_width
        surface_size = (self.grid_size * self.box_size) + (self.border * 2) + (self.line_width * (self.grid_size - 1))
        self.surface = pygame.display.set_mode((surface_size, surface_size), 0, 32)
        self.game_over = False
        self.setup()
        
    def setup(self):
        pygame.display.set_caption('CARO')
        self.surface.fill(WHITE)
        self.draw_lines()
        self.initialize_boxes()
        self.calculate_winners()
    
    def draw_lines(self):
        for i in range(1, self.grid_size):
            start_position = ((self.box_size * i) + (self.line_width * (i - 1))) + self.border
            width = self.surface.get_width() - (2 * self.border)
            pygame.draw.rect(self.surface, BLACK, (start_position, self.border, self.line_width, width))
            pygame.draw.rect(self.surface, BLACK, (self.border, start_position, width, self.line_width))
    
    def initialize_boxes(self):
        self.boxes = []
        self.x_moves = []
        self.o_moves = []

        top_left_numbers = []
        for i in range(0, self.grid_size):
            num = ((i * self.box_size) + self.border + (i *self.line_width))
            top_left_numbers.append(num)
        
        box_coordinates = list(itertools.product(top_left_numbers, repeat=2))
        
        for x, y in box_coordinates:
            self.boxes.append(Box(x, y, self.box_size, self))
    
    def get_box_at_pixel(self, x, y):
        for index, box in enumerate(self.boxes):
            if box.rect.collidepoint(x, y):
                return index, box
        return None, None
    
    def process_click(self, x, y):
        index, box = self.get_box_at_pixel(x, y)
        if box is not None and not self.game_over:
            self.play_turn(index, box)
            self.check_game_over()
            if self.is_ai:
                self.ai_turn()
                self.check_game_over()
            
    
    def play_turn(self, index, box):
        if box.state != 0:
            return
        if self.turn == 1:
            box.mark_x()
            box.state = 1
            self.turn = 2
            self.x_moves.append(index)
        elif self.turn == 2:
            box.mark_o()
            box.state = 2
            self.turn = 1
            self.o_moves.append(index)
        return

    def ai_turn(self):
        if self.turn != 2:
            return
        #define AI here
        def ai_1():
            for index, box in enumerate(self.boxes):
                if box.state == 0:
                    box.mark_o()
                    box.state = 2
                    self.turn = 1
                    return
        
        def ai_2():
            index = self.find_for_four_combinations()
            index = None
            if index is not None:
                self.boxes[index].mark_o()
                self.boxes[index].state = 2
                self.turn = 1
            else:
                #get possible move for AI around Xs
                possible_ai_moves = []
                
                for move in self.x_moves:
                    """
                        * * *
                        * x *
                        * * *
                    """
                    if self.boxes[move - self.grid_size - 1].state == 0:
                        possible_ai_moves.append(move - self.grid_size - 1)
                    if self.boxes[move - self.grid_size].state == 0:
                        possible_ai_moves.append(move - self.grid_size)
                    if self.boxes[move - self.grid_size + 1].state == 0:
                        possible_ai_moves.append(move - self.grid_size + 1)
                    if self.boxes[move - 1].state == 0:
                        possible_ai_moves.append(move - 1)
                    if self.boxes[move + 1].state == 0:
                        possible_ai_moves.append(move + 1)
                    if self.boxes[move + self.grid_size - 1].state == 0:
                        possible_ai_moves.append(move + self.grid_size - 1)
                    if self.boxes[move + self.grid_size].state == 0:
                        possible_ai_moves.append(move + self.grid_size)
                    if self.boxes[move + self.grid_size + 1].state == 0:
                        possible_ai_moves.append(move + self.grid_size + 1)

                    # get rid of invalid moves at the boundaries
                    if move % self.grid_size == 0:
                        if (move - self.grid_size - 1) in possible_ai_moves:
                            possible_ai_moves.remove(move - self.grid_size - 1)
                        if (move - 1) in possible_ai_moves:
                            possible_ai_moves.remove(move - 1)
                        if (move + self.grid_size - 1) in possible_ai_moves:
                            possible_ai_moves.remove(move + self.grid_size - 1)
                    if (move + 1) % self.grid_size == 0:
                        if (move - self.grid_size + 1) in possible_ai_moves:
                            possible_ai_moves.remove(move - self.grid_size + 1)
                        if (move + 1) in possible_ai_moves:
                            possible_ai_moves.remove(move + 1)
                        if (move + self.grid_size + 1) in possible_ai_moves:
                            possible_ai_moves.remove(move + self.grid_size + 1)
                    if move >= 0 and move <= self.grid_size - 1:
                        if (move - self.grid_size - 1) in possible_ai_moves:
                            possible_ai_moves.remove(move - self.grid_size - 1)
                        if (move - self.grid_size) in possible_ai_moves:
                            possible_ai_moves.remove(move - self.grid_size)
                        if (move - self.grid_size + 1) in possible_ai_moves:
                            possible_ai_moves.remove(move - self.grid_size + 1)
                    if move >= self.grid_size*(self.grid_size-1) and move <= self.grid_size*self.grid_size - 1:
                        if (move + self.grid_size - 1) in possible_ai_moves:
                            possible_ai_moves.remove(move + self.grid_size - 1)
                        if (move + self.grid_size) in possible_ai_moves:
                            possible_ai_moves.remove(move + self.grid_size)
                        if (move + self.grid_size + 1) in possible_ai_moves:
                            possible_ai_moves.remove(move + self.grid_size + 1)
                
                possible_ai_moves = list(set(possible_ai_moves))
                for move in possible_ai_moves:
                    if self.boxes[move].state != 0:
                        possible_ai_moves.remove(move)
                
                if len(possible_ai_moves) != 0:
                    index = random.choice(possible_ai_moves)
                    print(index)
                    self.boxes[index].mark_o()
                    self.boxes[index].state = 2
                    self.turn = 1
                else:
                    for index, box in enumerate(self.boxes):
                        print("haha ", index)
                        box.mark_o()
                        box.state = 2
                        self.turn = 1
                        break

        ai_2()
        
    def calculate_winners(self):
        self.winning_combinations = []
        self.four_combinations = []
        self.three_combinations = []

        indices = [x for x in range(0, self.grid_size * self.grid_size)]
        
        # Vertical combinations
        for i in range(0, len(indices), self.grid_size):
            for j in range(i, i + self.grid_size - 4):
                self.winning_combinations += [tuple(indices[j:j+5])]

        # Horizontal combinations
        for i in range(0, self.grid_size):
            tmp = []
            for j in range(0, self.grid_size - 4):
                start = i + j * self.grid_size
                for k in range(5):
                    tmp.append(start)
                    start += self.grid_size
                self.winning_combinations += [tuple(tmp)]
                tmp = []
        
        # Diagonal combinations
        # up-right half-triangle
        """
        ******
         *****
          ****
           ***
            **
             *
        """
        for i in range(self.grid_size):
            k = i
            tmp = []
            for j in range(self.grid_size - i):
                tmp.append(k)
                k += self.grid_size + 1
            for u in range(len(tmp) - 4):
                self.winning_combinations += [tuple(tmp[u:u+5])]

        # down-left half-triangle
        """
        *
        **
        ***
        ****
        *****
        ******
        """
        for i in range(self.grid_size, len(indices), self.grid_size):
            k = i
            tmp = []
            for j in range(self.grid_size - (i//self.grid_size)):
                tmp.append(k)
                k += self.grid_size + 1
            for u in range(len(tmp) - 4):
                self.winning_combinations += [tuple(tmp[u:u+5])]

        # top-left half-triangle
        """
        ******
        *****
        ****
        ***
        **
        *
        """
        for i in range(self.grid_size):
            k = i
            tmp = []
            for j in range(i + 1):
                tmp.append(k)
                k += self.grid_size - 1
            for u in range(len(tmp) - 4):
                self.winning_combinations += [tuple(tmp[u:u+5])]

        # down-right half-triangle
        """
              *
             **
            ***
           ****
          *****
         ******
        """
        for i in range(2 * self.grid_size - 1, len(indices), self.grid_size):
            k = i
            tmp = []
            for j in range(self.grid_size - (i + 1)//self.grid_size + 1):
                tmp.append(k)
                k += self.grid_size - 1
            for u in range(len(tmp) - 4):
                self.winning_combinations += [tuple(tmp[u:u+5])]

        # calculate four combinations
        for combination in self.winning_combinations:
            for i in range(5 - 4 + 1):
                self.four_combinations += [tuple(combination[i:i+4])]
        
        # calculate three combinations
        for combination in self.winning_combinations:
            for i in range(5 - 3 + 1):
                self.three_combinations += [tuple(combination[i:i+3])]

    def find_for_four_combinations(self):
        """
        return index of moveable box
        """
        for combination in self.four_combinations:
            states = []
            for index in combination:
                states.append(self.boxes[index].state)
            if all(x == 1 for x in states):
                if combination[0] + self.grid_size == combination[1]: #horizontal
                    if combination[0] >= 0 and combination[0] <= self.grid_size - 1: # check left bound
                        state = self.boxes[combination[3] + self.grid_size].state
                        if state == 0:
                            return combination[3] + self.grid_size
                    elif (combination[3] >= (self.grid_size*(self.grid_size - 1)) and \
                        combination[3] <= (self.grid_size*self.grid_size-1)): #check right bound
                        state = self.boxes[combination[0] - self.grid_size].state
                        if state == 0:
                            return combination[0] - self.grid_size
                    else:
                        state_head = self.boxes[combination[0] - self.grid_size].state
                        state_tail = self.boxes[combination[3] + self.grid_size].state
                        if state_head == 0 and state_tail == 0:
                            return random.choice([combination[0] - self.grid_size, combination[3] + self.grid_size])
                        elif state_head == 0:
                            return combination[0] - self.grid_size
                        elif state_tail == 0:
                            return combination[3] + self.grid_size

                elif combination[0] + 1 == combination[1]: #vertical
                    if combination[0] % self.grid_size == 0: # check up bound
                        state = self.boxes[combination[3] + 1].state
                        if state == 0:
                            return combination[3] + 1
                    elif (combination[3] + 1) % self.grid_size == 0: # check down bound
                        state = self.boxes[combination[0] - 1].state
                        if state == 0:
                            return combination[0] - 1
                    else:
                        state_head = self.boxes[combination[0] - 1].state
                        state_tail = self.boxes[combination[3] + 1].state
                        if state_head == 0 and state_tail == 0:
                            return random.choice([combination[0] - 1, combination[3] + 1])
                        elif state_head == 0:
                            return combination[0] - 1
                        elif state_tail == 0:
                            return combination[3] + 1
                
                elif combination[0] + self.grid_size + 1 == combination[1]:
                    """
                    *
                     *
                      *
                    """
                    if (combination[0] >= 0 and combination[0] <= self.grid_size - 1) or \
                        (combination[0] % self.grid_size == 0):
                        state = self.boxes[combination[3] + self.grid_size + 1].state
                        if state == 0:
                            return combination[3] + self.grid_size + 1
                    elif ((combination[3] >= (self.grid_size*(self.grid_size - 1)) and \
                        combination[3] <= (self.grid_size*self.grid_size-1))) or \
                            ((combination[3] + 1) % self.grid_size == 0): 
                        state = self.boxes[combination[0] - self.grid_size - 1].state
                        if state == 0:
                            return combination[0] - self.grid_size - 1
                    else:
                        state_head = self.boxes[combination[0] - self.grid_size - 1].state
                        state_tail = self.boxes[combination[3] + self.grid_size + 1].state
                        if state_head == 0 and state_tail == 0:
                            return random.choice([combination[0] - self.grid_size - 1, combination[3] + self.grid_size + 1])
                        elif state_head == 0:
                            return combination[0] - self.grid_size - 1
                        elif state_tail == 0:
                            return combination[3] + self.grid_size + 1

                elif combination[0] + self.grid_size - 1 == combination[1]:
                #     """
                #        *
                #       *
                #      *
                #     """
                    if (combination[0] >= 0 and combination[0] <= self.grid_size - 1) or \
                        ((combination[0] + 1) % self.grid_size == 0):
                        state = self.boxes[combination[3] + self.grid_size - 1].state
                        if state == 0:
                            return combination[3] + self.grid_size - 1
                    elif ((combination[3] >= (self.grid_size*(self.grid_size - 1)) and \
                        combination[3] <= (self.grid_size*self.grid_size-1))) or \
                            (combination[3] % self.grid_size == 0): 
                        state = self.boxes[combination[0] - self.grid_size + 1].state
                        if state == 0:
                            return combination[0] - self.grid_size + 1
                    else:
                        state_head = self.boxes[combination[0] - self.grid_size + 1].state
                        state_tail = self.boxes[combination[3] + self.grid_size - 1].state
                        if state_head == 0 and state_tail == 0:
                            return random.choice([combination[0] - self.grid_size + 1, combination[3] + self.grid_size - 1])
                        elif state_head == 0:
                            return combination[0] - self.grid_size + 1
                        elif state_tail == 0:
                            return combination[3] + self.grid_size - 1
        
        return None

    def check_for_winner(self):
        winner = 0
        for combination in self.winning_combinations:
            states = []
            for index in combination:
                states.append(self.boxes[index].state)
            if all(x == 1 for x in states):
                winner = 1
            if all(x == 2 for x in states):
                winner = 2
        return winner
    
    def check_game_over(self):
        winner = self.check_for_winner()
        if winner:
            self.game_over = True
        elif all(box.state in [1, 2] for box in self.boxes):
            self.game_over = True
        if self.game_over:
            self.display_game_over(winner)
    
    def display_game_over(self, winner):
        surface_size = self.surface.get_height()
        font = pygame.font.Font('freesansbold.ttf', int(surface_size / 8))
        if winner:
            text = 'Player %s won!' % winner
        else:
            text = 'Draw!'
        text = font.render(text, True, BLACK, WHITE)
        rect = text.get_rect()
        rect.center = (surface_size / 2, surface_size / 2)
        self.surface.blit(text, rect)