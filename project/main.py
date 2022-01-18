from typing import List, Optional
from fastapi import FastAPI, Form, Request, Depends
from pydantic import BaseModel
from starlette.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocket, WebSocketDisconnect
import models
from starlette_wtf import csrf_protect 
from db import SessionLocal, engine
from forms import User
from models import User
from sqlalchemy.orm import Session

class Item(BaseModel):
    name:str
    price:float
    is_offer: Optional[bool]=None

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket]=[]


    async def connect (self, websocket:WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)


    async def disconnect(self, websocket:WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket:WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message:str):
        for connection in self.active_connections:
            await connection.send_text(message)

        
app=FastAPI()
templates = Jinja2Templates(directory="templates")
manager=ConnectionManager()
models.Base.metadata.create_all(bind=engine)

@app.get("/start")
async def reed_root():
    return {"Hello":"World"}

@app.get("/items/{item_id}")
async def read_item(item_id:int, q:Optional[str]=None ):
    return {"item_id": item_id, "q":q}


@app.put("/items/{item_id}")
async def update_item(item_id: int, item:Item):
    return {"item_price": item.price, "item_id":item_id} 


@app.get("/chat")
async def open_chat(request:Request):
    
    return templates.TemplateResponse("chat.html", {"request":request})

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket:WebSocket, client_id:int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
        
@app.route('/', methods=['GET', 'POST'])

async def index(request):
    """GET|POST /: form handler
    """
    form = await User.from_formdata(request)
    
    if await form.validate_on_submit():
        print(form.name.data)
        return PlainTextResponse('SUCCESS')
    return templates.TemplateResponse("login.html", {"request":request, "form":form})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/get_user/')
async def get_user( user_id: int,db: Session = Depends(get_db)):
    print(db.query(models.User).filter(models.User.id == user_id).first())
    return db.query(models.User).filter(models.User.id == user_id).first()

