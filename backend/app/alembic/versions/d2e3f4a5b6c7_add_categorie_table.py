"""add categorie table (typed Categoria, FR-7)

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-06-16 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'd2e3f4a5b6c7'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'categorie',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('tipo', sqlmodel.sql.sqltypes.AutoString(length=16), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_categorie_utente_id'), 'categorie', ['utente_id'], unique=False)
    op.create_index(op.f('ix_categorie_tipo'), 'categorie', ['tipo'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_categorie_tipo'), table_name='categorie')
    op.drop_index(op.f('ix_categorie_utente_id'), table_name='categorie')
    op.drop_table('categorie')
