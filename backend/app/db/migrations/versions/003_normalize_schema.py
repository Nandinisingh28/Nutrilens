"""Normalize schema

Revision ID: 003
Revises: 002
Create Date: 2026-02-02

Normalized products, ingredients, nutrition_facts, claims, and verification_results.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('brand', sa.String(length=255), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_products_category_id_categories', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_products')
    )
    op.create_index('ix_products_category_id', 'products', ['category_id'], unique=False)

    # 2. Create ingredients table
    op.create_table(
        'ingredients',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('is_sugar_alias', sa.Boolean(), nullable=False),
        sa.Column('is_additive', sa.Boolean(), nullable=False),
        sa.Column('is_preservative', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_ingredients_product_id_products', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_ingredients')
    )
    op.create_index('ix_ingredients_product_id', 'ingredients', ['product_id'], unique=False)

    # 3. Create nutrition_facts table
    op.create_table(
        'nutrition_facts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_nutrition_facts_product_id_products', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_nutrition_facts')
    )
    op.create_index('ix_nutrition_facts_product_id', 'nutrition_facts', ['product_id'], unique=False)

    # 4. Create claims table
    op.create_table(
        'claims',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scan_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], name='fk_claims_scan_id_scans', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_claims')
    )
    op.create_index('ix_claims_scan_id', 'claims', ['scan_id'], unique=False)

    # 5. Create verification_results table
    op.create_table(
        'verification_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scan_id', sa.Integer(), nullable=False),
        sa.Column('claim_id', sa.Integer(), nullable=False),
        sa.Column('verdict', sa.Enum('true', 'misleading', 'false', 'mixed', 'unknown', name='overallverdict'), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['claim_id'], ['claims.id'], name='fk_verification_results_claim_id_claims', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], name='fk_verification_results_scan_id_scans', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_verification_results')
    )
    op.create_index('ix_verification_results_claim_id', 'verification_results', ['claim_id'], unique=False)
    op.create_index('ix_verification_results_scan_id', 'verification_results', ['scan_id'], unique=False)

    # 6. Modify scans table
    op.add_column('scans', sa.Column('product_id', sa.Integer(), nullable=True))
    op.add_column('scans', sa.Column('raw_results', sa.JSON(), nullable=True))
    op.create_foreign_key('fk_scans_product_id_products', 'scans', 'products', ['product_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_scans_product_id', 'scans', ['product_id'], unique=False)
    
    # Note: We keep product_name and brand for now but they're technically deprecated.
    # We remove the JSON fields
    op.drop_column('scans', 'parsed_ingredients')
    op.drop_column('scans', 'parsed_nutrition')
    op.drop_column('scans', 'results')


def downgrade():
    # 1. Re-add columns to scans
    op.add_column('scans', sa.Column('results', mysql.JSON(), nullable=True))
    op.add_column('scans', sa.Column('parsed_nutrition', mysql.JSON(), nullable=True))
    op.add_column('scans', sa.Column('parsed_ingredients', mysql.JSON(), nullable=True))
    
    # 2. Drop foreign key and columns from scans
    op.drop_constraint('fk_scans_product_id_products', 'scans', type_='foreignkey')
    op.drop_index('ix_scans_product_id', table_name='scans')
    op.drop_column('scans', 'raw_results')
    op.drop_column('scans', 'product_id')

    # 3. Drop tables
    op.drop_table('verification_results')
    op.drop_table('claims')
    op.drop_table('nutrition_facts')
    op.drop_table('ingredients')
    op.drop_table('products')
