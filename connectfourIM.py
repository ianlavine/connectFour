import random
import copy
import math

str_val = {"0": 1, "X": 2}
val_str = {"0": " ", "1": "0", "2": "X"}

def to_base_3(n):
    if n == 0:
        return '0' * 6
    digits = []
    while n:
        digits.append(str(n % 3))
        n //= 3
    return ''.join(digits[::-1]).rjust(6, '0')

def to_base_2(n):
    digits = []
    while n:
        digits.append(str(n % 2))
        n //= 2
    return ''.join(digits[::-1]).rjust(42, '0')


class Board:
    def __init__(self, board, turn, move=None, options={0,1,2,3,4,5,6}, n=0, x=None, o=None) -> None:
        self.map = board
        self.turn = turn
        self.move = move
        self.move_val = None
        self.options = options
        self.num = n
        self.x_repr = x
        self.o_repr = o

    def display(self):
        for i in range(6):
            str = ''
            for y in range(7):
                if self.map[y][i] == ' ':
                    str += '.'
                else:
                    str += self.map[y][i]
            print(str)
        # for row in self.map:
        #     print(' '.join(row))

    def display_number(self):
        for i in range(7):
            col_num = self.isolate_column_number(i)
            base_3_num = to_base_3(col_num)
            self.map[i] = ''.join(val_str[j] for j in base_3_num)
        self.display()

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

    def nearest_power_of_3(self, n):
        if n == 0:
            return 1
        elif n == 1:
            return 3

        return int(3 ** math.ceil(math.log(n, 3)))

    def isolate_column_number_xo(self, pos):
        pass

    def isolate_column_number(self, pos):
        top = self.num % (3 ** (6 * (pos + 1)))
        bottom = 3 ** (6 * pos)
        # print("Isolated Column number is: " + str(math.floor(top/bottom)))
        return math.floor(top/bottom)

    def update_number(self, pos):
        col_num = self.isolate_column_number(pos)
        col_update = str_val[self.turn] * self.nearest_power_of_3(col_num) * (3 ** (6 * pos))
        self.num += col_update
        self.move_val = col_update
        return self.num
    
    def empty(self, pos):
        return self.map[pos][0] == ' '

    def swap_turn(self):
        self.turn = 'X' if self.turn == '0' else '0'

    def make_move(self, pos):
        col = self.place(pos)
        self.move = (pos, col)
        if col == 0:
            self.options.remove(pos)
        self.update_number(pos)

    def place(self, pos):
        for i in range(6):
            if i == 5 or self.map[pos][i + 1] != ' ':
                print
                self.map[pos] = self.map[pos][:i] + self.turn + self.map[pos][i+1:]
                return i

    def check_down(self, count):
        sub = self.move_val / 3 ** (count - 1)
        uvp = self.num
        for _ in range(count):
            uvp -= sub
            sub *= 3
            if uvp % sub != 0:
                return False
        return True 


    def check_win(self):
        if self.move is None:
            return False
        return self.vertical_win() or self.horizontal_win() or self.diagonal_win()

    def end_game(self):
        if self.check_win():
            print(f"Player {self.turn} wins!")
            return True
        if self.check_draw():
            print("Draw!")
            return True
        return False

    def vertical_win(self):
        ranges = self.straight_ranges(max(0, self.move[1] - 3), min(5, self.move[1] + 3))
        for range in ranges:
            if all(self.map[self.move[0]][r] == self.turn for r in range):
                return True
        return False

    def horizontal_win(self):
        ranges = self.straight_ranges(max(0, self.move[0] - 3), min(6, self.move[0] + 3))
        for range in ranges:
            if all(self.map[c][self.move[1]] == self.turn for c in range):
                return True
        return False

    def diagonal_win(self):
        for dir in self.diagonal_ranges():
            for i in range(len(dir) - 3):
                if all(self.map[dir[j][0]][dir[j][1]] == self.turn for j in range(i, i + 4)):
                    return True
        return False

    def check_draw(self):
        for row in self.map:
            if ' ' in row:
                return False
        return True

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
    def __init__(self, map, turn, move=None, options={i for i in range(7)}, n=0, x=0, o=0) -> None:
        super().__init__(map, turn, move, options, n, x, o)
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
        new_map = self.map[:]
        new_options = self.options.copy()
        new_state = State(new_map, self.turn, options=new_options, n=self.num)
        new_state.swap_turn()
        new_state.make_move(move)
        self.children[move] = new_state
        return new_state


class Game(Board):
    def __init__(self, map, turn, move=None, options={i for i in range(7)}, n=0, x=0, o=0) -> None:
        super().__init__(map, turn, move, options, n, x, o)
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
            self.update_number(col)
            self.move = (col, row)
        else:
            print("Column already filled")
            self.user_turn()

    def computer_turn(self):
        self.begin_state = State(self.map, '0', self.move, self.options.copy())
        self.look_ahead(self.begin_state)
        best_move = self.begin_state.best_move()
        col = self.place(best_move[1])
        self.update_number(best_move[1])
        if col == 0:
            self.options.remove(best_move[1])
        self.move = (best_move[1], col)
        self.unique, self.found = 0, 0
        print(f"Computer plays at {self.move[0] + 1}")
        self.begin_state = None
        self.state_pool = dict()

    def play(self):
        self.display_number()
        while not self.end_game():
            self.turn = 'X' if self.turn == '0' else '0'
            self.user_turn()
            print(self.num, self.move_val)
            self.display_number()

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
                    self.display_number()
                    print(self.num, self.move_val)

                    if not self.end_game():
                        self.turn = '0'
                        self.user_turn()
                        self.display_number()
                        print(self.num, self.move_val)

                else:
                    self.turn = '0'
                    self.user_turn()
                    self.display_number()
                    print(self.num, self.move_val)

                    if not self.end_game():
                        self.turn = 'X'
                        self.computer_turn()
                        self.display_number()
                        print(self.num, self.move_val)

            go = input(("press any key to continue, or 'q' to quit"))
            counter += 1

    def look_ahead(self, state: State, depth=0):
        for s in state.options:
            new_state = state.make_child(s)
            board_id = ''.join(elem for elem in new_state.map)
            if board_id in self.state_pool:
                state.children[s] = self.state_pool[board_id]
                self.found += 1
            else:
                self.unique += 1
                if new_state.check_win():
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
    # print(game.map)
    # game.train()
    # print(game.total_states)
    # game.num = 16472437332222276
    # game.num = 3099366828 
    # game.num = 44
    # game.play_versus_computer()
    # game.play()
    # game.move_val = 81
    # game.num = 122
    # print(game.check_down(4))
    # game.display_number()
    # to_base_3(14)