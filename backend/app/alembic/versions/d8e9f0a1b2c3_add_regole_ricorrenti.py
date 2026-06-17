"""add regole_ricorrenti + regole_occorrenze + regola_id back-refs (FR-8)

Revision ID: d8e9f0a1b2c3
Revises: c7d8e9f0a1b2
Create Date: 2026-06-17 00:00:06.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'd8e9f0a1b2c3'
down_revision = 'c7d8e9f0a1b2'
branch_labels = None
depends_on = None

_AS = sqlmodel.sql.sqltypes.AutoString


def upgrade():
    op.create_table(
        'regole_ricorrenti',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('importo_cents', sa.BigInteger(), nullable=False),
        sa.Column('periodicita', _AS(length=16), nullable=False),
        sa.Column('intervallo_mesi', sa.Integer(), nullable=True),
        sa.Column('day_of_period', sa.Integer(), nullable=False),
        sa.Column('kind', _AS(length=20), nullable=False),
        sa.Column('categoria_id', sa.Uuid(), nullable=True),
        sa.Column('investimento_id', sa.Uuid(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('note', _AS(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorie.id']),
        sa.ForeignKeyConstraint(['investimento_id'], ['investimenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_regole_ricorrenti_utente_id'), 'regole_ricorrenti',
        ['utente_id'], unique=False,
    )

    op.create_table(
        'regole_occorrenze',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('regola_id', sa.Uuid(), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('skipped', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.ForeignKeyConstraint(['regola_id'], ['regole_ricorrenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_regole_occorrenze_utente_id'), 'regole_occorrenze',
        ['utente_id'], unique=False,
    )
    op.create_index(
        op.f('ix_regole_occorrenze_regola_id'), 'regole_occorrenze',
        ['regola_id'], unique=False,
    )

    op.add_column(
        'movimenti', sa.Column('regola_id', sa.Uuid(), nullable=True)
    )
    op.create_foreign_key(
        'fk_movimenti_regola_id', 'movimenti', 'regole_ricorrenti',
        ['regola_id'], ['id'],
    )
    op.add_column(
        'versamenti_pac', sa.Column('regola_id', sa.Uuid(), nullable=True)
    )
    op.create_foreign_key(
        'fk_versamenti_pac_regola_id', 'versamenti_pac', 'regole_ricorrenti',
        ['regola_id'], ['id'],
    )


def downgrade():
    op.drop_constraint(
        'fk_versamenti_pac_regola_id', 'versamenti_pac', type_='foreignkey'
    )
    op.drop_column('versamenti_pac', 'regola_id')
    op.drop_constraint('fk_movimenti_regola_id', 'movimenti', type_='foreignkey')
    op.drop_column('movimenti', 'regola_id')
    op.drop_index(
        op.f('ix_regole_occorrenze_regola_id'), table_name='regole_occorrenze'
    )
    op.drop_index(
        op.f('ix_regole_occorrenze_utente_id'), table_name='regole_occorrenze'
    )
    op.drop_table('regole_occorrenze')
    op.drop_index(
        op.f('ix_regole_ricorrenti_utente_id'), table_name='regole_ricorrenti'
    )
    op.drop_table('regole_ricorrenti')
