from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)


class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    """
    Base repository implementing the Repository Pattern.

    This abstract class provides common CRUD operations and ensures
    all database operations return clean Pydantic models instead of
    SQLAlchemy objects.
    """

    def __init__(self, session: Session):
        self._session = session

    @property
    @abstractmethod
    def _model(self) -> type[ModelType]:
        """Return the SQLAlchemy model class."""
        pass

    @property
    @abstractmethod
    def _response_schema(self) -> type[ResponseSchemaType]:
        """Return the Pydantic response schema class."""
        pass

    def _to_response(self, db_obj: ModelType | None) -> ResponseSchemaType | None:
        """Convert SQLAlchemy model to Pydantic response schema."""
        if db_obj is None:
            return None
        return self._response_schema.model_validate(db_obj)

    def _to_response_list(self, db_objs: list[ModelType]) -> list[ResponseSchemaType]:
        """Convert list of SQLAlchemy models to list of Pydantic response schemas."""
        return [self._response_schema.model_validate(obj) for obj in db_objs]

    def get_by_id(self, id: int) -> ResponseSchemaType | None:
        """Get a single record by ID."""
        db_obj = self._session.query(self._model).filter(self._model.id == id).first()
        return self._to_response(db_obj)

    def get_all(self) -> list[ResponseSchemaType]:
        """Get all records."""
        db_objs = self._session.query(self._model).all()
        return self._to_response_list(db_objs)

    def create(self, schema: CreateSchemaType) -> ResponseSchemaType:
        """Create a new record."""
        db_obj = self._model(**schema.model_dump())
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return self._to_response(db_obj)

    def update(self, id: int, schema: UpdateSchemaType) -> ResponseSchemaType | None:
        """Update an existing record."""
        db_obj = self._session.query(self._model).filter(self._model.id == id).first()
        if db_obj is None:
            return None

        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self._session.flush()
        self._session.refresh(db_obj)
        return self._to_response(db_obj)

    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        db_obj = self._session.query(self._model).filter(self._model.id == id).first()
        if db_obj is None:
            return False
        self._session.delete(db_obj)
        self._session.flush()
        return True

    def commit(self) -> None:
        """Commit the current transaction."""
        self._session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self._session.rollback()
