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
async def start(rows, cols):
    return game.start(rows, cols)


@app.post("/remove")
async def remove(x, y):
    return game.remove(x, y)


@app.post("/undo")
async def undo():
    return game.undo()


@app.post("/lost")
async def lost():
    return game.lost()


@app.post("/computer_move")
async def computer_move():
    return game.computer_move()
