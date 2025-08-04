"""Order ir Discount modeliai

Revision ID: 0baefadb3fa2
Revises: 0727dddedb16
Create Date: 2025-07-31 16:10:45.732438
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0baefadb3fa2'
down_revision = '0727dddedb16'
branch_labels = None
depends_on = None

def upgrade():
    # --- 1. Pašalinam default constraint iš 'created_on' ---
    op.execute("""
    DECLARE @constraint_name NVARCHAR(200)
    SELECT @constraint_name = dc.name
    FROM sys.default_constraints dc
        JOIN sys.columns c ON dc.parent_object_id = c.object_id AND dc.parent_column_id = c.column_id
        JOIN sys.tables t ON c.object_id = t.object_id
    WHERE t.name = 'orders' AND c.name = 'created_on'
    IF @constraint_name IS NOT NULL EXEC('ALTER TABLE orders DROP CONSTRAINT ' + @constraint_name)
    """)
    # --- 2. Pašalinam default constraint iš 'modified_on' ---
    op.execute("""
    DECLARE @constraint_name NVARCHAR(200)
    SELECT @constraint_name = dc.name
    FROM sys.default_constraints dc
        JOIN sys.columns c ON dc.parent_object_id = c.object_id AND dc.parent_column_id = c.column_id
        JOIN sys.tables t ON c.object_id = t.object_id
    WHERE t.name = 'orders' AND c.name = 'modified_on'
    IF @constraint_name IS NOT NULL EXEC('ALTER TABLE orders DROP CONSTRAINT ' + @constraint_name)
    """)

    # --- 3. ALTER COLUMN: keičiam tipą į DateTime(timezone=True) ---
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('created_on',
               existing_type=sa.DATETIME(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
        batch_op.alter_column('modified_on',
               existing_type=sa.DATETIME(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)

def downgrade():
    # --- Jeigu downgrade, gali vėl keisti atgal ---
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('modified_on',
               existing_type=sa.DateTime(timezone=True),
               type_=sa.DATETIME(),
               existing_nullable=False,
               existing_server_default=sa.text('(getdate())'))
        batch_op.alter_column('created_on',
               existing_type=sa.DateTime(timezone=True),
               type_=sa.DATETIME(),
               existing_nullable=False,
               existing_server_default=sa.text('(getdate())'))