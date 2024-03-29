"""empty message

Revision ID: d1567c402929
Revises: 
Create Date: 2020-06-26 23:18:41.055892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1567c402929'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ya_id', sa.String(length=64), nullable=False),
    sa.Column('tg_id', sa.Integer(), nullable=True),
    sa.Column('vk_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_verification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=6), nullable=False),
    sa.Column('expires', sa.DateTime(), nullable=False),
    sa.Column('received_from', sa.String(length=512), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_verification')
    op.drop_table('users')
    # ### end Alembic commands ###
