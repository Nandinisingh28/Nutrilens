"""Initial migration with all tables and seed data

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('avatar_file_id', sa.Integer(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('goal', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Create file_assets table
    op.create_table(
        'file_assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('owner_user_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.Enum('label_image', 'avatar', name='filekind'), nullable=False),
        sa.Column('storage_path', sa.String(512), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_file_assets_owner_user_id', 'file_assets', ['owner_user_id'])
    
    # Add foreign key for user avatar after file_assets exists
    op.create_foreign_key(
        'fk_users_avatar_file_id',
        'users', 'file_assets',
        ['avatar_file_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_categories_slug', 'categories', ['slug'], unique=True)
    
    # Create scans table
    op.create_table(
        'scans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('label_image_file_id', sa.Integer(), nullable=True),
        sa.Column('product_name', sa.String(255), nullable=True),
        sa.Column('brand', sa.String(255), nullable=True),
        sa.Column('claim_text', sa.Text(), nullable=True),
        sa.Column('ocr_raw_text', mysql.LONGTEXT(), nullable=True),
        sa.Column('parsed_ingredients', sa.JSON(), nullable=True),
        sa.Column('parsed_nutrition', sa.JSON(), nullable=True),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('overall_verdict', sa.Enum('true', 'misleading', 'false', 'mixed', 'unknown', name='overallverdict'), nullable=False, default='unknown'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['label_image_file_id'], ['file_assets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scans_user_id', 'scans', ['user_id'])
    op.create_index('ix_scans_category_id', 'scans', ['category_id'])
    
    # Create rules table
    op.create_table(
        'rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('rule_type', sa.Enum('sugar_alias', 'additive', 'claim_threshold', 'claim_pattern', name='ruletype'), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_rules_category_id', 'rules', ['category_id'])
    op.create_index('ix_rules_rule_type', 'rules', ['rule_type'])
    op.create_index('ix_rules_key', 'rules', ['key'])
    
    # Seed categories
    op.execute("""
        INSERT INTO categories (slug, title, description) VALUES
        ('protein-bars', 'Protein Bars', 'High protein snack bars and energy bars'),
        ('breakfast-cereals', 'Breakfast Cereals', 'Cereals, granolas, and breakfast foods')
        ON DUPLICATE KEY UPDATE title=VALUES(title)
    """)
    
    # Seed sugar aliases (global rules)
    sugar_aliases = [
        'glucose syrup', 'maltodextrin', 'dextrose', 'fructose', 'sucrose',
        'invert sugar', 'corn syrup', 'high fructose corn syrup', 'hfcs',
        'jaggery', 'honey', 'agave', 'maple syrup', 'molasses', 'brown sugar',
        'cane sugar', 'coconut sugar', 'date syrup', 'rice syrup', 'barley malt'
    ]
    for alias in sugar_aliases:
        op.execute(f"""
            INSERT INTO rules (category_id, rule_type, `key`, value, is_active) VALUES
            (NULL, 'sugar_alias', '{alias}', '{{"alias": "{alias}", "is_sugar": true}}', 1)
            ON DUPLICATE KEY UPDATE value=VALUES(value)
        """)
    
    # Seed claim patterns (global rules)
    claim_patterns = [
        ('high protein', '{"description": "Claims high protein content"}'),
        ('no added sugar', '{"description": "Claims no added sugars"}'),
        ('low sugar', '{"description": "Claims low sugar content"}'),
        ('no preservatives', '{"description": "Claims no preservatives"}'),
        ('100% natural', '{"description": "Claims all natural ingredients"}'),
        ('whole grain', '{"description": "Claims whole grain content"}'),
        ('healthy', '{"description": "Generic health claim"}'),
        ('sugar free', '{"description": "Claims no sugar"}'),
        ('zero sugar', '{"description": "Claims zero sugar"}'),
    ]
    for pattern, value in claim_patterns:
        op.execute(f"""
            INSERT INTO rules (category_id, rule_type, `key`, value, is_active) VALUES
            (NULL, 'claim_pattern', '{pattern}', '{value}', 1)
            ON DUPLICATE KEY UPDATE value=VALUES(value)
        """)
    
    # Seed claim thresholds (global rules)
    thresholds = [
        ('high_protein', '{"min_per_100g": 10, "min_calories_percent": 20, "unit": "g", "description": ">=10g per 100g OR >=20% calories from protein"}'),
        ('low_sugar', '{"max_per_100g": 5, "unit": "g", "description": "<=5g sugar per 100g"}'),
        ('no_added_sugar', '{"sugar_aliases_must_not_appear": true, "description": "Fail if any sugar alias appears in ingredients"}'),
        ('whole_grain', '{"must_be_in_top_n_ingredients": 3, "description": "Whole grain must appear in top 3 ingredients"}'),
        ('low_fat', '{"max_per_100g": 3, "unit": "g", "description": "<=3g fat per 100g"}'),
        ('high_fiber', '{"min_per_100g": 6, "unit": "g", "description": ">=6g fiber per 100g"}'),
    ]
    for key, value in thresholds:
        op.execute(f"""
            INSERT INTO rules (category_id, rule_type, `key`, value, is_active) VALUES
            (NULL, 'claim_threshold', '{key}', '{value}', 1)
            ON DUPLICATE KEY UPDATE value=VALUES(value)
        """)


def downgrade() -> None:
    op.drop_table('rules')
    op.drop_table('scans')
    op.drop_table('categories')
    op.drop_constraint('fk_users_avatar_file_id', 'users', type_='foreignkey')
    op.drop_table('file_assets')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS filekind")
    op.execute("DROP TYPE IF EXISTS overallverdict")
    op.execute("DROP TYPE IF EXISTS ruletype")
