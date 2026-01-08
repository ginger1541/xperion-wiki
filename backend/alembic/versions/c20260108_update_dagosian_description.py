"""update_dagosian_description

Revision ID: c20260108
Revises: b8b586cd5b24
Create Date: 2026-01-08 13:16:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c20260108'
down_revision = 'b8b586cd5b24'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update the description of the 'dagosian' project
    op.execute("""
        UPDATE projects
        SET description = '5인의 영웅이야기'
        WHERE id = 'dagosian'
    """)


def downgrade() -> None:
    # Revert to the original description
    op.execute("""
        UPDATE projects
        SET description = '3개의 태양이 뜨는 사막 행성 다고시안의 이야기'
        WHERE id = 'dagosian'
    """)
