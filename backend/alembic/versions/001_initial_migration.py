"""Initial migration with all models

Revision ID: 001_initial
Revises: 
Create Date: 2024-02-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create personas table
    op.create_table('personas',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('occupation', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('traits', sa.JSON(), nullable=True),
        sa.Column('communication_style', sa.Text(), nullable=False),
        sa.Column('backstory', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('scammer_identifier', sa.String(), nullable=False),
        sa.Column('persona_id', sa.String(length=36), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'STALLING', 'COMPLETED', 'ABANDONED', name='conversationstatus'), nullable=False),
        sa.Column('scam_type', sa.String(), nullable=True),
        sa.Column('detection_confidence', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('total_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_scammer_identifier'), 'conversations', ['scammer_identifier'], unique=False)
    
    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('sender_type', sa.Enum('SCAMMER', 'HONEYPOT', name='sendertype'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('analysis', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create intelligence table
    op.create_table('intelligence',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('artifact_type', sa.Enum('UPI_ID', 'BANK_ACCOUNT', 'IFSC_CODE', 'PHONE', 'URL', 'EMAIL', name='artifacttype'), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('extracted_at', sa.DateTime(), nullable=False),
        sa.Column('validated', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create scammer_profiles table
    op.create_table('scammer_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('identifier', sa.String(), nullable=False),
        sa.Column('known_aliases', sa.JSON(), nullable=True),
        sa.Column('first_seen', sa.DateTime(), nullable=False),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('total_conversations', sa.Integer(), nullable=True),
        sa.Column('linked_intelligence', sa.JSON(), nullable=True),
        sa.Column('threat_score', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier')
    )
    op.create_index(op.f('ix_scammer_profiles_identifier'), 'scammer_profiles', ['identifier'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_scammer_profiles_identifier'), table_name='scammer_profiles')
    op.drop_table('scammer_profiles')
    op.drop_table('intelligence')
    op.drop_table('messages')
    op.drop_index(op.f('ix_conversations_scammer_identifier'), table_name='conversations')
    op.drop_table('conversations')
    op.drop_table('personas')
