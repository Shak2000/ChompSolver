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

    // Message Modal Elements
    const messageModal = document.getElementById('message-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const modalCloseBtn = document.getElementById('modal-close-btn');

    let currentBoard = [];
    let boardRows = 0;
    let boardCols = 0;

    // Function to show a custom message box
    function showMessageBox(title, message) {
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        messageModal.classList.remove('hidden');
    }

    // Function to hide the custom message box
    modalCloseBtn.addEventListener('click', () => {
        messageModal.classList.add('hidden');
    });

    // Helper to fetch data from API
    async function fetchData(url, method = 'GET', body = null) {
        try {
            const options = { method };
            if (body) {
                options.headers = { 'Content-Type': 'application/x-www-form-urlencoded' }; // Ensure correct content type
                options.body = new URLSearchParams(body);
            }
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! Status: ${response.status}, Message: ${errorText}`);
            }
            return response.json(); // Expect JSON response
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

                // Ensure currentBoard[r] exists before accessing currentBoard[r][c]
                if (currentBoard[r] && currentBoard[r][c]) {
                    if (r === 0 && c === 0) {
                        cell.classList.add('poison');
                        cell.textContent = 'P'; // Mark poison square
                    } else {
                        cell.classList.add('chocolate');
                        cell.textContent = 'C'; // Mark chocolate square
                    }
                    cell.addEventListener('click', handleCellClick);
                } else {
                    cell.classList.add('removed');
                }
                boardDisplay.appendChild(cell);
            }
        }
    }

    // Function to fetch and update the board state from the backend
    async function fetchAndUpdateBoard() {
        const data = await fetchData('/get_board_state', 'GET');
        if (data && data.board) {
            currentBoard = data.board;
            boardRows = data.rows;
            boardCols = data.cols;
            renderBoard();
        } else {
            showMessageBox('Board Error', 'Failed to fetch current board state.');
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
            currentBoard = result.board; // Get the initial board state from the response
            gameSetupDiv.classList.add('hidden');
            gameContainerDiv.classList.remove('hidden');
            renderBoard();
            gameMessages.textContent = 'Game started! Your turn.';
            enableGameControls(); // Ensure controls are enabled for a new game
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
            currentBoard = result.board; // Update board from response
            renderBoard();
            const lost = await fetchData('/lost', 'POST'); // Check if game is lost after player's move
            if (lost) {
                showMessageBox('Game Over!', 'All chocolate squares have been eaten! The poison square (0,0) remains. You WIN!');
                gameMessages.textContent = 'You WIN!';
                disableGameControls();
            } else {
                gameMessages.textContent = `You removed (${col}, ${row}). Computer's turn.`;
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
            currentBoard = result.board; // Update board from response
            renderBoard();
            const lost = await fetchData('/lost', 'POST');
            if (lost) {
                showMessageBox('Game Over!', 'The computer has left only the poison square. You WIN!');
                gameMessages.textContent = 'You WIN!';
                disableGameControls();
            } else {
                gameMessages.textContent = "Computer made a move. Your turn.";
            }
        } else {
            showMessageBox('Computer Move Error', 'Computer could not make a move (only poison square remains). You WIN!');
            gameMessages.textContent = 'You WIN!';
            disableGameControls();
        }
    });

    // Handle undo move
    undoMoveBtn.addEventListener('click', async () => {
        const result = await fetchData('/undo', 'POST');
        if (result && result.success) {
            currentBoard = result.board; // Update board from response
            renderBoard();
            gameMessages.textContent = 'Move undone. Your turn.';
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
        enableGameControls(); // Re-enable controls for a new game
    });

    // Handle quit game button
    quitGameBtn.addEventListener('click', () => {
        showMessageBox('Goodbye!', 'Thanks for playing Chomp Solver!');
        disableGameControls(); // Disable controls immediately
        setTimeout(() => {
            gameContainerDiv.classList.add('hidden');
            gameSetupDiv.classList.remove('hidden');
            rowsInput.value = '';
            colsInput.value = '';
            gameMessages.textContent = '';
        }, 2000); // Go back to setup after 2 seconds
    });

    // Function to disable game controls after game ends
    function disableGameControls() {
        computerMoveBtn.disabled = true;
        undoMoveBtn.disabled = true;
        // The board cells should also be unclickable
        boardDisplay.querySelectorAll('.board-cell.chocolate').forEach(cell => {
            cell.removeEventListener('click', handleCellClick);
            cell.style.cursor = 'default';
        });
    }

    // Function to enable game controls for a new game
    function enableGameControls() {
        computerMoveBtn.disabled = false;
        undoMoveBtn.disabled = false;
        // Re-attach click listeners to chocolate cells
        boardDisplay.querySelectorAll('.board-cell.chocolate').forEach(cell => {
            cell.addEventListener('click', handleCellClick);
            cell.style.cursor = 'pointer';
        });
    }
});
