
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app as aplicacao
from database import Base
from models.cliente import Cliente


@pytest.fixture
def cliente_teste(monkeypatch):
    engine_teste = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine_teste)
    SessaoTeste = sessionmaker(bind=engine_teste)

    monkeypatch.setattr(aplicacao, "SessionLocal", SessaoTeste)
    aplicacao.app.config["TESTING"] = True

    with aplicacao.app.test_client() as cliente:
        yield cliente

    Base.metadata.drop_all(bind=engine_teste)
    engine_teste.dispose()


def test_pagina_inicial_carrega(cliente_teste):
    resposta = cliente_teste.get("/")

    assert resposta.status_code == 200
    assert b"Cadastro de clientes" in resposta.data


def test_cadastro_de_cliente(cliente_teste):
    resposta = cliente_teste.post(
        "/clientes",
        data={
            "nome": "Maria Silva",
            "telefone": "61999999999",
            "email": "MARIA@EXEMPLO.COM",
        },
    )

    assert resposta.status_code == 302

    with aplicacao.SessionLocal() as sessao:
        cliente = sessao.scalar(
            select(Cliente).where(
                Cliente.email == "maria@exemplo.com"
            )
        )
        assert cliente is not None
        assert cliente.nome == "Maria Silva"


def test_cadastro_com_campos_vazios(cliente_teste):
    resposta = cliente_teste.post(
        "/clientes",
        data={
            "nome": "",
            "telefone": "61999999999",
            "email": "maria@exemplo.com",
        },
    )

    assert resposta.status_code == 400
    assert b"Preencha todos os campos." in resposta.data


def test_email_duplicado(cliente_teste):
    dados = {
        "nome": "Maria Silva",
        "telefone": "61999999999",
        "email": "maria@exemplo.com",
    }

    primeira_resposta = cliente_teste.post("/clientes", data=dados)
    segunda_resposta = cliente_teste.post(
        "/clientes",
        data={
            **dados,
            "nome": "Maria Souza",
        },
    )

    assert primeira_resposta.status_code == 302
    assert segunda_resposta.status_code == 409
    assert b"Este e-mail j\xc3\xa1 est\xc3\xa1 cadastrado." in segunda_resposta.data
