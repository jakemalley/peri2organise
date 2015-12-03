"""empty message

Revision ID: 3e1b1d2e511b
Revises: 5746b17000bb
Create Date: 2015-12-03 16:27:29.461705

"""

# revision identifiers, used by Alembic.
revision = '3e1b1d2e511b'
down_revision = '5746b17000bb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lesson', sa.Column('attendance_recorded', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('lesson', 'attendance_recoreded')
    ### end Alembic commands ###
