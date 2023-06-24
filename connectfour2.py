import random
import copy


class State:
    def __init__(self, board, unfilled, turn, move=None) -> None:
          
        self.board = board
        self.unfilled = unfilled
        self.turn = turn
        self.move = move
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

    def display(self):
        print(self.board[0], self.board[1], self.board[2])
        print(self.board[3], self.board[4], self.board[5])
        print(self.board[6], self.board[7], self.board[8])


class Game:
    def __init__(self, board, turn) -> None:
        self.board = board
        self.turn = turn
        self.move = None
        self.state_pool = dict()
        self.cur_state = None
        self.begin_state = None
        self.options = {i for i in range(7)}

    def reset(self):
        self.board = [[' ' for _ in range(6)] for _ in range(7)]
        self.turn = 'X'
        self.move = None

    def update_data(self, state: State):
        print('current state ---- \n Weight: ', state.weight, '\n Move: ', state.move)
        state.display()
        for child in state.children.values():
            print('Weight: ', child.weight, ', Move: ', child.move)

    def display(self):
        board = self.board
        if self.cur_state:
            board = self.cur_state.board
        for i in range(6):
            str = ''
            for y in range(7):
                if board[y][i] == ' ':
                    str += '.'
                else:
                    str += board[y][i]
            print(str)
        # for row in board:
        #     print(' '.join(row))


    def empty(self, pos):
        return self.board[pos][0] == ' '

    def place(self, pos):
        board, turn = self.board, self.turn
        if self.cur_state:
            board, turn = self.cur_state.board, self.cur_state.turn
        for i in range(6):
            if i == 5 or board[pos][i + 1] != ' ':
                board[pos][i] = turn
                return i

    def check_win(self):
        if self.move is None:
            return False
        return self.vertical_win() or self.horizontal_win() or self.diagonal_win()

    def vertical_win(self):
        board, move, turn = self.board, self.move, self.turn
        if self.cur_state:
            board, move, turn = self.cur_state.board, self.cur_state.move, self.cur_state.turn
        ranges = self.straight_ranges(max(0, move[1] - 3), min(5, move[1] + 3))
        for range in ranges:
            if all(board[move[0]][r] == turn for r in range):
                return True
        return False

    def horizontal_win(self):
        board, move, turn = self.board, self.move, self.turn
        if self.cur_state:
            board, move, turn = self.cur_state.board, self.cur_state.move, self.cur_state.turn
        ranges = self.straight_ranges(max(0, move[0] - 3), min(6, move[0] + 3))
        for range in ranges:
            if all(board[c][move[1]] == turn for c in range):
                return True
        return False

    def diagonal_win(self):
        board, turn = self.board, self.turn
        if self.cur_state:
            board, turn = self.cur_state.board, self.cur_state.turn
        for dir in self.diagonal_ranges():
            for i in range(len(dir) - 3):
                if all(board[dir[j][0]][dir[j][1]] == turn for j in range(i, i + 4)):
                    return True
        return False

    def check_draw(self):
        for row in self.board:
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
        move = self.move
        if self.cur_state:
            move = self.cur_state.move
        fronthand_ranges = []
        backhand_ranges = []

        lat, lon = move
        for _ in range(4):
            if lat >= 0 and lon >= 0:
                fronthand_ranges.append((lat, lon))
                lat -= 1
                lon -= 1

        fronthand_ranges.reverse()
        lat, lon = move
        for _ in range(3):
            if lat < 6 and lon < 5:
                lat += 1
                lon += 1
                fronthand_ranges.append((lat, lon))

        lat, lon = move
        for _ in range(4):
            if lat >= 0 and lon < 6:
                backhand_ranges.append((lat, lon))
                lat -= 1
                lon += 1

        backhand_ranges.reverse()
        lat, lon = move
        for _ in range(3):
            if lat < 6 and lon >= 1:
                lat += 1
                lon -= 1
                backhand_ranges.append((lat, lon))

        return fronthand_ranges, backhand_ranges

    def end_game(self):
        if self.check_win():
            print(f"Player {self.turn} wins!")
            return True
        if self.check_draw():
            print("Draw!")
            return True
        return False

    def user_turn(self):
        col = int(input(f"Player {self.turn}, enter position: ")) - 1
        if col < 0 or col > 6:
            print("Position out of range!")
            self.user_turn()
        if self.empty(col):
            row = self.place(col)
            self.move = (col, row)
        else:
            print("Column")
            self.user_turn()

    def computer_turn(self):
        self.begin_state = State(copy.deepcopy(self.board), copy.deepcopy(self.options), self.turn)
        self.cur_state = self.begin_state
        self.look_ahead(self.begin_state)
        best_move = self.begin_state.best_move()
        print(f"Computer plays at {self.move}")
        col = self.place(best_move[1])
        self.move = (col, best_move[1])
        self.cur_state, self.begin_state = None, None

    def play(self):
        self.display()
        while not self.end_game():
            self.turn = 'X' if self.turn == '0' else '0'
            self.user_turn()
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
                    self.computer_turn()
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
                        self.computer_turn()
                        self.display()

            go = input(("press any key to continue, or 'q' to quit"))
            counter += 1

    def look_ahead(self, state: State, depth=0):
        print(depth)
        print(state.unfilled)

        for s in state.unfilled:
            new_board = copy.deepcopy(state.board)
            new_unfilled = copy.deepcopy(state.unfilled)
            new_turn = 'X' if state.turn == '0' else '0'
            new_move = s

            col = self.place(new_move)
            board_id = str(new_board) + new_turn
            if board_id in self.state_pool:
                state.children[new_move] = self.state_pool[board_id]
            else:
                new_state = State(new_board, new_unfilled, new_turn, (col, new_move))
                self.cur_state = new_state
                state.children[new_move] = new_state

                if self.check_win():
                    new_state.weight = -1 if new_turn == 'X' else 1
                    new_state.offense = new_state.weight
                elif self.check_draw() or depth == 6:
                    new_state.weight = 0
                    new_state.offense = 0
                else:
                    self.look_ahead(new_state, depth + 1)

                self.state_pool[board_id] = new_state
        
        state.weight = min(state.children[child].weight for child in state.children)
        if state.turn == 'X':
            state.weight = max(state.children[child].weight for child in state.children)
        state.offense = round(sum(state.children[child].offense for child in state.children)/len(state.children), 3)

    def display_tree(self, state: State, indent=0, count=0):
        if count < 2:  
            print(' ' * indent, state.weight)
            self.board = state.board
            self.display()
            print("--------------")
            for child in state.children:
                self.display_tree(state.children[child], indent + 2, count + 1)


if __name__ == "__main__":
    game = Game([[' ' for _ in range(6)] for _ in range(7)], 'X')
    # game.train()
    # print(game.total_states)
    # game.play_versus_computer()
    game.play()