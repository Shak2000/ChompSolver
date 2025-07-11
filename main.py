import random


class Game:
    def __init__(self):
        self.board = []
        self.rows = 0
        self.cols = 0
        self.rem = 0
        self.history = []
        self.current_player = "Player 1"  # New: Track current player
        self.winner = None  # New: Track winner

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
        self.current_player = "Player 1"  # Reset to Player 1 for new game
        self.winner = None  # Reset winner
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
        self.history.append((current_board_copy, self.current_player))  # Store board and current player

        for i in range(y, self.rows):
            for j in range(x, self.cols):
                if self.board[i][j]:
                    self.board[i][j] = False
                    self.rem -= 1

        # After a successful move, check for win condition and switch player
        if self.lost():
            self.winner = self.current_player  # The player who made the last move wins
        else:
            self.switch_player()  # Switch player only if game is not over
        return True

    def undo(self):
        """
        Undoes the last move by restoring the board from history.
        Returns True if undo was successful, False otherwise.
        """
        if not self.history:
            print("No moves to undo.")
            return False

        previous_board, previous_player = self.history.pop()  # Retrieve previous board and player
        self.board = previous_board
        self.rem = sum(1 for row in self.board for piece in row if piece)
        self.current_player = previous_player  # Revert to the player who was about to move
        self.winner = None  # Clear winner on undo
        print("Move undone.")
        return True

    def lost(self):
        """Checks if the game is lost (only the poison square remains)."""
        # The game is lost if only the poison square (0,0) remains and it's still True
        return self.rem == 1 and self.board[0][0]

    def display_board(self):
        """Prints the current state of the Chomp board (for console)."""
        print("\nCurrent Board:")
        print("   " + " ".join(str(j) for j in range(self.cols)))
        print("  +" + "--" * self.cols)
        for i in range(self.rows):
            row_str = f"{i} |"
            for j in range(self.cols):
                if self.board[i][j]:
                    if i == 0 and j == 0:
                        row_str += "P "  # 'P' for Poison square
                    else:
                        row_str += "C "  # 'C' for existing Chocolate
                else:
                    row_str += "  "  # ' ' for removed chocolate
            print(row_str)
        print(f"Remaining pieces: {self.rem}\n")
        print(f"Current Turn: {self.current_player}")
        if self.winner:
            print(f"Winner: {self.winner}!")

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
        Checks if the given temporary board is a 1xN or Nx1 shape (excluding 1x1).
        This is a simplified check for the computer's strategy.
        """
        active_rows = [any(temp_board[r]) for r in range(temp_rows)]
        active_cols = [any(temp_board[r][c] for r in range(temp_rows)) for c in range(temp_cols)]

        num_active_rows = sum(active_rows)
        num_active_cols = sum(active_cols)

        if self.rem == 1 and self.board[0][0]:  # If only poison square remains
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
            return False

        best_moves = []
        other_moves = []

        for move_x, move_y in valid_moves:
            temp_game = Game()
            temp_game.start(self.rows, self.cols)
            temp_game.board = [[self.board[r][c] for c in range(self.cols)] for r in range(self.rows)]
            temp_game.rem = self.rem

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

        chosen_move = None
        if best_moves:
            chosen_move = random.choice(best_moves)
        elif other_moves:
            chosen_move = random.choice(other_moves)

        if chosen_move:
            print(f"Computer chooses to remove ({chosen_move[0]}, {chosen_move[1]})")
            # Perform the actual move and then switch player
            success = self.remove(chosen_move[0], chosen_move[1])
            return success
        else:
            print("Computer has no valid moves to make (only poison square remains).")
            return False

    def switch_player(self):
        """Switches the current player."""
        self.current_player = "Player 2" if self.current_player == "Player 1" else "Player 1"


# The main function for console interaction is no longer strictly needed for the web app,
# but can be kept for direct console testing.
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
                if game.winner:  # Check for winner after displaying board
                    print(f"Game Over! {game.winner} wins!")
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
                                continue
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
                        # If computer_move returns False, it means there are no valid non-poison moves.
                        # The game ends, and the current player (who forced this state) wins.
                        game.winner = game.current_player  # Set the current player as winner
                        print("The computer has no valid moves left. You win!")
                        break  # Break out of current game loop
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
