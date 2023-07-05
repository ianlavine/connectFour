import random
import copy
import math

def to_base_2(n):
    digits = []
    while n:
        digits.append(str(n % 2))
        n //= 2
    return ''.join(digits[::-1]).rjust(42, '0')


class Board:
    def __init__(self, turn, move=None, options=[0]*7, x=None, o=None) -> None:
        self.turn = turn
        self.move = move
        self.move_val_xo = None
        self.flat_move = 0
        self.options = options
        self.x_repr = x
        self.o_repr = o

    @property
    def turn_repr(self):
        if self.turn == 'X':
            return self.x_repr
        return self.o_repr

    def display_number_xo(self):
        xs = to_base_2(self.x_repr)
        os = to_base_2(self.o_repr)
        for i in range(6):
            row = ''
            for y in range(7):
                if xs[i*7 + y] == '1':
                    row += 'X'
                elif os[i*7 + y] == '1':
                    row += '0'
                else:
                    row += '.'
            print(row)

    def update_number_xo(self, pos):
        height = self.get_height(pos)
        val_to_be_added = self.get_pos_value(height, pos)
        self.move_val_xo = val_to_be_added
        self.flat_move = height * 7 + (6 - pos)
        self.add_to_repr(val_to_be_added)

    def get_height(self, pos):
        sub = 6 - pos
        for i in range(6):
            flat_pos = i * 7 + sub
            if not self.get_piece(flat_pos):
                return i

    def get_piece(self, pos_val):
        mask = 1 << pos_val
        x = self.x_repr & mask
        o = self.o_repr & mask
        return x or o

    def get_turn_piece(self, pos_val):
        mask = 1 << pos_val
        return self.turn_repr & mask

    def get_pos_value(self, height, pos):
        return 1 << (height * 7 + (6 - pos))

    def add_to_repr(self, val):
        if self.turn == 'X':
            self.x_repr += val
        else:
            self.o_repr += val
    
    def empty(self, pos):
        return True

    def swap_turn(self):
        self.turn = 'X' if self.turn == '0' else '0'

    def make_move(self, pos):
        col = self.place(pos)
        self.move = (pos, col)
        self.update_number_xo(pos)

    def place(self, pos):
        self.options[pos] += 1
        return self.options[pos] - 1

    def check_win(self):
        if self.move is None:
            return False
        return self.vertical_win() or self.horizontal_win() or self.diagonal_win()

    def check_win_xo(self):
        if self.check_direction(self.down_move, self.down_cutoff) >= 3:
            return True
        if self.check_direction(self.left_move, self.left_cutoff) + self.check_direction(self.right_move, self.right_cutoff) >= 3:
            return True
        if self.check_direction(self.up_left_move, self.up_left_cutoff) + self.check_direction(self.down_right_move, self.down_right_cutoff) >= 3:
            return True
        return self.check_direction(self.down_left_move, self.down_left_cutoff) + self.check_direction(self.up_right_move, self.up_right_cutoff) >= 3  

    def check_direction(self, change, cutoff):
        count = 0
        for i in range(1, 4):
            nex = change(i)
            if cutoff(nex):
                break
            if self.get_turn_piece(nex):
                count += 1
            else:
                break

        return count

    def down_move(self, i):
        return self.flat_move - i * 7

    def down_cutoff(self, i):
        return i < 0

    def left_move(self, i):
        return self.flat_move + i

    def left_cutoff(self, i):
        return i % 7 == 0

    def right_move(self, i):
        return self.flat_move - i

    def right_cutoff(self, i):
        return i % 7 == 6

    def up_left_move(self, i):
        return self.flat_move + i * 8

    def up_left_cutoff(self, i):
        return i % 7 == 0 or i > 42

    def down_right_move(self, i):
        return self.flat_move - i * 8

    def down_right_cutoff(self, i):
        return i % 7 == 6 or i < 0

    def up_right_move(self, i):
        return self.flat_move + i * 6

    def up_right_cutoff(self, i):
        return i % 7 == 6 or i > 42

    def down_left_move(self, i):
        return self.flat_move - i * 6

    def down_left_cutoff(self, i):
        return i % 7 == 0 or i < 0

    def end_game(self):
        if self.check_win_xo():
            print(f"Player {self.turn} wins!")
            return True
        if self.check_draw():
            print("Draw!")
            return True
        return False

    def check_draw(self):
        return False

    def straight_ranges(self, start, end):
        ranges = []
        while start + 3 <= end:
            ranges.append(range(start, start + 4))
            start += 1
        return ranges

    def diagonal_ranges(self):
        fronthand_ranges = []
        backhand_ranges = []

        lat, lon = self.move
        for _ in range(4):
            if lat >= 0 and lon >= 0:
                fronthand_ranges.append((lat, lon))
                lat -= 1
                lon -= 1

        fronthand_ranges.reverse()
        lat, lon = self.move
        for _ in range(3):
            if lat < 6 and lon < 5:
                lat += 1
                lon += 1
                fronthand_ranges.append((lat, lon))

        lat, lon = self.move
        for _ in range(4):
            if lat >= 0 and lon < 6:
                backhand_ranges.append((lat, lon))
                lat -= 1
                lon += 1

        backhand_ranges.reverse()
        lat, lon = self.move
        for _ in range(3):
            if lat < 6 and lon >= 1:
                lat += 1
                lon -= 1
                backhand_ranges.append((lat, lon))

        return fronthand_ranges, backhand_ranges

    def evaluate(self):
        return 0

