from typing import TypeVar, Type, Optional, List, Any
from sqlmodel import SQLModel, Session, select

# Tipo genérico para os modelos
T = TypeVar("T", bound=SQLModel)


class ModelManager:
    def __init__(self, session: Session):
        self.session = session

    # ----- Métodos genéricos -----
    def get_by_field(self, model_class, field_name: str, value):
        """Busca genérica por qualquer campo."""
        field = getattr(model_class, field_name)
        stmt = select(model_class).where(field == value)
        return self.session.exec(stmt).first()

    def get_all(self, model: Type[T]) -> List[T]:
        return self.session.exec(select(model)).all()

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: T, data: dict) -> T:
        for key, value in data.items():
            setattr(obj, key, value)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.commit()

