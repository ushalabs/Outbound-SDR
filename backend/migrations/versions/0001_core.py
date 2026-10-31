"""Isolated SDR schema. Frozen DDL, never touches unrelated schemas."""
from pathlib import Path

from alembic import op

revision = "0001_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    ddl = Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")
    for statement in ddl.split(";\n"):
        if statement.strip():
            op.execute(statement.strip())


def downgrade():
    raise RuntimeError("Automatic destructive downgrades are disabled. Restore an isolated test schema explicitly.")
