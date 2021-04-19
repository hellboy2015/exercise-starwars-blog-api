"""empty message

Revision ID: 7223ec5da000
Revises: bc01b860ceb3
Create Date: 2021-04-11 02:16:37.169607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7223ec5da000'
down_revision = 'bc01b860ceb3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('planets', sa.Column('name', sa.String(length=250), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('planets', 'name')
    # ### end Alembic commands ###