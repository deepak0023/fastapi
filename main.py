from fastapi import FastAPI
import models
from database import engine
from routers import todos

# Get fastapi instance
app = FastAPI()

# creates the required table in db based on models file configuration
models.Base.metadata.create_all(bind = engine)

app.include_router(todos.router)