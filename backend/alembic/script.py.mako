"""
Mako template for Alembic revision scripts.
"""
from alembic import op
import sqlalchemy as sa

revision = '${up_revision}'
down_revision = ${down_revision}
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
