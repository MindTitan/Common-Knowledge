"""Create upload_tasks table

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for task status
    task_status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='taskstatus')
    task_status_enum.create(op.get_bind())
    
    # Create upload_tasks table
    op.create_table('upload_tasks',
        sa.Column('task_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='taskstatus'), nullable=False),
        sa.Column('source_file_path', sa.Text(), nullable=False),
        sa.Column('blob_storage_path', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('task_id')
    )
    op.create_index(op.f('ix_upload_tasks_task_id'), 'upload_tasks', ['task_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_upload_tasks_task_id'), table_name='upload_tasks')
    op.drop_table('upload_tasks')
    
    # Drop enum type
    task_status_enum = postgresql.ENUM(name='taskstatus')
    task_status_enum.drop(op.get_bind()) 