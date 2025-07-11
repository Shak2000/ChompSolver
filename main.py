import random


class Game:
    def __init__(self):
        self.board = []
        self.rows = 0
        self.cols = 0
        self.rem = 0
        self.history = []

    def start(self, rows, cols):
        """Initializes a new Chomp game board."""
        if rows <= 0 or cols <= 0:
            print("Board dimensions must be positive integers.")
            return False
        self.rows = rows
        self.cols = cols
        self.board = [[True for _ in range(cols)] for _ in range(rows)]
        self.rem = self.rows * self.cols
        self.history = []
        return True

    def remove(self, x, y):
        """
        Removes the chocolate square at (x, y) and all squares to its right and below.
        Returns True if the move was valid and executed, False otherwise.
        """
        # Prevent removal of the poison square (0,0)
        if x == 0 and y == 0:
            return False

        if not (0 <= x < self.cols and 0 <= y < self.rows and self.board[y][x]):
            return False

        current_board_copy = [[self.board[i][j] for j in range(self.cols)] for i in range(self.rows)]
        self.history.append(current_board_copy)

        for i in range(y, self.rows):
            for j in range(x, self.cols):
                if self.board[i][j]:
                    self.board[i][j] = False
                    self.rem -= 1
        return True

    def undo(self):
        """
        Undoes the last move by restoring the board from history.
        Returns True if undo was successful, False otherwise.
        """
        if not self.history:
            print("No moves to undo.")
            return False

        previous_board = self.history.pop()
        self.board = previous_board
        self.rem = sum(1 for row in self.board for piece in row if piece)
        print("Move undone.")
        return True

    def lost(self):
        """Checks if the game is lost (only the poison square remains)."""
        # The game is lost if only the poison square (0,0) remains and it's still True
        # This condition means the player who made the last move left only (0,0)
        return self.rem == 1 and self.board[0][0]

    def display_board(self):
        """Prints the current state of the Chomp board."""
        print("\nCurrent Board:")
        print("   " + " ".join(str(j) for j in range(self.cols)))
        print("  +" + "--" * self.cols)
        for i in range(self.rows):
            row_str = f"{i} |"
            for j in range(self.cols):
                if self.board[i][j]:
                    if i == 0 and j == 0:
                        row_str += "X "  # 'X' for poison square
                    else:
                        row_str += "C "  # 'C' for existing chocolate
                else:
                    row_str += "  "  # ' ' for removed chocolate
            print(row_str)
        print(f"Remaining pieces: {self.rem}\n")

    def get_valid_moves(self):
        """Returns a list of (x, y) tuples for all currently valid moves."""
        moves = []
        for r in range(self.rows):
            for c in range(self.cols):
                # Exclude the poison square (0,0) from valid moves
                if self.board[r][c] and not (c == 0 and r == 0):
                    moves.append((c, r))
        return moves

    def is_1xn_or_nx1(self, temp_board, temp_rows, temp_cols):
        """
        Checks if the given temporary board is a 1xn or nx1 shape (excluding 1x1).
        This is a simplified check for the computer's strategy.
        """
        active_rows = [any(temp_board[r]) for r in range(temp_rows)]
        active_cols = [any(temp_board[r][c] for r in range(temp_rows)) for c in range(temp_cols)]

        num_active_rows = sum(active_rows)
        num_active_cols = sum(active_cols)

        # If only the poison square remains, it's not a "bad shape" to avoid for the computer,
        # as it signifies the end of the game.
        if self.rem == 1 and self.board[0][0]:
            return False

        if num_active_rows == 1 and num_active_cols > 1:
            return True
        if num_active_cols == 1 and num_active_rows > 1:
            return True
        return False

    def computer_move(self):
        """
        Computer makes a move based on the following strategy:
        1. Prioritize moves that leave an odd number of points.
        2. Among those, prioritize moves that prevent a 1xM or Nx1 (non-1x1) board shape.
        3. If no such move, pick any valid move.
        """
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            # If no valid moves are left (meaning only poison square remains)
            return False

        best_moves = []
        other_moves = []

        for move_x, move_y in valid_moves:
            # Create a temporary game state to simulate the move
            temp_game = Game()
            temp_game.start(self.rows, self.cols)
            temp_game.board = [[self.board[r][c] for c in range(self.cols)] for r in range(self.rows)]
            temp_game.rem = self.rem

            # Simulate the removal (the temp_game.remove method already prevents (0,0))
            # We don't need to check (0,0) here again because get_valid_moves already excludes it.
            for i in range(move_y, temp_game.rows):
                for j in range(move_x, temp_game.cols):
                    if temp_game.board[i][j]:
                        temp_game.board[i][j] = False
                        temp_game.rem -= 1

            leaves_odd = (temp_game.rem % 2 != 0)
            avoids_bad_shape = not self.is_1xn_or_nx1(temp_game.board, temp_game.rows, temp_game.cols)

            if leaves_odd and avoids_bad_shape:
                best_moves.append((move_x, move_y))
            else:
                other_moves.append((move_x, move_y))

        if best_moves:
            chosen_move = random.choice(best_moves)
            print(f"Computer chooses to remove ({chosen_move[0]}, {chosen_move[1]})")
            return self.remove(chosen_move[0], chosen_move[1])
        elif other_moves:
            chosen_move = random.choice(other_moves)
            print(f"Computer chooses to remove ({chosen_move[0]}, {chosen_move[1]})")
            return self.remove(chosen_move[0], chosen_move[1])
        else:
            # This case means get_valid_moves returned moves, but none fit best_moves or other_moves criteria
            # which implies only the poison square is left.
            print("Computer has no valid moves to make (only poison square remains).")
            return False


