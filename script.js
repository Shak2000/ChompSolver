document.addEventListener('DOMContentLoaded', () => {
    const gameSetupDiv = document.getElementById('game-setup');
    const gameContainerDiv = document.getElementById('game-container');
    const rowsInput = document.getElementById('rows-input');
    const colsInput = document.getElementById('cols-input');
    const startGameBtn = document.getElementById('start-game-btn');
    const boardDisplay = document.getElementById('board-display');
    const gameMessages = document.getElementById('game-messages');
    const computerMoveBtn = document.getElementById('computer-move-btn');
    const undoMoveBtn = document.getElementById('undo-move-btn');
    const newGameBtn = document.getElementById('new-game-btn');
    const quitGameBtn = document.getElementById('quit-game-btn');
    const currentTurnDisplay = document.getElementById('current-turn-display'); // New element

    // Message Modal Elements
    const messageModal = document.getElementById('message-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const modalCloseBtn = document.getElementById('modal-close-btn');

    let currentBoard = [];
    let boardRows = 0;
    let boardCols = 0;
    let currentPlayer = "Player 1"; // Frontend tracking of current player
    let gameWinner = null; // Frontend tracking of winner

    // Function to show a custom message box
    function showMessageBox(title, message, isGameOver = false) {
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        messageModal.classList.remove('hidden');
        if (isGameOver) {
            modalCloseBtn.textContent = 'New Game'; // Change button text for game over
            modalCloseBtn.onclick = () => {
                messageModal.classList.add('hidden');
                newGameBtn.click(); // Trigger new game
            };
        } else {
            modalCloseBtn.textContent = 'OK';
            modalCloseBtn.onclick = () => {
                messageModal.classList.add('hidden');
            };
        }
    }

    // Helper to fetch data from API
    async function fetchData(url, method = 'GET', body = null) {
        try {
            const options = { method };
            if (body) {
                options.headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
                options.body = new URLSearchParams(body);
            }
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! Status: ${response.status}, Message: ${errorText}`);
            }
            return response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            showMessageBox('Error', `Failed to communicate with the server: ${error.message}. Please try again.`);
            return null;
        }
    }

    // Render the board dynamically
    function renderBoard() {
        boardDisplay.innerHTML = ''; // Clear existing board
        boardDisplay.style.gridTemplateColumns = `repeat(${boardCols}, 1fr)`;

        for (let r = 0; r < boardRows; r++) {
            for (let c = 0; c < boardCols; c++) {
                const cell = document.createElement('div');
                cell.classList.add('board-cell');
                cell.dataset.row = r;
                cell.dataset.col = c;

                if (currentBoard[r] && currentBoard[r][c]) {
                    if (r === 0 && c === 0) {
                        cell.classList.add('poison');
                        cell.textContent = 'P'; // Mark poison square
                    } else {
                        cell.classList.add('chocolate');
                        cell.textContent = 'C'; // Mark chocolate square
                    }
                    // Only add click listener if game is not over and it's a chocolate piece
                    if (!gameWinner) {
                        cell.addEventListener('click', handleCellClick);
                    }
                } else {
                    cell.classList.add('removed');
                }
                boardDisplay.appendChild(cell);
            }
        }
        updateTurnDisplay(); // Update turn display after rendering board
    }

    // Update the turn display
    function updateTurnDisplay() {
        if (gameWinner) {
            currentTurnDisplay.textContent = `Game Over! Winner: ${gameWinner}!`;
            currentTurnDisplay.classList.add('text-green-700'); // Highlight winner
            currentTurnDisplay.classList.remove('text-gray-800');
        } else {
            currentTurnDisplay.textContent = `Current Turn: ${currentPlayer}`;
            currentTurnDisplay.classList.remove('text-green-700');
            currentTurnDisplay.classList.add('text-gray-800');
        }
    }

    // Handle starting a new game
    startGameBtn.addEventListener('click', async () => {
        const rows = parseInt(rowsInput.value);
        const cols = parseInt(colsInput.value);

        if (isNaN(rows) || isNaN(cols) || rows <= 0 || cols <= 0) {
            showMessageBox('Invalid Input', 'Please enter valid positive numbers for rows and columns.');
            return;
        }

        const result = await fetchData(`/start?rows=${rows}&cols=${cols}`, 'POST');

        if (result && result.success) {
            boardRows = result.rows;
            boardCols = result.cols;
            currentBoard = result.board;
            currentPlayer = result.current_player; // Get current player from backend
            gameWinner = result.winner; // Get winner (should be null initially)

            gameSetupDiv.classList.add('hidden');
            gameContainerDiv.classList.remove('hidden');
            renderBoard();
            gameMessages.textContent = 'Game started! Your turn.';
            enableGameControls();
        } else {
            showMessageBox('Game Error', 'Failed to start the game. Please check server logs.');
        }
    });

    // Handle cell click for player move
    async function handleCellClick(event) {
        const row = parseInt(event.target.dataset.row);
        const col = parseInt(event.target.dataset.col);

        if (row === 0 && col === 0) {
            showMessageBox('Invalid Move', 'You cannot remove the poison square (0,0)!');
            return;
        }

        const result = await fetchData(`/remove?x=${col}&y=${row}`, 'POST');

        if (result && result.success) {
            currentBoard = result.board;
            currentPlayer = result.current_player; // Update current player
            gameWinner = result.winner; // Check for winner

            renderBoard();
            if (gameWinner) {
                showMessageBox('Game Over!', `All chocolate squares have been eaten! The poison square (0,0) remains. ${gameWinner} WINS!`, true);
                gameMessages.textContent = `${gameWinner} WINS!`;
                disableGameControls();
            } else {
                gameMessages.textContent = `You removed (${col}, ${row}). ${currentPlayer}'s turn.`;
            }
        } else {
            showMessageBox('Invalid Move', 'That square is already removed or out of bounds. Try again.');
        }
    }

    // Handle computer move
    computerMoveBtn.addEventListener('click', async () => {
        gameMessages.textContent = 'Computer is thinking...';
        const result = await fetchData('/computer_move', 'POST');

        if (result && result.success) {
            currentBoard = result.board;
            currentPlayer = result.current_player; // Update current player
            gameWinner = result.winner; // Check for winner

            renderBoard();
            if (gameWinner) {
                showMessageBox('Game Over!', `The computer has left only the poison square. ${gameWinner} WINS!`, true);
                gameMessages.textContent = `${gameWinner} WINS!`;
                disableGameControls();
            } else {
                gameMessages.textContent = `Computer made a move. ${currentPlayer}'s turn.`;
            }
        } else {
            // Computer could not make a move (only poison square remains), meaning current player wins
            const data = await fetchData('/get_board_state', 'GET'); // Fetch state to get current player
            if (data) {
                 gameWinner = data.current_player; // The current player wins if computer can't move
                 currentBoard = data.board;
                 boardRows = data.rows;
                 boardCols = data.cols;
                 renderBoard(); // Re-render to show final board
                 showMessageBox('Game Over!', `Computer could not make a move (only poison square remains). ${gameWinner} WINS!`, true);
                 gameMessages.textContent = `${gameWinner} WINS!`;
                 disableGameControls();
            } else {
                showMessageBox('Error', 'Failed to determine game state after computer move failure.');
            }
        }
    });

    // Handle undo move
    undoMoveBtn.addEventListener('click', async () => {
        const result = await fetchData('/undo', 'POST');
        if (result && result.success) {
            currentBoard = result.board;
            currentPlayer = result.current_player; // Revert to previous player
            gameWinner = result.winner; // Clear winner on undo
            renderBoard();
            gameMessages.textContent = 'Move undone. Your turn.';
            enableGameControls(); // Re-enable controls after undo
        } else {
            showMessageBox('Undo Error', 'No moves to undo.');
        }
    });

    // Handle new game button
    newGameBtn.addEventListener('click', () => {
        gameContainerDiv.classList.add('hidden');
        gameSetupDiv.classList.remove('hidden');
        rowsInput.value = '';
        colsInput.value = '';
        gameMessages.textContent = '';
        gameWinner = null; // Clear winner
        currentPlayer = "Player 1"; // Reset player
        enableGameControls(); // Ensure controls are enabled for a new game
        updateTurnDisplay(); // Reset turn display
    });

    // Handle quit game button
    quitGameBtn.addEventListener('click', () => {
        showMessageBox('Goodbye!', 'Thanks for playing Chomp Solver!');
        disableGameControls();
        setTimeout(() => {
            gameContainerDiv.classList.add('hidden');
            gameSetupDiv.classList.remove('hidden');
            rowsInput.value = '';
            colsInput.value = '';
            gameMessages.textContent = '';
            gameWinner = null;
            currentPlayer = "Player 1";
            updateTurnDisplay();
        }, 2000);
    });

    // Function to disable game controls after game ends
    function disableGameControls() {
        computerMoveBtn.disabled = true;
        undoMoveBtn.disabled = true;
        boardDisplay.querySelectorAll('.board-cell.chocolate').forEach(cell => {
            cell.removeEventListener('click', handleCellClick);
            cell.style.cursor = 'default';
        });
    }

    // Function to enable game controls for a new game
    function enableGameControls() {
        computerMoveBtn.disabled = false;
        undoMoveBtn.disabled = false;
        boardDisplay.querySelectorAll('.board-cell.chocolate').forEach(cell => {
            cell.addEventListener('click', handleCellClick);
            cell.style.cursor = 'pointer';
        });
    }

    updateTurnDisplay(); // Initialize turn display even before game starts
});
