import random
import copy


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
        self.move = (col, pos)
        if col == 5:
            self.options.remove(pos)

    def place(self, pos):
        for i in range(6):
            if i == 5 or self.map[pos][i + 1] != ' ':
                self.map[pos][i] = self.turn
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

class State:
    def __init__(self, board) -> None:
        self.board = board
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

    def procreate(self):
        for move in self.board.unfilled:
            self.make_child(move)

    def make_child(self, move):
        new_board = copy.deepcopy(self.board)
        new_board.make_move(move)
        new_board.swap_turn()
        new_state = State(new_board)
        self.children[move] = new_state
        return new_state


class Game:
    def __init__(self, board, turn) -> None:
        self.board = board
        self.turn = turn
        self.move = None
        self.state_pool = dict()
        self.begin_state = None
        self.options = {i for i in range(7)}

    def user_turn(self):
        col = int(input(f"Player {self.turn}, enter position: ")) - 1
        if col < 0 or col > 6:
            print("Position out of range!")
            self.user_turn()
        if self.board.empty(col):
            row = self.board.place(col)
            self.move = (col, row)
        else:
            print("Column")
            self.user_turn()

    def computer_turn(self):
        self.begin_state = State(copy.deepcopy(self.board))
        self.look_ahead(self.begin_state)
        best_move = self.begin_state.best_move()
        print(f"Computer plays at {self.move}")
        col = self.place(best_move[1])
        self.move = (col, best_move[1])
        self.begin_state = None
        self.state_pool = dict()

    def play(self):
        self.board.display()
        while not self.board.end_game():
            self.turn = 'X' if self.turn == '0' else '0'
            self.user_turn()
            self.board.display()

    def play_versus_computer(self):
        counter = 0
        while True:
            self.turn = '0'
            if counter % 2 == 0:
                self.turn = 'X'
            while not self.board.end_game():
                if self.turn == '0':
                    self.turn = 'X'
                    self.computer_turn()
                    self.display()

                    if not self.board.end_game():
                        self.turn = '0'
                        self.user_turn()
                        self.display()

                else:
                    self.turn = '0'
                    self.user_turn()
                    self.board.display()

                    if not self.board.end_game():
                        self.turn = 'X'
                        self.computer_turn()
                        self.display()

            go = input(("press any key to continue, or 'q' to quit"))
            counter += 1

    def look_ahead(self, state: State, depth=0):

        for s in state.board.options:
            new_state = state.make_child(s)
            board_id = ''.join([str(elem) for sublist in new_state.board.map for elem in sublist])
            if board_id in self.state_pool:
                state.children[s] = self.state_pool[board_id]
            else:
                if new_state.board.check_win():
                    new_state.weight = -1 if new_state.turn == 'X' else 1
                    new_state.offense = new_state.weight
                elif new_state.board.check_draw() or depth == 6:
                    new_state.weight = 0
                    new_state.offense = 0
                else:
                    self.look_ahead(new_state, depth + 1)

                self.state_pool[board_id] = new_state
        
        state.weight = min(state.children[child].weight for child in state.children)
        if state.turn == 'X':
            state.weight = max(state.children[child].weight for child in state.children)
        state.offense = round(sum(state.children[child].offense for child in state.children)/len(state.children), 3)


if __name__ == "__main__":
    game = Game(Board([[' ' for _ in range(6)] for _ in range(7)], 'X'), 'X')
    # game.train()
    # print(game.total_states)
    # game.play_versus_computer()
    game.play()