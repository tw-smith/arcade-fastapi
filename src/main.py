from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_routes, highscore_routes, lobby_routes, lobby_events, game_events
from src.websocket_dependencies import socket_app
from src.config.config import settings


app = FastAPI()


#socket_manager.mount_to("/", app)
allowed_origins = [
    'http://127.0.0.1:7000'
    'http://localhost:4200/*' #TODO remove hardcoded cors origin
    'http://localhost:4200/lobbies',
    'localhost:4200',
    'https://arcade2.tw-smith.me',
    'https://arcade.tw-smith.me'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:4200', 'https://arcade2.tw-smith.me', 'https://arcade.tw-smith.me'],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


app.include_router(auth_routes.router, prefix=settings.route_prefix)
app.include_router(highscore_routes.router, prefix=settings.route_prefix)
app.include_router(lobby_routes.router, prefix=settings.route_prefix)
app.include_router(lobby_events.router, prefix=settings.route_prefix)
app.include_router(game_events.router, prefix=settings.route_prefix)
app.mount("", socket_app)





