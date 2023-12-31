"""empty message

Revision ID: d03beb762048
Revises: fc019d4d0b85
Create Date: 2023-09-15 17:07:13.884691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd03beb762048'
down_revision = 'fc019d4d0b85'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # with op.batch_alter_table('song_user_data', schema=None) as batch_op:
    #     batch_op.add_column(sa.Column('title', sa.String(length=200), nullable=False))
    #     batch_op.drop_column('name')

    # ### end Alembic commands ###
    op.alter_column('song_user_data', 'name', new_column_name='title')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # with op.batch_alter_table('song_user_data', schema=None) as batch_op:
    #     batch_op.add_column(sa.Column('name', sa.VARCHAR(length=200), nullable=False))
    #     batch_op.drop_column('title')

    # ### end Alembic commands ###
    op.alter_column('song_user_data', 'title', new_column_name='name')
