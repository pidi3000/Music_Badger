"""empty message

Revision ID: 79873af71a76
Revises: d03beb762048
Create Date: 2023-09-18 02:11:58.006558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79873af71a76'
down_revision = 'd03beb762048'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('song_user_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_added', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('song_user_data', schema=None) as batch_op:
        batch_op.drop_column('date_added')

    # ### end Alembic commands ###
