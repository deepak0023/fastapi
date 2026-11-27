from sqlalchemy.orm import Session
from models import Users
from enums.roles import UserRole

def seed_users(db: Session):

    users = [
        {
            "email": "admin@gmail.com",
            "username": "admin",
            "first_name": "Admin",
            "last_name": "Test",
            "hashed_password": "admin123",
            "is_active": True,
            "role_id": UserRole.ADMIN.value
        },
    ]

    for user_data in users:
        existing = db.query(Users).filter(
            Users.email == user_data["email"]
        ).first()

        if not existing:
            db.add(Users(**user_data))

    db.commit()