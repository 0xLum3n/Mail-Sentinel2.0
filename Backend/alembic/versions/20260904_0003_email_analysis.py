"""add email ingestion and analysis schema

Revision ID: 20260904_0003
Revises: 20260904_0002
Create Date: 2026-09-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260904_0003"
down_revision: Union[str, None] = "20260904_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "email_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message_hash", sa.String(length=64), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=64), server_default="email_upload", nullable=False),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("sender_email", sa.String(length=320), nullable=True),
        sa.Column("recipient_email", sa.String(length=320), nullable=True),
        sa.Column("reply_to_email", sa.String(length=320), nullable=True),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("body_html", sa.Text(), nullable=True),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("headers", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_messages_org_created", "email_messages", ["organization_id", "created_at"], unique=False)
    op.create_index("ix_email_messages_org_sender", "email_messages", ["organization_id", "sender_email"], unique=False)
    op.create_index("ix_email_messages_org_message_hash", "email_messages", ["organization_id", "message_hash"], unique=False)

    op.create_table(
        "email_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["email_id"], ["email_messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_attachments_email", "email_attachments", ["email_id"], unique=False)
    op.create_index("ix_email_attachments_sha256", "email_attachments", ["sha256"], unique=False)

    op.create_table(
        "email_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="queued", nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=True),
        sa.Column("threat_type", sa.String(length=64), nullable=True),
        sa.Column("verdict", sa.String(length=64), nullable=True),
        sa.Column("confidence_score", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("auth_results", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("engine_version", sa.String(length=64), nullable=True),
        sa.Column("ai_provider", sa.String(length=64), nullable=True),
        sa.Column("ai_model", sa.String(length=128), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('queued', 'running', 'completed', 'failed')", name="ck_email_analyses_status"),
        sa.CheckConstraint("severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="ck_email_analyses_severity"),
        sa.CheckConstraint("risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)", name="ck_email_analyses_risk_score"),
        sa.CheckConstraint("confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)", name="ck_email_analyses_confidence_score"),
        sa.ForeignKeyConstraint(["email_id"], ["email_messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_analyses_email_created", "email_analyses", ["email_id", "created_at"], unique=False)
    op.create_index("ix_email_analyses_org_created", "email_analyses", ["organization_id", "created_at"], unique=False)
    op.create_index("ix_email_analyses_org_risk", "email_analyses", ["organization_id", "risk_score"], unique=False)

    op.create_table(
        "analysis_findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("weight", sa.Integer(), server_default="0", nullable=False),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="ck_analysis_findings_severity"),
        sa.CheckConstraint("source IN ('rule', 'threat_intel', 'ai')", name="ck_analysis_findings_source"),
        sa.ForeignKeyConstraint(["analysis_id"], ["email_analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_findings_analysis", "analysis_findings", ["analysis_id"], unique=False)

    op.create_table(
        "indicators",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("verdict", sa.String(length=16), server_default="Unknown", nullable=False),
        sa.Column("confidence_score", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("enrichment", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("type IN ('IP', 'URL', 'DOMAIN', 'HASH', 'EMAIL')", name="ck_indicators_type"),
        sa.CheckConstraint("verdict IN ('Unknown', 'Benign', 'Suspicious', 'Malicious', 'Phishing')", name="ck_indicators_verdict"),
        sa.ForeignKeyConstraint(["analysis_id"], ["email_analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_indicators_analysis_type", "indicators", ["analysis_id", "type"], unique=False)
    op.create_index("ix_indicators_type_value", "indicators", ["type", "value"], unique=False)

    op.create_table(
        "mitre_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tactic", sa.String(length=128), nullable=False),
        sa.Column("technique_id", sa.String(length=32), nullable=True),
        sa.Column("technique_name", sa.String(length=255), nullable=False),
        sa.Column("confidence_score", sa.Integer(), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["analysis_id"], ["email_analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mitre_mappings_analysis", "mitre_mappings", ["analysis_id"], unique=False)
    op.create_index("ix_mitre_mappings_technique", "mitre_mappings", ["technique_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_mitre_mappings_technique", table_name="mitre_mappings")
    op.drop_index("ix_mitre_mappings_analysis", table_name="mitre_mappings")
    op.drop_table("mitre_mappings")
    op.drop_index("ix_indicators_type_value", table_name="indicators")
    op.drop_index("ix_indicators_analysis_type", table_name="indicators")
    op.drop_table("indicators")
    op.drop_index("ix_analysis_findings_analysis", table_name="analysis_findings")
    op.drop_table("analysis_findings")
    op.drop_index("ix_email_analyses_org_risk", table_name="email_analyses")
    op.drop_index("ix_email_analyses_org_created", table_name="email_analyses")
    op.drop_index("ix_email_analyses_email_created", table_name="email_analyses")
    op.drop_table("email_analyses")
    op.drop_index("ix_email_attachments_sha256", table_name="email_attachments")
    op.drop_index("ix_email_attachments_email", table_name="email_attachments")
    op.drop_table("email_attachments")
    op.drop_index("ix_email_messages_org_message_hash", table_name="email_messages")
    op.drop_index("ix_email_messages_org_sender", table_name="email_messages")
    op.drop_index("ix_email_messages_org_created", table_name="email_messages")
    op.drop_table("email_messages")
