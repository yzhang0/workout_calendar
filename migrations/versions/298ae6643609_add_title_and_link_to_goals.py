"""add title and link to goals

Revision ID: 298ae6643609
Revises: 
Create Date: 2025-05-24 21:20:11.061066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '298ae6643609'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('link', sa.String(length=200), nullable=True))
        batch_op.alter_column('workout_type',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.alter_column('description',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('weeks_to_complete',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('weeks_to_complete',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('description',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('workout_type',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.drop_column('link')
        batch_op.drop_column('title')

    # ### end Alembic commands ###
