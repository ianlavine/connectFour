import time

SEARCH_DEPTH = 10
MOVE_ORDER = (3, 2, 4, 1, 5, 0, 6)

def to_base_2(n):
    digits = []
    while n:
        digits.append(str(n % 2))
        n //= 2
    return ''.join(digits[::-1]).rjust(42, '0')

def down_cutoff(i):
    return i < 0

def left_cutoff(i):
    return i % 7 == 0

def right_cutoff(i):
    return i % 7 == 6

def up_left_cutoff(i):
    return i % 7 == 0 or i > 42

def down_right_cutoff(i):
    return i % 7 == 6 or i < 0

def up_right_cutoff(i):
    return i % 7 == 6 or i > 42

def down_left_cutoff(i):
    return i % 7 == 0 or i < 0

cut_offs = {
    ((1, left_cutoff),
    (-1, right_cutoff)),
    ((8, up_left_cutoff),
    (-8, down_right_cutoff)),
    ((6, up_right_cutoff),
    (-6, down_left_cutoff))
}


class Board:
    def __init__(self, turn, x=0, o=0, x_set=set(), o_set=set()) -> None:
        self.turn = turn
        self.col = None
        self.x_repr = x
        self.o_repr = o
        self.x_set = x_set
        self.o_set = o_set

    def reset(self):
        self.col = None
        self.x_repr = 0
        self.o_repr = 0

    @property
    def turn_repr(self):
        if self.turn == 'X':
            return self.x_repr
        return self.o_repr

    @property
    def opp_repr(self):
        if self.turn == 'X':
            return self.o_repr
        return self.x_repr

    @property
    def turn_set(self):
        if self.turn == 'X':
            return self.x_set
        return self.o_set

    @property
    def opp_set(self):
        if self.turn == 'X':
            return self.o_set
        return self.x_set

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

    def display_wins(self):
        print("X wins: ", self.x_set)
        print("0 wins: ", self.o_set)

    def update_number_xo(self, pos):
        self.col = pos
        self.row = self.get_height(self.col)
        self.flat_pos =  self.row * 7 + self.col
        self.opp_set.discard(self.flat_pos)
        self.flat_pos_value = 1 << self.flat_pos
        self.add_to_repr()
        self.check_for_sets()

    def get_height(self, pos):
        sub = pos
        for i in range(7):
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

    def get_opp_piece(self, pos_val):
        mask = 1 << pos_val
        return self.opp_repr & mask

    def add_to_repr(self):
        if self.turn == 'X':
            self.x_repr = self.x_repr | self.flat_pos_value
        else:
            self.o_repr = self.o_repr | self.flat_pos_value

    def add_to_3_set(self, keys):
        if self.turn == 'X':
            self.x_set.update(keys)
        else:
            self.o_set.update(keys)
    
    def empty(self, pos):
        return self.get_height(pos) < 6

    def swap_turn(self):
        self.turn = 'X' if self.turn == '0' else '0'

    def check_for_sets(self):
        if self.col is None:
            return False

        down = self.check_direction(-7, down_cutoff)
        if down[0] == 2 and self.flat_pos < 36:
            self.add_to_3_set({self.flat_pos + 7})

        for first_cutoff, second_cutoff in cut_offs:
            first_num, first_set, first_split  = self.check_direction(first_cutoff[0], first_cutoff[1])
            second_num, second_set, second_split = self.check_direction(second_cutoff[0], second_cutoff[1])

            ends = first_set | second_set
            if ends:
                sum = first_num + second_num
                if sum < 2:
                    if first_split + sum >= 2:
                        self.add_to_3_set(first_set)
                    if second_split + sum >= 2:
                        self.add_to_3_set(second_set)
                else:
                    self.add_to_3_set(ends)
            

    def check_direction(self, change, cutoff):
        count = 0
        end = set()
        split = 0

        nex = self.flat_pos
        for _ in range(3):
            nex += change
            if cutoff(nex) or self.get_opp_piece(nex):
                return (count, end, split)
            if self.get_turn_piece(nex):
                if end:
                    split += 1
                else:
                    count += 1
            elif end:
                return (count, end, split)
            else:
                end.add(nex)

        return (count, end, split)

    def immediate_loss_loop(self):
        for opp in self.opp_set:
            quo, col = divmod(opp, 7)
            if self.get_height(col) == quo:
                return col
        return None

    def check_win(self):
        return self.col is not None and self.flat_pos in self.turn_set

    def evaluate(self):
        return len(self.x_set) - len(self.o_set)

class Leaf():

    def __init__(self, weight):
        self.weight = weight

