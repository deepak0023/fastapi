from fastapi import FastAPI
from database import engine
from routers import todos, auth, admin

# Get fastapi instance
app = FastAPI()

# creates the required table in db based on models file configuration
# models.Base.metadata.create_all(bind = engine)

app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(admin.router)