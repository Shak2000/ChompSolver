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


@app.post("/start")
async def start(rows: int, cols: int):
    success = game.start(rows, cols)
    if success:
        return {
            "success": True,
            "board": game.board,
            "rows": game.rows,
            "cols": game.cols,
            "current_player": game.current_player,
            "winner": game.winner
        }
    return {"success": False}


@app.post("/remove")
async def remove(x: int, y: int):
    success = game.remove(x, y)
    if success:
        return {"success": True, "board": game.board, "current_player": game.current_player, "winner": game.winner}
    return {"success": False}


@app.post("/undo")
async def undo():
    success = game.undo()
    if success:
        return {"success": True, "board": game.board, "current_player": game.current_player, "winner": game.winner}
    return {"success": False}


@app.post("/lost")
async def lost():
    # This endpoint can still return just the boolean, but the winner info will be in other calls
    return game.lost()


@app.post("/computer_move")
async def computer_move():
    success = game.computer_move()
    if success:
        return {"success": True, "board": game.board, "current_player": game.current_player, "winner": game.winner}
    return {"success": False}


@app.get("/get_board_state")
async def get_board_state():
    return {
        "board": game.board,
        "rows": game.rows,
        "cols": game.cols,
        "rem": game.rem,
        "current_player": game.current_player,
        "winner": game.winner
    }
