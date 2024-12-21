"""Add notes field to Colony model

Revision ID: 58b9ce1a3607
Revises: 
Create Date: 2024-12-20 20:35:36.566018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58b9ce1a3607'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('colony', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('colony', schema=None) as batch_op:
        batch_op.drop_column('notes')

    # ### end Alembic commands ###
