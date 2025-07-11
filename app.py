from fastapi import FastAPI
from fastapi.responses import FileResponse
from main import Game

game = Game()
app = FastAPI()


@app.get("/")
async def get_ui():
    return FileResponse("index.html")


@app.get("/styles.css")
async def get_styles():
    return FileResponse("styles.css")


@app.get("/script.js")
async def get_script():
    return FileResponse("script.js")


# Add type hints to rows and cols to ensure FastAPI parses them as integers
@app.post("/start")
async def start(rows: int, cols: int):
    # The game.start method returns True/False, so we'll return a dictionary
    # to indicate success and potentially the board state for the UI.
    success = game.start(rows, cols)
    if success:
        # Return the initial board state along with success status
        return {"success": True, "board": game.board, "rows": game.rows, "cols": game.cols}
    return {"success": False}


# Add type hints to x and y
@app.post("/remove")
async def remove(x: int, y: int):
    success = game.remove(x, y)
    if success:
        # Return the updated board state after a successful remove
        return {"success": True, "board": game.board}
    return {"success": False}


@app.post("/undo")
async def undo():
    success = game.undo()
    if success:
        # Return the updated board state after a successful undo
        return {"success": True, "board": game.board}
    return {"success": False}


@app.post("/lost")
async def lost():
    # This endpoint returns a boolean directly, which is fine.
    return game.lost()


@app.post("/computer_move")
async def computer_move():
    success = game.computer_move()
    if success:
        # Return the updated board state after a successful computer move
        return {"success": True, "board": game.board}
    return {"success": False}


# Add a new GET endpoint to fetch the current board state
# This is crucial for synchronizing the UI with the backend after any move
# or when the page loads/refreshes.
@app.get("/get_board_state")
async def get_board_state():
    return {"board": game.board, "rows": game.rows, "cols": game.cols, "rem": game.rem}
