"""Add tags table and page_tags

Revision ID: 002
Revises: 001
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # tags 테이블 생성
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('usage_count', sa.Integer(), server_default='0', nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('idx_tags_name', 'tags', ['name'], unique=True)

    # page_tags 다대다 관계 테이블
    op.create_table(
        'page_tags',
        sa.Column('page_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('page_id', 'tag_id')
    )

    op.create_index('idx_page_tags_page', 'page_tags', ['page_id'], unique=False)
    op.create_index('idx_page_tags_tag', 'page_tags', ['tag_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_page_tags_tag', table_name='page_tags')
    op.drop_index('idx_page_tags_page', table_name='page_tags')
    op.drop_table('page_tags')

    op.drop_index('idx_tags_name', table_name='tags')
    op.drop_table('tags')
