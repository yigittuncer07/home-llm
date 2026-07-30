"""create all tables

Revision ID: 8bcd80717952
Revises: 
Create Date: 2026-07-30 23:48:48.735667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bcd80717952'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=50)),
        sa.Column('email', sa.String(length=50)),
        sa.Column('password_hash', sa.String(length=200))
    )
    
    op.create_table(
        'chats',
        sa.Column('chatId', sa.Integer(), primary_key=True),
        sa.Column('userId', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('title', sa.String(length=255))
    )
    
    op.create_table(
        'messages',
        sa.Column('messageId', sa.Integer(), primary_key=True),
        sa.Column('chatId', sa.Integer(), sa.ForeignKey('chats.chatId', ondelete='CASCADE')),
        sa.Column('model', sa.String(length=100)),
        sa.Column('tokens', sa.Integer()),
        sa.Column('role', sa.String(length=50)),
        sa.Column('content', sa.Text()),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    op.create_table(
        'user_config',
        sa.Column('userId', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('personalized_prompt', sa.Text())
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_config')
    op.drop_table('messages')
    op.drop_table('chats')
    op.drop_table('users')