class State(Board):
    def __init__(self, turn, move=None, options=[0]*7, x=0, o=0) -> None:
        super().__init__(turn, move, options, x, o)
        self.weight = None
        self.offense = None
        self.children = dict()

    def best_move(self):
        max_weight = max(self.children[child].weight for child in self.children)
        max_weight_children = [(child, move) for move, child in self.children.items() if child.weight == max_weight]
        max_offense = max_weight_children[0][0].offense
        max_child = max_weight_children[0]
        for child in max_weight_children:
            if child[0].offense > max_offense:
                max_offense = child[0].offense
                max_child = child

        return max_child

    def make_child(self, move):
        new_options = self.options[:]
        new_state = State(self.turn, options=new_options, x=self.x_repr, o=self.o_repr)
        new_state.swap_turn()
        new_state.make_move(move)
        self.children[move] = new_state
        return new_state


class Game(Board):
    def __init__(self, turn, move=None, options=[0]*7, x=0, o=0) -> None:
        super().__init__(turn, move, options, x, o)
        self.state_pool = dict()
        self.begin_state = None
        self.unique = 0
        self.found = 0

    def user_turn(self):
        col = int(input(f"Player {self.turn}, enter position: ")) - 1
        if col < 0 or col > 6:
            print("Position out of range!")
            self.user_turn()
        elif self.empty(col):
            row = self.place(col)
            self.update_number_xo(col)
            self.move = (col, row)
        else:
            print("Column already filled")
            self.user_turn()

    def computer_turn(self):
        self.begin_state = State('0', self.move, self.options[:], self.x_repr, self.o_repr)
        self.look_ahead(self.begin_state)
        best_move = self.begin_state.best_move()
        col = self.place(best_move[1])
        self.update_number_xo(best_move[1])
        self.move = (best_move[1], col)
        self.unique, self.found = 0, 0
        print(f"Computer plays at {self.move[0] + 1}")
        self.begin_state = None
        self.state_pool = dict()

    def play(self):
        self.display_number_xo()
        while not self.end_game():
            self.turn = 'X' if self.turn == '0' else '0'
            self.user_turn()
            print("Base 2: " + str(self.x_repr) + " " + str(self.o_repr) + " " + str(self.move_val_xo))
            self.display_number_xo()

    def play_versus_computer(self):
        counter = 0
        while True:
            self.turn = '0'
            if counter % 2 == 0:
                self.turn = 'X'
            while not self.end_game():
                if self.turn == '0':
                    self.turn = 'X'
                    self.computer_turn()
                    self.display_number_xo()
                    print("Base 2: " + str(self.x_repr) + " " + str(self.o_repr) + " " + str(self.move_val_xo))

                    if not self.end_game():
                        self.turn = '0'
                        self.user_turn()
                        self.display_number_xo()
                        print("Base 2: " + str(self.x_repr) + " " + str(self.o_repr) + " " + str(self.move_val_xo))

                else:
                    self.turn = '0'
                    self.user_turn()
                    self.display_number_xo()
                    print("Base 2: " + str(self.x_repr) + " " + str(self.o_repr) + " " + str(self.move_val_xo))

                    if not self.end_game():
                        self.turn = 'X'
                        self.computer_turn()
                        self.display_number_xo()
                        print("Base 2: " + str(self.x_repr) + " " + str(self.o_repr) + " " + str(self.move_val_xo))

            go = input(("press any key to continue, or 'q' to quit"))
            counter += 1

    def look_ahead(self, state: State, depth=0):
        for s in range(7):
            if state.options[s] == 6:
                continue
            new_state = state.make_child(s)
            board_id = (new_state.x_repr, new_state.o_repr)
            if board_id in self.state_pool:
                state.children[s] = self.state_pool[board_id]
                self.found += 1
            else:
                self.unique += 1
                if new_state.check_win_xo():
                    new_state.weight = 1 if new_state.turn == 'X' else -1
                    new_state.offense = new_state.weight
                elif new_state.check_draw():
                    new_state.weight = 0
                    new_state.offense = 0
                elif depth == 7:
                    new_state.weight = new_state.evaluate()
                    new_state.offense = 0
                else:
                    self.look_ahead(new_state, depth + 1)

                self.state_pool[board_id] = new_state
        
        state.weight = min(state.children[child].weight for child in state.children)
        if state.turn == 'X':
            state.weight = max(state.children[child].weight for child in state.children)
        state.offense = round(sum(state.children[child].offense for child in state.children)/len(state.children), 3)


if __name__ == "__main__":
    game = Game([' ' * 6 for _ in range(7)], 'X', None)
    # game.train()
    # print(game.total_states)
    # game.num = 16472437332222276
    # game.num = 3099366828 
    # game.num = 44
    # game.play_versus_computer()
    game.play()
    # game.move_val = 81
    # game.num = 122
    # print(game.check_down(4))
    # game.display_number()
    # to_base_3(14)
    # game.o_repr = 0
    # game.x_repr = 3
    # print(game.get_height(6))