def main():
    print("Welcome to the Chomp Solver!")
    game = Game()

    while True:
        print("\nMain Menu:")
        print("1. Start a new game")
        print("2. Quit")
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            while True:
                try:
                    rows = int(input("Enter the height (rows) of the board: "))
                    cols = int(input("Enter the width (columns) of the board: "))
                    if game.start(rows, cols):
                        break
                    else:
                        print("Invalid dimensions. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter integers for height and width.")

            while True:
                game.display_board()
                if game.lost():
                    print("All chocolate squares have been eaten! The poison square (0,0) remains.")
                    print("The player who made the last move (leaving only the poison square) wins!")
                    break

                print("\nTurn Options:")
                print("1. Make your move")
                print("2. Have the computer make a move")
                print("3. Undo last move")
                print("4. Start a new game")
                print("5. Quit program")
                turn_choice = input("Enter your choice: ").strip()

                if turn_choice == '1':
                    while True:
                        try:
                            x = int(input("Enter column (x) to remove: "))
                            y = int(input("Enter row (y) to remove: "))
                            if x == 0 and y == 0:
                                print("You cannot remove the poison square (0,0)!")
                                continue  # Ask for input again
                            if game.remove(x, y):
                                print(f"You removed ({x}, {y}).")
                                break
                            else:
                                print("Invalid move. That square is already removed or out of bounds. Try again.")
                        except ValueError:
                            print("Invalid input. Please enter integers for coordinates.")
                elif turn_choice == '2':
                    print("Computer is making a move...")
                    if not game.computer_move():
                        print("Computer could not make a move (only poison square remains).")
                        # If computer_move returns False, it means there are no valid non-poison moves.
                        # The game ends, and the current player (who forced this state) wins.
                        print("The computer has left only the poison square. You win!")
                        break
                elif turn_choice == '3':
                    game.undo()
                elif turn_choice == '4':
                    print("Starting a new game...")
                    break
                elif turn_choice == '5':
                    print("Quitting the program. Goodbye!")
                    return
                else:
                    print("Invalid choice. Please select a valid option.")

        elif choice == '2':
            print("Quitting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter '1' or '2'.")


if __name__ == "__main__":
    main()
