"""Add user_id to sessions

Revision ID: a1b2c3d4e5f6
Revises: 27f0d193f12d
Create Date: 2025-11-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '27f0d193f12d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_id column to resume_sessions
    op.add_column('resume_sessions', sa.Column('user_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_resume_sessions_user_id'), 'resume_sessions', ['user_id'], unique=False)

    # Add user_id column to workflow_sessions
    op.add_column('workflow_sessions', sa.Column('user_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_workflow_sessions_user_id'), 'workflow_sessions', ['user_id'], unique=False)

    # Add user_id column to applications
    op.add_column('applications', sa.Column('user_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_applications_user_id'), 'applications', ['user_id'], unique=False)


def downgrade() -> None:
    # Remove user_id column from applications
    op.drop_index(op.f('ix_applications_user_id'), table_name='applications')
    op.drop_column('applications', 'user_id')

    # Remove user_id column from workflow_sessions
    op.drop_index(op.f('ix_workflow_sessions_user_id'), table_name='workflow_sessions')
    op.drop_column('workflow_sessions', 'user_id')

    # Remove user_id column from resume_sessions
    op.drop_index(op.f('ix_resume_sessions_user_id'), table_name='resume_sessions')
    op.drop_column('resume_sessions', 'user_id')
