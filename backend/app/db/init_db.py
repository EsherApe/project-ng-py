import logging
from sqlmodel import SQLModel, Session
from backend.app.db.database import engine
from backend.app.models.user import User
from backend.app.models.token import RefreshToken
from backend.app.core.security import get_password_hash

logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Initialize the database with tables and default data
    """
    # Create tables
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created")

    # Check if admin user exists
    with Session(engine) as session:
        admin = session.query(User).filter(User.username == "admin").first()

        if not admin:
            # Create default admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="Admin User",
                hashed_password=get_password_hash("admin"),
                roles="ADMIN,USER",
                tenant="default"
            )

            session.add(admin_user)
            session.commit()

            logger.info("Default admin user created")
