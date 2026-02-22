"""add daily_stats UNIQUE constraint and saved_words next_review_date index

Revision ID: 20260223_audit_indexes
Revises: 20260222_subscriptions
Create Date: 2026-02-23

Adds:
- UniqueConstraint on daily_stats(user_id, date) to prevent duplicates
- Index on saved_words(next_review_date) for review query performance
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260223_audit_indexes"
down_revision = "20260222_subscriptions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove duplicate daily_stats before adding UNIQUE constraint
    op.execute("""
        DELETE FROM daily_stats
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM daily_stats
            GROUP BY user_id, date
        )
    """)

    op.create_unique_constraint(
        "uq_daily_stats_user_date",
        "daily_stats",
        ["user_id", "date"],
    )

    op.create_index(
        "idx_saved_words_next_review",
        "saved_words",
        ["next_review_date"],
    )


def downgrade() -> None:
    op.drop_index("idx_saved_words_next_review", table_name="saved_words")
    op.drop_constraint("uq_daily_stats_user_date", "daily_stats", type_="unique")
