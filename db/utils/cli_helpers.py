from sqlmodel import SQLModel
from typing import Type, Any


def listar(crud, model: Type[SQLModel]) -> None:
    """Lista todas as instâncias de um modelo"""
    itens = crud.get_all(model)
    for item in itens:
        print(item)


def buscar(crud, model: Type[SQLModel], id_: Any) -> None:
    """Busca uma instância pelo ID"""
    item = crud.get_by_id(model, id_)
    if item:
        print(item)
    else:
        print(f"Nenhum registro encontrado com id={id_}")


def deletar(crud, session, model: Type[SQLModel], id_: Any) -> None:
    """Remove uma instância pelo ID"""
    item = crud.get_by_id(model, id_)
    if item:
        session.delete(item)
        session.commit()
        print(f"Registro com id={id_} removido com sucesso.")
    else:
        print(f"Nenhum registro encontrado com id={id_}")


def criar(crud, model: Type[SQLModel], **campos) -> None:
    """Cria uma nova instância a partir dos campos fornecidos"""
    instancia = model(**campos)
    crud.create(instancia)
    print(f"Criado: {instancia}")
