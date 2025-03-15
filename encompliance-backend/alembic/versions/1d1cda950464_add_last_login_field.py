"""add_last_login_field

Revision ID: 1d1cda950464
Revises: rename_pdf_to_document
Create Date: 2025-03-15 00:06:09.314267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d1cda950464'
down_revision = 'rename_pdf_to_document'
branch_labels = None
depends_on = None


def upgrade():
    # Add last_login column to users table
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    # Remove last_login column from users table
    op.drop_column('users', 'last_login') 