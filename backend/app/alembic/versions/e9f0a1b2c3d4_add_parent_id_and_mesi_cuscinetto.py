"""add categorie.parent_id + utenti.mesi_cuscinetto (sub-categories, cuscinetto N)

Revision ID: e9f0a1b2c3d4
Revises: d8e9f0a1b2c3
Create Date: 2026-06-17 00:00:07.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'e9f0a1b2c3d4'
down_revision = 'd8e9f0a1b2c3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('categorie', sa.Column('parent_id', sa.Uuid(), nullable=True))
    op.create_index(
        op.f('ix_categorie_parent_id'), 'categorie', ['parent_id'], unique=False
    )
    op.create_foreign_key(
        'fk_categorie_parent_id', 'categorie', 'categorie', ['parent_id'], ['id']
    )
    op.add_column(
        'utenti',
        sa.Column('mesi_cuscinetto', sa.Integer(), nullable=False, server_default='6'),
    )


def downgrade():
    op.drop_column('utenti', 'mesi_cuscinetto')
    op.drop_constraint('fk_categorie_parent_id', 'categorie', type_='foreignkey')
    op.drop_index(op.f('ix_categorie_parent_id'), table_name='categorie')
    op.drop_column('categorie', 'parent_id')
