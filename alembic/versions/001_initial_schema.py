"""
Initial database migration.

Creates all core tables:
- users
- agents
- tasks
- agent_executions
- embeddings
- api_keys
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_superuser', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'USER', 'GUEST', name='userrole'), default='USER', nullable=False),
        sa.Column('api_key', sa.String(255), nullable=True, unique=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('login_count', sa.String(), default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_api_key', 'users', ['api_key'])
    
    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config', postgresql.JSONB(), default={}, nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_agents_name', 'agents', ['name'])
    op.create_index('ix_agents_type', 'agents', ['type'])
    op.create_index('ix_agents_owner_id', 'agents', ['owner_id'])
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED', name='taskstatus'), default='PENDING', nullable=False),
        sa.Column('priority', sa.Integer(), default=1, nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('celery_task_id', sa.String(255), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_agent_id', 'tasks', ['agent_id'])
    op.create_index('ix_tasks_owner_id', 'tasks', ['owner_id'])
    op.create_index('ix_tasks_celery_task_id', 'tasks', ['celery_task_id'])
    
    # Create agent_executions table
    op.create_table(
        'agent_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('input_data', postgresql.JSONB(), nullable=True),
        sa.Column('output_data', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Numeric(10, 4), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_traceback', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), default={}, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_agent_executions_agent_id', 'agent_executions', ['agent_id'])
    op.create_index('ix_agent_executions_task_id', 'agent_executions', ['task_id'])
    op.create_index('ix_agent_executions_status', 'agent_executions', ['status'])
    
    # Create embeddings table
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', postgresql.ARRAY(sa.Float, dimensions=1536), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), default={}, nullable=False),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', sa.String(255), nullable=True),
        sa.Column('chunk_index', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_embeddings_owner_id', 'embeddings', ['owner_id'])
    op.create_index('ix_embeddings_source', 'embeddings', ['source'])
    op.create_index('ix_embeddings_document_id', 'embeddings', ['document_id'])
    
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('prefix', sa.String(16), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scopes', postgresql.JSONB(), default=[], nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.String(), default='0'),
        sa.Column('rate_limit', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_api_keys_key_hash', 'api_keys', ['key_hash'])
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])


def downgrade() -> None:
    op.drop_table('api_keys')
    op.drop_table('embeddings')
    op.drop_table('agent_executions')
    op.drop_table('tasks')
    op.drop_table('agents')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS taskstatus')
