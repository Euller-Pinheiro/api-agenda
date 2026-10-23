"""Cria profissionais, serviços, clientes e o vínculo profissional-serviço.

Revisão: 52c79e96e1c2
Anterior: nenhuma (primeira migração)
Criada em: 2026-10-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "52c79e96e1c2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cliente",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("telefone", sa.String(length=11), nullable=True),
        sa.Column(
            "criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cliente")),
        sa.UniqueConstraint("email", name=op.f("uq_cliente_email")),
    )
    op.create_table(
        "profissional",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_profissional")),
        sa.UniqueConstraint("email", name=op.f("uq_profissional_email")),
    )
    op.create_table(
        "servico",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("descricao", sa.String(length=500), nullable=True),
        sa.Column("duracao_minutos", sa.Integer(), nullable=False),
        sa.Column("preco_centavos", sa.Integer(), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("duracao_minutos > 0", name=op.f("ck_servico_duracao_positiva")),
        sa.CheckConstraint("preco_centavos >= 0", name=op.f("ck_servico_preco_nao_negativo")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_servico")),
        sa.UniqueConstraint("nome", name=op.f("uq_servico_nome")),
    )
    op.create_table(
        "profissional_servico",
        sa.Column("profissional_id", sa.Integer(), nullable=False),
        sa.Column("servico_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["profissional_id"],
            ["profissional.id"],
            name=op.f("fk_profissional_servico_profissional_id_profissional"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["servico_id"],
            ["servico.id"],
            name=op.f("fk_profissional_servico_servico_id_servico"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "profissional_id", "servico_id", name=op.f("pk_profissional_servico")
        ),
    )


def downgrade() -> None:
    op.drop_table("profissional_servico")
    op.drop_table("servico")
    op.drop_table("profissional")
    op.drop_table("cliente")
