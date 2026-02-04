"""Add two-image scan support

Revision ID: 002
Revises: 001
Create Date: 2026-02-01

Adds columns for separate ingredients and nutrition images,
plus separate OCR text fields for each.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new image file ID columns to scans table
    op.add_column(
        'scans',
        sa.Column('ingredients_image_file_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        'scans',
        sa.Column('nutrition_image_file_id', sa.Integer(), nullable=True)
    )
    
    # Add new OCR text columns for separate sources
    op.add_column(
        'scans',
        sa.Column('ocr_raw_ingredients_text', mysql.LONGTEXT(), nullable=True)
    )
    op.add_column(
        'scans',
        sa.Column('ocr_raw_nutrition_text', mysql.LONGTEXT(), nullable=True)
    )
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_scans_ingredients_image',
        'scans',
        'file_assets',
        ['ingredients_image_file_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_scans_nutrition_image',
        'scans',
        'file_assets',
        ['nutrition_image_file_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Update file_assets.kind enum to include new types
    # MySQL-specific: ALTER TABLE to modify ENUM
    op.execute("""
        ALTER TABLE file_assets 
        MODIFY COLUMN kind ENUM('label_image', 'ingredients_image', 'nutrition_image', 'avatar') NOT NULL
    """)


def downgrade() -> None:
    # Remove foreign keys first
    op.drop_constraint('fk_scans_ingredients_image', 'scans', type_='foreignkey')
    op.drop_constraint('fk_scans_nutrition_image', 'scans', type_='foreignkey')
    
    # Remove columns
    op.drop_column('scans', 'ocr_raw_nutrition_text')
    op.drop_column('scans', 'ocr_raw_ingredients_text')
    op.drop_column('scans', 'nutrition_image_file_id')
    op.drop_column('scans', 'ingredients_image_file_id')
    
    # Revert enum (only if no rows use new values)
    op.execute("""
        ALTER TABLE file_assets 
        MODIFY COLUMN kind ENUM('label_image', 'avatar') NOT NULL
    """)
