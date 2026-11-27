from sqlalchemy.orm import Session
from models.roles import Roles
from enums.roles import UserRole

def seed_roles(db: Session):

    roles = [
        {
            "id": UserRole.ADMIN.value,
            "title": UserRole.ADMIN.name.capitalize(),
            "description": "Administrator"
        },
        {
            "id": UserRole.USER.value,
            "title": UserRole.USER.name.capitalize(),
            "description": "Normal user"
        },
    ]

    for role_data in roles:
        existing = db.query(Roles).filter(
            Roles.title == role_data["title"]
        ).first()

        if not existing:
            db.add(Roles(**role_data))

    db.commit()