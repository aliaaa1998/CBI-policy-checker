"""initial tables"""
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("documents", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(255), nullable=False), sa.Column("source_filename", sa.String(255), nullable=False, unique=True), sa.Column("page_count", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("pages", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=False), sa.Column("page_number", sa.Integer(), nullable=False), sa.Column("ocr_engine", sa.String(30), nullable=False), sa.Column("ocr_confidence", sa.Float(), nullable=True), sa.Column("original_text", sa.Text(), nullable=False), sa.Column("normalized_text", sa.Text(), nullable=False), sa.Column("extracted_at", sa.DateTime(), nullable=False))
    op.create_table("chunks", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=False), sa.Column("page_number", sa.Integer(), nullable=False), sa.Column("chunk_index", sa.Integer(), nullable=False), sa.Column("section_title", sa.String(255), nullable=True), sa.Column("original_text", sa.Text(), nullable=False), sa.Column("normalized_text", sa.Text(), nullable=False), sa.Column("ocr_confidence", sa.Float(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("ingestion_runs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("status", sa.String(30), nullable=False), sa.Column("request_id", sa.String(80), nullable=False), sa.Column("details", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("query_runs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("request_id", sa.String(80), nullable=False), sa.Column("question", sa.Text(), nullable=False), sa.Column("model", sa.String(80), nullable=False), sa.Column("response", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("compliance_runs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("request_id", sa.String(80), nullable=False), sa.Column("scenario", sa.Text(), nullable=False), sa.Column("model", sa.String(80), nullable=False), sa.Column("response", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))


def downgrade() -> None:
    op.drop_table("compliance_runs")
    op.drop_table("query_runs")
    op.drop_table("ingestion_runs")
    op.drop_table("chunks")
    op.drop_table("pages")
    op.drop_table("documents")
