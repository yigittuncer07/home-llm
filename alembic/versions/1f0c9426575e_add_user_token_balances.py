from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '1f0c9426575e'
down_revision: Union[str, Sequence[str], None] = '8bcd80717952'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'user_token_balances',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('userId', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('model_name', sa.String(length=100)),
        sa.Column('balance', sa.Integer(), server_default='0'),
        sa.UniqueConstraint('userId', 'model_name', name='uq_user_model_balance')
    )

def downgrade() -> None:
    op.drop_table('user_token_balances')