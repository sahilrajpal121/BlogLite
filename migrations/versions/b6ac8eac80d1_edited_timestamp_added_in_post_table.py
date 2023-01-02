"""edited_timestamp added in post table

Revision ID: b6ac8eac80d1
Revises: 2c37df2e67c3
Create Date: 2023-01-02 04:12:46.178950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6ac8eac80d1'
down_revision = '2c37df2e67c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('edited_timestamp', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('edited_timestamp')

    # ### end Alembic commands ###
