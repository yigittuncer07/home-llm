import os
import bcrypt
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from dotenv import load_dotenv

load_dotenv()

revision: str = '74de17d74910' # Update this ID if you auto-generated the file
down_revision: Union[str, Sequence[str], None] = '1f0c9426575e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False))
    
    # get credentials from .env
    admin_email = os.getenv("ADMIN_EMAIL", "admin@admin.com")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")
    
    # hash the password to match your auth system
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')
    
    # insert the admin user
    op.execute(
        sa.text("""
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (:username, :email, :password_hash, true)
        """).bindparams(
            username=admin_username,
            email=admin_email,
            password_hash=password_hash
        )
    )

def downgrade() -> None:
    admin_email = os.getenv("ADMIN_EMAIL", "admin@admin.com")
    
    op.execute(
        sa.text("DELETE FROM users WHERE email = :email").bindparams(email=admin_email)
    )
    
    op.drop_column('users', 'is_admin')