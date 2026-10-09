
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Base, engine, SessionLocal
from models.cliente import Cliente

app = Flask(__name__)

Base.metadata.create_all(bind=engine)


@app.route("/")
def inicio():
    with SessionLocal() as session:
        clientes = session.scalars(
            select(Cliente).order_by(Cliente.nome)
        ).all()

    return render_template("index.html", clientes=clientes)


@app.route("/clientes", methods=["POST"])
def cadastrar_cliente():
    nome = request.form.get("nome", "").strip()
    telefone = request.form.get("telefone", "").strip()
    email = request.form.get("email", "").strip().lower()

    if not nome or not telefone or not email:
        return "Preencha todos os campos.", 400

    with SessionLocal() as session:
        cliente = Cliente(
            nome=nome,
            telefone=telefone,
            email=email
        )
        session.add(cliente)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            return "Este e-mail já está cadastrado.", 409

    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)
