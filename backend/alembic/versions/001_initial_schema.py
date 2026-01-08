"""Initial schema with pages table

Revision ID: 001
Revises:
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pg_trgm extension 활성화 (Trigram 검색용)
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')

    # pages 테이블 생성
    op.create_table(
        'pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('author', sa.String(length=100), nullable=True),

        # 컨텐츠
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=True),

        # 날짜
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),

        # 상태
        sa.Column('status', sa.String(length=20), server_default='active', nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),

        # GitHub 동기화
        sa.Column('github_sha', sa.String(length=40), nullable=True),
        sa.Column('github_url', sa.Text(), nullable=True),
        sa.Column('last_synced_at', sa.TIMESTAMP(timezone=True), nullable=True),

        # 조회수
        sa.Column('view_count', sa.Integer(), server_default='0', nullable=True),

        # 제약조건
        sa.CheckConstraint("status IN ('active', 'archived', 'draft')", name='status_check'),
        sa.PrimaryKeyConstraint('id')
    )

    # 인덱스 생성
    op.create_index('idx_pages_slug', 'pages', ['slug'], unique=True)
    op.create_index('idx_pages_category', 'pages', ['category'], unique=False)
    op.create_index('idx_pages_status', 'pages', ['status'], unique=False)
    op.create_index('idx_pages_updated', 'pages', ['updated_at'], unique=False)

    # Trigram 인덱스 (한글 검색용)
    op.execute('CREATE INDEX idx_pages_title_trgm ON pages USING gin (title gin_trgm_ops);')
    op.execute('CREATE INDEX idx_pages_content_trgm ON pages USING gin (content gin_trgm_ops);')


def downgrade() -> None:
    # Trigram 인덱스 삭제
    op.execute('DROP INDEX IF EXISTS idx_pages_content_trgm;')
    op.execute('DROP INDEX IF EXISTS idx_pages_title_trgm;')

    # 일반 인덱스 삭제
    op.drop_index('idx_pages_updated', table_name='pages')
    op.drop_index('idx_pages_status', table_name='pages')
    op.drop_index('idx_pages_category', table_name='pages')
    op.drop_index('idx_pages_slug', table_name='pages')

    # 테이블 삭제
    op.drop_table('pages')

    # extension 삭제 (선택사항)
    # op.execute('DROP EXTENSION IF EXISTS pg_trgm;')
