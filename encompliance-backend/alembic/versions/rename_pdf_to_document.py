"""rename_pdf_to_document

Revision ID: rename_pdf_to_document
Revises: 10cbb240bc52
Create Date: 2025-03-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_pdf_to_document'
down_revision = '10cbb240bc52'
branch_labels = None
depends_on = None


def upgrade():
    # Create new documents table
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('filepath', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    
    # Copy data from pdfs to documents if the pdfs table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'pdfs' in tables:
        # Copy data from pdfs to documents, adding new columns
        conn.execute(
            """
            INSERT INTO documents (id, filename, filepath, uploaded_at, uploaded_by, is_deleted, deleted_at, deleted_by, file_type, file_size)
            SELECT id, filename, filepath, uploaded_at, uploaded_by, is_deleted, deleted_at, deleted_by, 'PDF', 0
            FROM pdfs
            """
        )
        
        # Drop the old pdfs table
        op.drop_table('pdfs')


def downgrade():
    # Create the pdfs table
    op.create_table('pdfs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('filepath', sa.String(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pdfs_id'), 'pdfs', ['id'], unique=False)
    
    # Copy data back from documents to pdfs, dropping the new columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'documents' in tables:
        conn.execute(
            """
            INSERT INTO pdfs (id, filename, filepath, uploaded_at, uploaded_by, is_deleted, deleted_at, deleted_by)
            SELECT id, filename, filepath, uploaded_at, uploaded_by, is_deleted, deleted_at, deleted_by
            FROM documents
            """
        )
        
        # Drop the new documents table
        op.drop_table('documents') 