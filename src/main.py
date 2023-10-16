
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_routes, highscore_routes, lobby_routes




app = FastAPI()
allowed_origins = [
    'http://127.0.0.1:7000'
    'http://localhost:4200/*' #TODO remove hardcoded cors origin
    'http://localhost:4200/lobbies',
    'localhost:4200'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins='http://localhost:4200',
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


app.include_router(auth_routes.router)
app.include_router(highscore_routes.router)
app.include_router(lobby_routes.router)





