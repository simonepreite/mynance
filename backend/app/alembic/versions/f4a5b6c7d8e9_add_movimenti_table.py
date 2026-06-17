"""add movimenti table (typed Movimento: Spesa/Entrata, FR-5/FR-6)

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-06-17 00:00:02.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'f4a5b6c7d8e9'
down_revision = 'e3f4a5b6c7d8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'movimenti',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('tipo', sqlmodel.sql.sqltypes.AutoString(length=16), nullable=False),
        sa.Column('amount_cents', sa.BigInteger(), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('categoria_id', sa.Uuid(), nullable=False),
        sa.Column('note', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorie.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_movimenti_utente_id'), 'movimenti', ['utente_id'], unique=False
    )
    op.create_index(op.f('ix_movimenti_tipo'), 'movimenti', ['tipo'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_movimenti_tipo'), table_name='movimenti')
    op.drop_index(op.f('ix_movimenti_utente_id'), table_name='movimenti')
    op.drop_table('movimenti')
