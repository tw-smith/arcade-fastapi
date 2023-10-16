
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_routes, highscore_routes, lobby_routes




app = FastAPI()
allowed_origins = [
    'http://localhost:4200' #TODO remove hardcoded cors origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=['GET', 'POST']
)


app.include_router(auth_routes.router)
app.include_router(highscore_routes.router)
app.include_router(lobby_routes.router)





