from app.infrastructure.database.session import engine, Base
# Import all ORM models so they are registered with Base
from app.infrastructure.database import models

def main():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    main()
