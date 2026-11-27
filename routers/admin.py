from fastapi import APIRouter, Depends, HTTPException, Path
from models.users import Users
from pydantic import BaseModel, Field, ConfigDict, model_validator
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Annotated, Literal
from starlette import status
from enums.roles import UserRole
from .auth import get_current_user

# Get fastapi instance
router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

# Pydantic validation for user request
class UpdateRoleRequest(BaseModel):
    role: Literal ["User", "Admin"] = Field (
        description="Role name must be either 'Admin' or 'User'.",
    )

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: Literal["ADMIN", "USER"] | str

    @model_validator(mode="before")
    @classmethod
    def map_role_from_id(cls, data):
        # Handle SQLAlchemy ORM instances
        if not isinstance(data, dict):
            role_id = getattr(data, "role_id", None)
            try:
                role_name = UserRole(role_id).name if role_id is not None else "UNKNOWN"
            except ValueError:
                role_name = str(role_id)

            return {
                "id": data.id,
                "email": data.email,
                "username": data.username,
                "first_name": data.first_name,
                "last_name": data.last_name,
                "is_active": data.is_active,
                "role": role_name.capitalize(),
            }
        return data

# Get db connection for CRUD operation
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

def get_role_id(role_name: str):
    match role_name:
        case UserRole.ADMIN.name:
            return 1
        case UserRole.USER.name:
            return 2
        case _:
            raise HTTPException(status_code=404, detail='Invalid user Role')

# user role update
@router.patch('/update_role/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def create_user(db: db_dependency, user:user_dependency, update_user_role_request: UpdateRoleRequest, user_id: int=Path(gt=0)):
    # Update user role
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    if user.get('user_role') != UserRole.ADMIN.name:
        raise HTTPException(status_code=403, detail="Only admin can update user roles, contact admin !!")
    user = db.query(Users).filter(Users.id == user_id).first()
    user.role_id = get_role_id(update_user_role_request.role.upper())
    db.add(user)
    db.commit()

# user role update
@router.patch('/user_list', status_code=status.HTTP_200_OK, response_model=list[UserResponse])
async def create_user(db: db_dependency, user:user_dependency):
    # Update user role
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    if user.get('user_role') != UserRole.ADMIN.name:
        raise HTTPException(status_code=403, detail="Only admin can access user list, contact admin !!")
    return db.query(Users).all()