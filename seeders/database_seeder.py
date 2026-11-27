from database import SessionLocal

from seeders.seed_roles import seed_roles
from seeders.seed_users import seed_users

def run_seeders():

    db = SessionLocal()

    try:
        seed_roles(db)
        seed_users(db)

        print("Database seeding completed!")

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()

if __name__ == "__main__":
    run_seeders()