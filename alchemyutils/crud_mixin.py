#!/usr/bin/env python3
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declared_attr
import logging
from typing import Dict, List, Literal, Union

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declared_attr

log = logging.getLogger(__name__)


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations.
    The methods are implemented as class methods, therefore they do not make use of "self" parameter of class instances but
    expect a given instance to be provided as parameter."""

    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def create(cls, *args, **kwargs):
        # def create(cls, data):
        """Create a new record and save it the database."""
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        instance = cls(*args, **clean_kwargs)
        log.debug(f"Adding {clean_kwargs}")
        return cls.save(instance)

    @classmethod
    # def update(cls, record, commit=True, **kwargs):
    def update(cls, record, data: Dict, commit: bool = True):
        """Update specific fields of a record."""
        for attr, value in data.items():
            setattr(record, attr, value)
        log.debug(f"Updating {record}")
        if commit:
            return cls.save(record)
        return record

    @classmethod
    def save(cls, record, commit: bool = True):
        """Save the record."""
        try:
            if not record.id:
                cls._session.add(record)
            if commit:
                cls._session.commit()
        except IntegrityError as e:
            cls._session.rollback()
            raise e
        return record

    @classmethod
    def delete(cls, record, commit: bool = True) -> None:
        """Remove the record from the database."""
        cls._session.delete(record)
        if commit:
            return cls._session.commit()
        return

    @classmethod
    def get(
        cls, criterion: Union["CRUDMixin", dict, int]
    ) -> Union[List["CRUDMixin"], "CRUDMixin", Literal[None]]:
        # convenience: if we get an int we assume itsthe id
        r = None
        if isinstance(criterion, cls):
            return criterion
        elif isinstance(criterion, int):
            return cls.query.filter_by(id=criterion).one()
        elif isinstance(criterion, dict):
            r = cls.query.filter_by(**criterion).all()
        else:
            raise ValueError("No plausible value to filter found")
        if len(r) == 1:
            return r[0]
        elif len(r) == 0:
            return None
        else:
            return r

    @classmethod
    def all(cls):
        return cls.query.all()
