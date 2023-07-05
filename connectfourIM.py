import time


def to_base_2(n):
    digits = []
    while n:
        digits.append(str(n % 2))
        n //= 2
    return ''.join(digits[::-1]).rjust(42, '0')


class Board:
    def __init__(self, turn, x=0, o=0) -> None:
        self.turn = turn
        self.move_val_xo = None
        self.row = None
        self.col = None
        self.x_repr = x
        self.o_repr = o

    @property
    def turn_repr(self):
        if self.turn == 'X':
            return self.x_repr
        return self.o_repr

    @property
    def flat_pos(self):
        return self.row * 7 + self.col

    @property
    def flat_pos_value(self):
        return 1 << self.flat_pos

    def pos_value(self, pos):
        return 1 << pos

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
        self.col = pos
        self.row = self.get_height(self.col)
        self.move_val_xo = self.flat_pos_value
        self.add_to_repr()

    def get_height(self, pos):
        sub = pos
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

    def add_to_repr(self):
        if self.turn == 'X':
            self.x_repr += self.move_val_xo
        else:
            self.o_repr += self.move_val_xo
    
    def empty(self, pos):
        return self.get_height(pos) < 5

    def swap_turn(self):
        self.turn = 'X' if self.turn == '0' else '0'

    def check_win_xo(self):
        if not self.move_val_xo:
            return False
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
        return self.flat_pos - i * 7

    def down_cutoff(self, i):
        return i < 0

    def left_move(self, i):
        return self.flat_pos + i

    def left_cutoff(self, i):
        return i % 7 == 0

    def right_move(self, i):
        return self.flat_pos - i

    def right_cutoff(self, i):
        return i % 7 == 6

    def up_left_move(self, i):
        return self.flat_pos + i * 8

    def up_left_cutoff(self, i):
        return i % 7 == 0 or i > 42

    def down_right_move(self, i):
        return self.flat_pos - i * 8

    def down_right_cutoff(self, i):
        return i % 7 == 6 or i < 0

    def up_right_move(self, i):
        return self.flat_pos + i * 6

    def up_right_cutoff(self, i):
        return i % 7 == 6 or i > 42

    def down_left_move(self, i):
        return self.flat_pos - i * 6

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

    def evaluate(self):
        return 0

class State(Board):
    def __init__(self, turn, x=0, o=0) -> None:
        super().__init__(turn, x, o)
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

    def make_child(self, pos):
        new_state = State(self.turn, x=self.x_repr, o=self.o_repr)
        new_state.swap_turn()
        new_state.update_number_xo(pos)
        self.children[pos] = new_state
        return new_state


class Game(Board):
    def __init__(self, turn, x=0, o=0) -> None:
        super().__init__(turn, x, o)
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
            self.update_number_xo(6 - col)
        else:
            print("Column already filled")
            self.user_turn()

    def computer_turn(self):
        self.begin_state = State('0', self.x_repr, self.o_repr)
        self.look_ahead(self.begin_state)
        best_move = self.begin_state.best_move()
        self.update_number_xo(best_move[1])
        self.unique, self.found = 0, 0
        print(f"Computer plays at {best_move[1] + 1}")
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

                    start = time.time()
                    self.computer_turn()
                    end = time.time()
                    print(end - start)

                    self.display_number_xo()

                    if not self.end_game():
                        self.turn = '0'
                        self.user_turn()
                        self.display_number_xo()

                else:
                    self.turn = '0'
                    self.user_turn()
                    self.display_number_xo()

                    if not self.end_game():
                        self.turn = 'X'

                        start = time.time()
                        self.computer_turn()
                        end = time.time()
                        print(end - start)

                        self.display_number_xo()

            go = input(("press any key to continue, or 'q' to quit"))
            counter += 1

    def look_ahead(self, state: State, depth=0):
        for s in range(7):
            if not state.empty(s):
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
    game = Game('X')
    # game.train()
    # print(game.total_states)
    # game.num = 16472437332222276
    # game.num = 3099366828 
    # game.num = 44
    game.play_versus_computer()
    # game.play()
    # game.move_val = 81
    # game.num = 122
    # print(game.check_down(4))
    # game.display_number()
    # to_base_3(14)
    # game.o_repr = 0
    # game.x_repr = 3
    # print(game.get_height(6))