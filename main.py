class Game:
    def __init__(self):
        self.board = []
        self.rows = False
        self.cols = False
        self.rem = 0
        self.history = []

    def start(self, rows, cols):
        self.board = [[True for j in range(cols)] for i in range(rows)]
        self.rows = rows
        self.cols = cols
        self.rem = self.rows * self.cols

    def remove(self, x, y):
        if not (0 <= x < self.cols and 0 <= y < self.rows and self.board[y][x]):
            return False
        self.history.append([[self.board[i][j] for j in range(self.cols)] for i in range(self.rows)])
        for i in range(y, self.rows):
            for j in range(x, self.cols):
                self.board[i][j] = False
                self.rem -= 1
        return True

    def lost(self):
        return self.rem == 1

    def computer_move(self):
        if not self.board[0][1]:
            self.remove(1, 0)
        elif not self.board[1][0]:
            self.remove(0, 1)


def main():
    print("Welcome to the Chomp Solver!")


if __name__ == "__main__":
    main()
