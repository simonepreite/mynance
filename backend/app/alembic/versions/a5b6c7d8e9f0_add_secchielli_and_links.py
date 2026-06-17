"""add secchielli table + Categoria/Movimento secchiello_id links (FR-9/10/11)

Revision ID: a5b6c7d8e9f0
Revises: f4a5b6c7d8e9
Create Date: 2026-06-17 00:00:03.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a5b6c7d8e9f0'
down_revision = 'f4a5b6c7d8e9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'secchielli',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('utente_id', sa.Uuid(), nullable=False),
        sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('importo_previsto_cents', sa.BigInteger(), nullable=False),
        sa.Column('periodicita', sqlmodel.sql.sqltypes.AutoString(length=16), nullable=False),
        sa.Column('intervallo_mesi', sa.Integer(), nullable=True),
        sa.Column('prossima_scadenza', sa.Date(), nullable=False),
        sa.Column('data_inizio', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utente_id'], ['utenti.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_secchielli_utente_id'), 'secchielli', ['utente_id'], unique=False
    )
    op.add_column(
        'categorie', sa.Column('secchiello_id', sa.Uuid(), nullable=True)
    )
    op.create_foreign_key(
        'fk_categorie_secchiello_id', 'categorie', 'secchielli',
        ['secchiello_id'], ['id'],
    )
    op.add_column(
        'movimenti', sa.Column('secchiello_id', sa.Uuid(), nullable=True)
    )
    op.create_foreign_key(
        'fk_movimenti_secchiello_id', 'movimenti', 'secchielli',
        ['secchiello_id'], ['id'],
    )


def downgrade():
    op.drop_constraint('fk_movimenti_secchiello_id', 'movimenti', type_='foreignkey')
    op.drop_column('movimenti', 'secchiello_id')
    op.drop_constraint('fk_categorie_secchiello_id', 'categorie', type_='foreignkey')
    op.drop_column('categorie', 'secchiello_id')
    op.drop_index(op.f('ix_secchielli_utente_id'), table_name='secchielli')
    op.drop_table('secchielli')
