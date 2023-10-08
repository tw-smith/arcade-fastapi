
from fastapi import FastAPI
from .routers import auth_routes




app = FastAPI()
app.include_router(auth_routes.router)





