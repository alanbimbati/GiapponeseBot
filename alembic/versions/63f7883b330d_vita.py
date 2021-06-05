"""vita

Revision ID: 63f7883b330d
Revises: 
Create Date: 2021-06-05 14:18:28.755811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63f7883b330d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('utente', sa.Column('vita', sa.Integer))

def downgrade():
    op.drop_column('utente', 'vita')