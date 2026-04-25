"""create content table

Revision ID: 0001_create_content_table
Revises: 
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_create_content_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'content',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('topic', sa.Text, nullable=False),
        sa.Column('script', sa.Text, nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='draft'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )


def downgrade():
    op.drop_table('content')
