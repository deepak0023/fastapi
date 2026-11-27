from fastapi import APIRouter, Depends, HTTPException
from models.users import Users
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Annotated, Literal
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from enums.roles import UserRole

# Get fastapi instance
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '6442318aefd6abfad912c4c373769ea6bfbdabeaaa98063c3e4bd118edb50200'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/login')

# Pydantic validation for user request
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: Literal ["User", "Admin"] = Field (
        description="Role name must be either 'Admin' or 'User'.",
    )

class Token(BaseModel):
    access_token: str
    token_type: str

# Get db connection for CRUD operation
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# user signin / add user
@router.post('/signin', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email= create_user_request.email,
        username= create_user_request.username,
        first_name= create_user_request.first_name,
        last_name= create_user_request.last_name,
        role_id= UserRole.USER.value,
        hashed_password= bcrypt_context.hash(create_user_request.password),
        is_active=True
    )

    db.add(create_user_model)
    db.commit()

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta, role_id: int):
    encode = {'sub': username, 'id': user_id, 'role_id': role_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# authenticate user with username and password and generate and return jwt token
@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    auth = authenticate_user(form_data.username, form_data.password, db)
    if not auth:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    token = create_access_token(auth.username, auth.id, timedelta(minutes=20), auth.role_id)
    return {'access_token': token, 'token_type': 'bearer'}

# use the jwt token generated to access user details from specific claims
@router.get("/get_current_user")
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role_id: int = payload.get('role_id')
        role: UserRole = UserRole(role_id)
        if username is None or user_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
        return {'username': username, 'user_id': user_id, 'user_role': role.name}
    except JWTError:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
