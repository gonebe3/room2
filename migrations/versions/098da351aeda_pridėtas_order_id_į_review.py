"""Pridėtas order_id į review

Revision ID: 098da351aeda
Revises: 42e8f01b6f4c
Create Date: 2025-08-02 14:30:35.407698

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '098da351aeda'
down_revision = '42e8f01b6f4c'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('review') as batch_op:
        batch_op.add_column(sa.Column('order_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_review_order', 'orders', ['order_id'], ['id'])

def downgrade():
    with op.batch_alter_table('review') as batch_op:
        batch_op.drop_constraint('fk_review_order', type_='foreignkey')
        batch_op.drop_column('order_id')

    # ### end Alembic commands ###
