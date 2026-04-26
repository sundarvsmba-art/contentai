"""add trends table and extended content columns

Revision ID: 0002_add_trends_and_content_columns
Revises: 0001_create_content_table
Create Date: 2026-04-26
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_add_trends_and_content_columns"
down_revision = "0001_create_content_table"
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------ trends
    op.create_table(
        "trends",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("topic", sa.Text, nullable=False),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("viral_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            index=True,
        ),
    )
    op.create_index("ix_trends_category", "trends", ["category"])
    op.create_index("ix_trends_created_at", "trends", ["created_at"])

    # ----------------------------------------- extended columns on content
    op.add_column("content", sa.Column("hook", sa.Text, nullable=True))
    op.add_column("content", sa.Column("reel_title", sa.String(256), nullable=True))
    op.add_column("content", sa.Column("caption", sa.Text, nullable=True))
    op.add_column("content", sa.Column("hashtags", sa.Text, nullable=True))
    op.add_column("content", sa.Column("category", sa.String(64), nullable=True))
    op.add_column("content", sa.Column("viral_score", sa.Integer, nullable=True))
    op.add_column(
        "content",
        sa.Column(
            "trend_id",
            sa.Integer,
            sa.ForeignKey("trends.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_content_category", "content", ["category"])
    op.create_index("ix_content_status", "content", ["status"])


def downgrade():
    op.drop_index("ix_content_status", "content")
    op.drop_index("ix_content_category", "content")
    op.drop_column("content", "trend_id")
    op.drop_column("content", "viral_score")
    op.drop_column("content", "category")
    op.drop_column("content", "hashtags")
    op.drop_column("content", "caption")
    op.drop_column("content", "reel_title")
    op.drop_column("content", "hook")
    op.drop_index("ix_trends_created_at", "trends")
    op.drop_index("ix_trends_category", "trends")
    op.drop_table("trends")
