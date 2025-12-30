"""Add is_featured column to articles

Revision ID: b2c3d4e5f6a7
Revises: 8df415dbab92
Create Date: 2025-12-30 02:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = '8df415dbab92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_featured column with default False
    op.add_column('articles', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'))
    
    # Create index for efficient filtering
    op.create_index('idx_articles_is_featured', 'articles', ['is_featured'])


def downgrade() -> None:
    op.drop_index('idx_articles_is_featured', table_name='articles')
    op.drop_column('articles', 'is_featured')
