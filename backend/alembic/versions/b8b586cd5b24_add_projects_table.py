"""add_projects_table

Revision ID: b8b586cd5b24
Revises: 002
Create Date: 2026-01-08 11:44:09.113646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8b586cd5b24'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('doc_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('color', sa.String(length=50), nullable=True, server_default='bg-blue-500'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Insert default project (for migration of existing data)
    op.execute("""
        INSERT INTO projects (id, title, description, color)
        VALUES ('dagosian', '다고시안 듀얼단', '3개의 태양이 뜨는 사막 행성 다고시안의 이야기', 'bg-orange-500')
    """)

    # 3. Add project_id column to pages table (with default value for existing rows)
    op.add_column('pages', sa.Column('project_id', sa.String(length=50), nullable=True))

    # 4. Set existing pages to default project
    op.execute("UPDATE pages SET project_id = 'dagosian' WHERE project_id IS NULL")

    # 5. Make project_id NOT NULL
    op.alter_column('pages', 'project_id', nullable=False)

    # 6. Create foreign key
    op.create_foreign_key('fk_pages_project_id', 'pages', 'projects', ['project_id'], ['id'], ondelete='CASCADE')

    # 7. Create index on project_id
    op.create_index('idx_pages_project_id', 'pages', ['project_id'])


def downgrade() -> None:
    # 1. Drop foreign key and index
    op.drop_index('idx_pages_project_id', table_name='pages')
    op.drop_constraint('fk_pages_project_id', 'pages', type_='foreignkey')

    # 2. Drop project_id column
    op.drop_column('pages', 'project_id')

    # 3. Drop projects table
    op.drop_table('projects')
