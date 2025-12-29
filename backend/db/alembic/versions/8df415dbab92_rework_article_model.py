"""rework_article_model

Revision ID: 8df415dbab92
Revises: 7c783e214029
Create Date: 2025-12-29 12:00:16.312090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8df415dbab92'
down_revision: Union[str, Sequence[str], None] = '7c783e214029'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type first
    article_type_enum = sa.Enum('GENERATED_NEWS', 'EDITORIAL', name='article_type_enum')
    article_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create new LLM metadata table
    op.create_table('article_llm_metadata',
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('ai_model_used', sa.String(length=50), nullable=False),
        sa.Column('sentiment_score', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('article_id')
    )
    
    # Create join table for LLM metadata sources
    op.create_table('llm_metadata_sources',
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['article_llm_metadata.article_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id']),
        sa.PrimaryKeyConstraint('article_id', 'source_id')
    )
    
    # Drop old article_sources table
    op.drop_table('article_sources')
    
    # Add article_type column
    op.add_column('articles', sa.Column('article_type', 
        sa.Enum('GENERATED_NEWS', 'EDITORIAL', name='article_type_enum', create_constraint=True), 
        server_default='GENERATED_NEWS', nullable=False))
    op.create_index('idx_articles_article_type', 'articles', ['article_type'], unique=False)
    
    # Drop old columns
    op.drop_column('articles', 'sentiment_score')
    op.drop_column('articles', 'ai_model_used')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back old columns
    op.add_column('articles', sa.Column('ai_model_used', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('articles', sa.Column('sentiment_score', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
    
    # Drop article_type column and index
    op.drop_index('idx_articles_article_type', table_name='articles')
    op.drop_column('articles', 'article_type')
    
    # Recreate article_sources table
    op.create_table('article_sources',
        sa.Column('article_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('source_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name=op.f('article_sources_article_id_fkey'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], name=op.f('article_sources_source_id_fkey')),
        sa.PrimaryKeyConstraint('article_id', 'source_id', name=op.f('article_sources_pkey'))
    )
    
    # Drop new tables
    op.drop_table('llm_metadata_sources')
    op.drop_table('article_llm_metadata')
    
    # Drop the enum type
    article_type_enum = sa.Enum('GENERATED_NEWS', 'EDITORIAL', name='article_type_enum')
    article_type_enum.drop(op.get_bind(), checkfirst=True)


