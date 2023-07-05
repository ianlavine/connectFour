import random
import copy
import math
import time


class Board:
    def __init__(self, board, turn, move=None, options={0,1,2,3,4,5,6}) -> None:
        self.map = board
        self.turn = turn
        self.move = move
        self.options = options

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
    
    def empty(self, pos):
        return self.map[pos][0] == ' '

    def swap_turn(self):
        self.turn = 'X' if self.turn == '0' else '0'

    def make_move(self, pos):
        col = self.place(pos)
        self.move = (pos, col)
        if col == 0:
            self.options.remove(pos)

    def place(self, pos):
        for i in range(6):
            if i == 5 or self.map[pos][i + 1] != ' ':
                print
                self.map[pos] = self.map[pos][:i] + self.turn + self.map[pos][i+1:]
                return i

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
    def __init__(self, map, turn, move=None, options={i for i in range(7)}) -> None:
        super().__init__(map, turn, move, options)
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
        new_state = State(new_map, self.turn, options=new_options)
        new_state.swap_turn()
        new_state.make_move(move)
        self.children[move] = new_state
        return new_state


class Game(Board):
    def __init__(self, map, turn, move=None, options={i for i in range(7)}) -> None:
        super().__init__(map, turn, move, options)
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
            self.move = (col, row)
        else:
            print("Column already filled")
            self.user_turn()

    def computer_turn(self):
        self.begin_state = State(self.map, '0', self.move, self.options.copy())
        self.look_ahead(self.begin_state)
        best_move = self.begin_state.best_move()
        col = self.place(best_move[1])
        if col == 0:
            self.options.remove(best_move[1])
        self.move = (best_move[1], col)
        self.unique, self.found = 0, 0
        print(f"Computer plays at {self.move[0] + 1}")
        self.begin_state = None
        self.state_pool = dict()

    def play(self):
        self.display()
        while not self.end_game():
            self.turn = 'X' if self.turn == '0' else '0'
            self.user_turn()
            print(self.num, self.move_val)
            self.display()

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
                    self.display()

                    if not self.end_game():
                        self.turn = '0'
                        self.user_turn()
                        self.display()

                else:
                    self.turn = '0'
                    self.user_turn()
                    self.display()

                    if not self.end_game():
                        self.turn = 'X'
                        start = time.time()
                        self.computer_turn()
                        end = time.time()
                        print(end - start)
                        self.display()

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
    game.play_versus_computer()
    # game.play()
    # game.move_val = 81
    # game.num = 122
    # print(game.check_down(4))
    # game.display_number()
    # to_base_3(14)