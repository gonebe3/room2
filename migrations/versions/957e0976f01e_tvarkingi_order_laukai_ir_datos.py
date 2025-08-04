"""Tvarkingi Order laukai ir datos

Revision ID: 957e0976f01e
Revises: 0baefadb3fa2
Create Date: 2025-07-31 16:20:52.366723

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision = '957e0976f01e'
down_revision = '0baefadb3fa2'
branch_labels = None
depends_on = None


def upgrade():
    # --- Pirma: Pašalink esamą default constraint (jei yra), tada pridėk naują ---
    # (Priklausomai nuo situacijos, gal reikia rankiniu būdu, jei pavadinimas nežinomas)
    # -- Pridėk default constraint prie 'created_on' --
    op.alter_column('orders', 'created_on',
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=sa.text('GETDATE()')
    )
    op.alter_column('orders', 'modified_on',
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=sa.text('GETDATE()')
    )

def downgrade():
    op.alter_column('orders', 'created_on',
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=None
    )
    op.alter_column('orders', 'modified_on',
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=None
    )