"""livello domanda

Revision ID: 5403776bb39e
Revises: 63f7883b330d
Create Date: 2021-06-05 14:29:43.538086

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5403776bb39e'
down_revision = '63f7883b330d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('word', sa.Column('livello', sa.Integer))

def downgrade():
    op.drop_column('word', 'livello')