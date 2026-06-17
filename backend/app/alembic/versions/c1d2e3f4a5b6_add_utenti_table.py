"""add utenti table (mynance Utente domain, FR-1/FR-3)

Revision ID: c1d2e3f4a5b6
Revises: fe56fa70289e
Create Date: 2026-06-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'c1d2e3f4a5b6'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'utenti',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('username', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('recovery_code_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('session_timeout_days', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_utenti_username'), 'utenti', ['username'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_utenti_username'), table_name='utenti')
    op.drop_table('utenti')
