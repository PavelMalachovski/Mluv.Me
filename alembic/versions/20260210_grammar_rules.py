"""
Grammar Rules: Tables for grammar rules from příručka ÚJČ and user progress tracking.

Revision ID: 20260210_grammar_rules
Revises: 20260203_gamification_v2
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260210_grammar_rules'
down_revision = '20260203_gamification_v2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add grammar rules system:
    1. grammar_rules table — stores reformulated rules from příručka ÚJČ
    2. user_grammar_progress table — tracks user learning progress per rule
    """

    # Create grammar_rules table
    op.create_table(
        'grammar_rules',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False,
                  comment='Unique rule slug, e.g. vyjmenovana_slova_b'),
        sa.Column('category', sa.String(50), nullable=False,
                  comment='Grammar category: vyslovnost, pravopis_hlasky, etc.'),
        sa.Column('subcategory', sa.String(100), nullable=True,
                  comment='Subcategory within the main category'),
        sa.Column('level', sa.String(5), nullable=False,
                  comment='CEFR level: A1, A2, B1, B2'),
        sa.Column('title_cs', sa.String(300), nullable=False,
                  comment='Rule title in Czech'),
        sa.Column('rule_cs', sa.Text, nullable=False,
                  comment='Rule explanation in Czech (simplified for learners)'),
        sa.Column('explanation_cs', sa.Text, nullable=True,
                  comment='Detailed explanation in Czech'),
        sa.Column('examples', sa.Text, nullable=False, server_default='[]',
                  comment='JSON array of examples'),
        sa.Column('mnemonic', sa.Text, nullable=True,
                  comment='Mnemonic tip in Czech'),
        sa.Column('common_mistakes', sa.Text, nullable=True,
                  comment='JSON array of common mistakes'),
        sa.Column('exercise_data', sa.Text, nullable=False, server_default='[]',
                  comment='JSON array of exercises for games'),
        sa.Column('source_ref', sa.String(100), nullable=True,
                  comment='Reference to original příručka article'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('true'),
                  comment='Is the rule active'),
        sa.Column('sort_order', sa.Integer, nullable=False, server_default='0',
                  comment='Sort order within category'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create composite index for category + level filtering
    op.create_index(
        'ix_grammar_rules_category_level',
        'grammar_rules',
        ['category', 'level']
    )

    # Create user_grammar_progress table
    op.create_table(
        'user_grammar_progress',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer,
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('grammar_rule_id', sa.Integer,
                  sa.ForeignKey('grammar_rules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('times_shown', sa.Integer, nullable=False, server_default='0',
                  comment='Times shown in notifications'),
        sa.Column('times_practiced', sa.Integer, nullable=False, server_default='0',
                  comment='Times practiced in games'),
        sa.Column('last_shown_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Last notification show'),
        sa.Column('last_practiced_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Last game practice'),
        sa.Column('mastery_level', sa.String(20), nullable=False, server_default='new',
                  comment='new, seen, practiced, known, mastered'),
        sa.Column('correct_count', sa.Integer, nullable=False, server_default='0',
                  comment='Correct answers count'),
        sa.Column('incorrect_count', sa.Integer, nullable=False, server_default='0',
                  comment='Incorrect answers count'),
    )

    # Unique constraint: one progress record per user per rule
    op.create_unique_constraint(
        'uq_user_grammar_rule',
        'user_grammar_progress',
        ['user_id', 'grammar_rule_id']
    )

    # Indexes for user_grammar_progress
    op.create_index(
        'ix_user_grammar_progress_user_id',
        'user_grammar_progress',
        ['user_id']
    )
    op.create_index(
        'ix_user_grammar_progress_rule_id',
        'user_grammar_progress',
        ['grammar_rule_id']
    )
    op.create_index(
        'ix_user_grammar_progress_user_rule',
        'user_grammar_progress',
        ['user_id', 'grammar_rule_id']
    )


def downgrade() -> None:
    """Remove grammar rules tables."""
    op.drop_table('user_grammar_progress')
    op.drop_table('grammar_rules')
