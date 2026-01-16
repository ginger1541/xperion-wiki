"""Make project_id nullable

Revision ID: 003
Revises: 002
Create Date: 2026-01-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    project_id 컬럼을 nullable로 변경

    프론트엔드에서 project_id를 보내지 않는 경우를 처리하기 위해
    일시적으로 nullable로 변경합니다.
    """
    # PostgreSQL
    op.alter_column('pages', 'project_id',
                    existing_type=sa.String(length=50),
                    nullable=True)


def downgrade() -> None:
    """
    project_id를 다시 NOT NULL로 되돌림

    주의: NULL 값이 있는 경우 이 다운그레이드는 실패합니다.
    """
    # 먼저 NULL 값을 기본값으로 채움
    op.execute("UPDATE pages SET project_id = 'default' WHERE project_id IS NULL")

    # NOT NULL 제약조건 추가
    op.alter_column('pages', 'project_id',
                    existing_type=sa.String(length=50),
                    nullable=False)
