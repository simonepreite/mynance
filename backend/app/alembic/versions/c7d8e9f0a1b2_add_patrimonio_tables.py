"""add patrimonio tables: investimenti, versamenti_pac, beni_immobili, beni_mobili

Revision ID: c7d8e9f0a1b2
Revises: b6c7d8e9f0a1
Create Date: 2026-06-17 00:00:05.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'c7d8e9f0a1b2'
down_revision = 'b6c7d8e9f0a1'
branch_labels = None
depends_on = None

_AS = sqlmodel.sql.sqltypes.AutoString


def _timestamps():
    return (
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )


def upgrade():
    op.create_table(
        'investimenti',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('nome', _AS(length=255), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_investimenti_utente_id'), 'investimenti', ['utente_id'], unique=False
    )

    op.create_table(
        'versamenti_pac',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('investimento_id', sa.Uuid(), nullable=False),
        sa.Column('importo_cents', sa.BigInteger(), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.ForeignKeyConstraint(['investimento_id'], ['investimenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_versamenti_pac_utente_id'), 'versamenti_pac', ['utente_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_versamenti_pac_investimento_id'), 'versamenti_pac',
        ['investimento_id'], unique=False,
    )

    op.create_table(
        'beni_immobili',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('nome', _AS(length=255), nullable=False),
        sa.Column('prezzo_cents', sa.BigInteger(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_beni_immobili_utente_id'), 'beni_immobili', ['utente_id'],
        unique=False,
    )

    op.create_table(
        'beni_mobili',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('nome', _AS(length=255), nullable=False),
        sa.Column('prezzo_cents', sa.BigInteger(), nullable=False),
        sa.Column('data_acquisto', sa.Date(), nullable=False),
        sa.Column('svalutazione_percentuale', sa.Float(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_beni_mobili_utente_id'), 'beni_mobili', ['utente_id'], unique=False
    )


def downgrade():
    op.drop_index(op.f('ix_beni_mobili_utente_id'), table_name='beni_mobili')
    op.drop_table('beni_mobili')
    op.drop_index(op.f('ix_beni_immobili_utente_id'), table_name='beni_immobili')
    op.drop_table('beni_immobili')
    op.drop_index(
        op.f('ix_versamenti_pac_investimento_id'), table_name='versamenti_pac'
    )
    op.drop_index(op.f('ix_versamenti_pac_utente_id'), table_name='versamenti_pac')
    op.drop_table('versamenti_pac')
    op.drop_index(op.f('ix_investimenti_utente_id'), table_name='investimenti')
    op.drop_table('investimenti')
