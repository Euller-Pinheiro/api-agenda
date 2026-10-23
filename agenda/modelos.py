"""Tabelas do domínio de agendamento.

Decisões que valem para o projeto todo:
- dinheiro em centavos (inteiro): float erra na soma (0.1 + 0.2 != 0.3);
- e-mail único e sempre gravado em minúsculas, para "Ana@x.com" e "ana@x.com"
  não virarem duas pessoas;
- regras simples (duração positiva, preço não negativo) também viram
  CHECK no banco, para valer mesmo se alguém gravar sem passar pela API.
"""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    MetaData,
    String,
    Table,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Nomes previsíveis para índices e restrições: facilitam as migrações e as
# mensagens de erro do banco.
CONVENCAO_NOMES = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENCAO_NOMES)


class ComDatas:
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# Quais serviços cada profissional atende (muitos para muitos).
profissional_servico = Table(
    "profissional_servico",
    Base.metadata,
    Column(
        "profissional_id",
        ForeignKey("profissional.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "servico_id",
        ForeignKey("servico.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Profissional(ComDatas, Base):
    __tablename__ = "profissional"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    ativo: Mapped[bool] = mapped_column(default=True, server_default="true")

    servicos: Mapped[list["Servico"]] = relationship(
        secondary=profissional_servico,
        back_populates="profissionais",
        order_by="Servico.nome",
    )


class Servico(ComDatas, Base):
    __tablename__ = "servico"
    __table_args__ = (
        CheckConstraint("duracao_minutos > 0", name="duracao_positiva"),
        CheckConstraint("preco_centavos >= 0", name="preco_nao_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True)
    descricao: Mapped[str | None] = mapped_column(String(500))
    duracao_minutos: Mapped[int]
    preco_centavos: Mapped[int]
    ativo: Mapped[bool] = mapped_column(default=True, server_default="true")

    profissionais: Mapped[list[Profissional]] = relationship(
        secondary=profissional_servico, back_populates="servicos"
    )


class Cliente(ComDatas, Base):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(254), unique=True)
    telefone: Mapped[str | None] = mapped_column(String(11))
