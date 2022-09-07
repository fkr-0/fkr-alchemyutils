# SPDX-FileCopyrightText: 2022-present cbadger <void@some.where>
#
# SPDX-License-Identifier: MIT

#!/usr/bin/env python3
from typing import Tuple
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, event
from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import declarative_base
from .crud_mixin import CRUDMixin

"""alchemyutils - A collection of utilities for Alchemy"""


def setup_schema(Base, session):
    """
    Function for adding sessions to model classes. Sets model._session
    and to provided session instance and allows querying from the class.
    """

    def setup_schema_fn():
        # for class_ in Base._decl_class_registry.values():
        for class_ in Base.registry._class_registry.values():
            if hasattr(class_, "__tablename__"):
                # console.log(f"Assigning {session} to {class_}")
                setattr(class_, "_session", session)
                setattr(class_, "query", session.query(class_))

    return setup_schema_fn


Base = declarative_base(cls=CRUDMixin)


def setup_db(path) -> Tuple[Session, Engine]:
    """Setup the database"""

    global Base
    engine = create_engine(path)

    Session = sessionmaker(bind=engine)
    session = Session()
    event.listen(mapper, "after_configured", setup_schema(Base, session))
    Base.metadata.create_all(engine)
    Base.registry.configure()
    return session, engine
