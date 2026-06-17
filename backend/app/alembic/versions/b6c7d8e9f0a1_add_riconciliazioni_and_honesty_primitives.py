"""add riconciliazioni + categorie.is_system + utenti reconcile interval (FR-16/17/18)

Revision ID: b6c7d8e9f0a1
Revises: a5b6c7d8e9f0
Create Date: 2026-06-17 00:00:04.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'b6c7d8e9f0a1'
down_revision = 'a5b6c7d8e9f0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'riconciliazioni',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('liquidita_reale_cents', sa.BigInteger(), nullable=False),
        sa.Column('liquidita_calcolata_cents', sa.BigInteger(), nullable=False),
        sa.Column('drift_cents', sa.BigInteger(), nullable=False),
        sa.Column('data_riconciliazione', sa.Date(), nullable=False),
        sa.Column('esito', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_riconciliazioni_utente_id_data_riconciliazione',
        'riconciliazioni',
        ['utente_id', 'data_riconciliazione'],
        unique=False,
    )
    op.add_column(
        'categorie',
        sa.Column(
            'is_system', sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        'utenti',
        sa.Column(
            'intervallo_riconciliazione_giorni',
            sa.Integer(),
            nullable=False,
            server_default='7',
        ),
    )


def downgrade():
    op.drop_column('utenti', 'intervallo_riconciliazione_giorni')
    op.drop_column('categorie', 'is_system')
    op.drop_index(
        'ix_riconciliazioni_utente_id_data_riconciliazione',
        table_name='riconciliazioni',
    )
    op.drop_table('riconciliazioni')
