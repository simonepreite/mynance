"""add liquidita_iniziale_cents to utenti + rebaseline_audit table (FR-12)

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-06-17 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f4a5b6c7d8'
down_revision = 'd2e3f4a5b6c7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'utenti',
        sa.Column('liquidita_iniziale_cents', sa.BigInteger(), nullable=True),
    )
    op.create_table(
        'rebaseline_audit',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('old_value_cents', sa.BigInteger(), nullable=False),
        sa.Column('new_value_cents', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_rebaseline_audit_utente_id'),
        'rebaseline_audit',
        ['utente_id'],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f('ix_rebaseline_audit_utente_id'), table_name='rebaseline_audit'
    )
    op.drop_table('rebaseline_audit')
    op.drop_column('utenti', 'liquidita_iniziale_cents')