class State(Board):
    def __init__(self, turn, x_repr=0, o_repr=0, x_set=set(), o_set=set(), depth=0) -> None:
        super().__init__(turn, x_repr, o_repr, x_set, o_set)
        self.weight = None
        self.children = dict()
        self.depth = depth

    def best_move(self):
        max_weight = max(self.children[child].weight for child in self.children)
        max_weight_child = [(child, move) for move, child in self.children.items() if child.weight == max_weight][0]

        print("Best weight: " + str(max_weight))

        if max_weight == 10:
            print("Solution found! ----------------------")

        return max_weight_child

    def make_child(self, pos):
        new_state = State(self.turn, self.x_repr, self.o_repr, self.x_set.copy(), self.o_set.copy(), self.depth + 1)
        new_state.swap_turn()
        new_state.update_number_xo(pos)
        self.children[pos] = new_state
        return new_state

    def make_leaf(self, pos):
        new_state = Leaf(self.weight)
        self.children[pos] = new_state

    def display_children(self, depth):
        if depth == 0:
            for child in self.children:
                print(str(7 - self.col) + ": Column " + str(7 - child) + " has weight " + str(self.children[child].weight))
        else:
            for child in self.children:
                self.children[child].display_children(depth - 1)

    def check_draw(self):
        if self.depth == 42:
            return True
        return self.depth >= 40 and not self.x_set and not self.o_set


class Game(Board):
    def __init__(self, turn, x=0, o=0, x_set=set(), o_set=set()) -> None:
        super().__init__(turn, x, o, x_set, o_set)
        self.state_pool = dict()
        self.begin_state = None
        self.search_depth = SEARCH_DEPTH

    def reset(self):
        self.state_pool = dict()
        self.begin_state = None
        super().reset()

    def end_game(self):
        if self.check_win():
            print(f"Player {self.turn} wins!")
            return True
        if self.check_draw():
            print("Draw!")
            return True
        return False

    def check_draw(self):
        for i in range(7):
            if self.get_height(i) < 6:
                return False
        return True

    def user_turn(self):
        col = 7 - int(input(f"Player {self.turn}, enter position: "))
        if col < 0 or col > 6:
            print("Position out of range!")
            self.user_turn()
        elif self.empty(col):
            self.update_number_xo(col)
            self.display_wins()
        else:
            print("Column already filled")
            self.user_turn()

    def computer_turn(self):
        self.begin_state = State('0', self.x_repr, self.o_repr, self.x_set.copy(), self.o_set.copy())
        self.look_ahead(self.begin_state)
        best_move = self.begin_state.best_move()
        if best_move[0].weight == 10:
            self.search_depth -= 2
        self.update_number_xo(best_move[1])
        print(f"Computer plays at {7 - best_move[1]}")
        self.begin_state = None
        self.state_pool = dict()
        self.display_wins()

    def play(self):
        self.display_number_xo()
        while not self.end_game():
            self.turn = 'X' if self.turn == '0' else '0'
            self.user_turn()
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

            go = input(("press any key to continue, or 'q' to quit: "))
            if go == 'q':
                exit()
            counter += 1
            self.reset()

    def look_ahead(self, state: State, depth=0, alpha=-float('inf'), beta=float('inf')):
        early_loss = state.immediate_loss_loop()
        if early_loss is not None:
            state.weight = -10 if state.turn == 'X' else 10
            state.make_leaf(early_loss)
        else:
            if state.turn == 'X':
                self.min_search_look_ahead(state, depth, alpha, beta)
            else:
                self.max_search_look_ahead(state, depth, alpha, beta)

    def max_search_look_ahead(self, state: State, depth, alpha, beta):
        maxEval = -float('inf')
        for s in MOVE_ORDER:
            if not state.empty(s):
                continue

            new_state = state.make_child(s)
            board_id = (new_state.x_repr, new_state.o_repr)
            if board_id in self.state_pool:
                new_state = self.state_pool[board_id]
            else:
                if new_state.check_draw():
                    new_state.weight = 0
                elif depth == self.search_depth:
                    new_state.weight = new_state.evaluate()
                else:
                    self.look_ahead(new_state, depth + 1, alpha, beta)

                self.state_pool[board_id] = new_state

            maxEval = max(maxEval, new_state.weight)
            alpha = max(alpha, maxEval)

            if beta <= alpha:
                break

        state.weight = maxEval

    def min_search_look_ahead(self, state: State, depth, alpha, beta):
        minEval = float('inf')
        for s in MOVE_ORDER:
            if not state.empty(s):
                continue

            new_state = state.make_child(s)
            board_id = (new_state.x_repr, new_state.o_repr)
            if board_id in self.state_pool:
                new_state = self.state_pool[board_id]
            else:
                if new_state.check_draw():
                    new_state.weight = 0
                elif depth == self.search_depth:
                    new_state.weight = new_state.evaluate()
                else:
                    self.look_ahead(new_state, depth + 1, alpha, beta)

                self.state_pool[board_id] = new_state

            minEval = min(minEval, new_state.weight)
            beta = min(beta, minEval)

            if beta <= alpha:
                break

        state.weight = minEval


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