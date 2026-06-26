"""add utenti.email + email_verified and utente_token (email verify + reset)

Revision ID: f0a1b2c3d4e5
Revises: e9f0a1b2c3d4
Create Date: 2026-06-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

revision = 'f0a1b2c3d4e5'
down_revision = 'e9f0a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade():
    # Email on utenti — nullable to grandfather pre-feature rows, unique-indexed.
    op.add_column(
        'utenti',
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    )
    op.create_index(op.f('ix_utenti_email'), 'utenti', ['email'], unique=True)
    op.add_column(
        'utenti',
        sa.Column(
            'email_verified',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
    )
    # Grandfather: existing accounts registered before the verification gate
    # stay able to log in.
    op.execute('UPDATE utenti SET email_verified = true')

    op.create_table(
        'utente_token',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column(
            'token_hash', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False
        ),
        sa.Column(
            'purpose', sqlmodel.sql.sqltypes.AutoString(length=32), nullable=False
        ),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_utente_token_utente_id'), 'utente_token', ['utente_id'], unique=False
    )
    op.create_index(
        op.f('ix_utente_token_token_hash'),
        'utente_token',
        ['token_hash'],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f('ix_utente_token_token_hash'), table_name='utente_token')
    op.drop_index(op.f('ix_utente_token_utente_id'), table_name='utente_token')
    op.drop_table('utente_token')
    op.drop_column('utenti', 'email_verified')
    op.drop_index(op.f('ix_utenti_email'), table_name='utenti')
    op.drop_column('utenti', 'email')
