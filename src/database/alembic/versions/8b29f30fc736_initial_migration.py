"""initial migration

Revision ID: 8b29f30fc736
Revises: 
Create Date: 2023-10-04 14:18:02.395826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b29f30fc736'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('public_id', sa.String, unique=True, index=True),
        sa.Column('username', sa.String, unique=True, index=True),
        sa.Column('is_active', sa.Boolean, default=False),
        sa.Column('is_host', sa.Boolean, default=False),
        sa.Column('is_ready', sa.Boolean, default=False),
        sa.Column('lobby_id', sa.Integer),
        sa.ForeignKeyConstraint(['lobby_id'], ['lobbies.id'])
    )

    op.create_table(
        'scores',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('date_set', sa.DateTime),
        sa.Column('value', sa.Integer, index=True),
        sa.Column('owner_id', sa.Integer),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'])
    )

    op.create_table(
        'lobbies',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('public_id', sa.String, unique=True, index=True),
        sa.Column('name', sa.String, unique=True)
    )


def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('scores')
    op.drop_table('lobbies')
