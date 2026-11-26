from fastapi import APIRouter, Depends, HTTPException, Path
from models.todos import Todos
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user

# Get fastapi instance
router = APIRouter()

# Get db connection for CRUD operation
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length = 3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt = 0, lt=6)
    complete: bool

@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency, user: user_dependency):
    # Authenticate user
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    # Fetch all todo records pertaining to owner/user id except admin
    if user.get('user_role') == 'admin':
        return db.query(Todos).all()
    else:
        return db.query(Todos).filter(Todos.owner_id == user.get('user_id')).all()

@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)):
    # Authenticate user
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    # Fetch specific todo record pertaining to the user/owner except admin
    if user.get('user_role') == 'admin':
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    else:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')

@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest, user: user_dependency):
    # Authenticate user
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    # Get required data from request and add a new todo record
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('user_id'))
    db.add(todo_model)
    db.commit()

@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, user:user_dependency, todo_id: int=Path(gt=0)):
    # Authenticate user
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    # Get the required todo record pertaing to the user/owner except admin
    if user.get('user_role') == 'admin':
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    else:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    # Update the specific record if found with provided request details
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.add(todo_model)
    db.commit()

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, user:user_dependency, todo_id: int = Path(gt=0)):
    # Authenticate user
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    # Get the required todo records pertaining to the user/owner except admin
    if user.get('user_role') == 'admin':
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    else:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    #delete the record with todo_id if present
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()