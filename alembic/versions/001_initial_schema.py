"""Initial schema with users and email verification

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-11-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema"""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(20), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create email verification tokens table
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('token', UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_email_verification_tokens_token', 'email_verification_tokens', ['token'])
    
    # Create factions table
    op.create_table(
        'factions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('game_system', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('abbreviation', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_factions_game_system', 'factions', ['game_system'])
    
    # Create matchups table
    op.create_table(
        'matchups',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('game_system', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='created'),
        
        sa.Column('player1_user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('player1_name', sa.String(100), nullable=False),
        sa.Column('player1_army_list', sa.Text(), nullable=True),
        sa.Column('player1_faction_id', UUID(as_uuid=True), nullable=True),
        
        sa.Column('player2_user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('player2_name', sa.String(100), nullable=True),
        sa.Column('player2_army_list', sa.Text(), nullable=True),
        sa.Column('player2_faction_id', UUID(as_uuid=True), nullable=True),
        
        sa.Column('battle_plan_json', sa.Text(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('battle_started_at', sa.DateTime(), nullable=True),
        sa.Column('battle_ended_at', sa.DateTime(), nullable=True),
        
        sa.Column('scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('location_name', sa.String(200), nullable=True),
        
        sa.Column('winner_user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('player1_vp', sa.Integer(), nullable=True),
        sa.Column('player2_vp', sa.Integer(), nullable=True),
        sa.Column('result_notes', sa.Text(), nullable=True),
        sa.Column('result_verified_at', sa.DateTime(), nullable=True),
        
        sa.Column('disputed_at', sa.DateTime(), nullable=True),
        sa.Column('dispute_reason', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolved_by_admin_id', UUID(as_uuid=True), nullable=True),
        sa.Column('location_manually_verified', sa.Boolean(), nullable=False, server_default='false'),
        
        sa.ForeignKeyConstraint(['player1_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['player2_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['player1_faction_id'], ['factions.id']),
        sa.ForeignKeyConstraint(['player2_faction_id'], ['factions.id']),
        sa.ForeignKeyConstraint(['winner_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['resolved_by_admin_id'], ['users.id']),
    )
    op.create_index('ix_matchups_status', 'matchups', ['status'])
    
    # Create location verifications table
    op.create_table(
        'matchup_locations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('matchup_id', sa.String(50), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        
        sa.ForeignKeyConstraint(['matchup_id'], ['matchups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_matchup_locations_matchup_id', 'matchup_locations', ['matchup_id'])
    op.create_index('ix_matchup_locations_user_id', 'matchup_locations', ['user_id'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('matchup_locations')
    op.drop_table('matchups')
    op.drop_table('factions')
    op.drop_table('email_verification_tokens')
    op.drop_table('users')
