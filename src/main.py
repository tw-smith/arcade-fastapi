
from fastapi import FastAPI
from .routers import auth_routes, highscore_routes




app = FastAPI()
app.include_router(auth_routes.router)
app.include_router(highscore_routes.router)





