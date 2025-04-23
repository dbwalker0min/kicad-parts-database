from abc import ABC, ABCMeta, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import Any
from sqlalchemy import inspect, Engine, Column, String, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from dataclasses import dataclass
from typing import Any, Type


@dataclass
class KiCadTableProperties:
    key: str = 'key'
    symbols: str = 'symbols'
    footprints: str = 'footprints'


class KiCadProperty(StrEnum):
    """Enum to represent identify a database field as a KiCAD property"""
    comment = 'comment',
    FOOTPRINT_FILTERS = 'footprint_filters',
    VALUE = 'value',
    DATASHEET = 'datasheet',
    KEYWORDS = 'keywords',
    EXCLUDE_FROM_BOM = 'exclude_from_bom',
    EXCLUDE_FROM_BOARD = 'exclude_from_board',
    EXCLUDE_FROM_SIM = 'exclude_from_sim',


def generate_kicad_dbl(engine: Engine, properties: KiCadTableProperties = KiCadTableProperties(), filename: Path = Path('database_lib.kicad_dbl')) -> None:
    """Iterate over all SQLModel tables and extract the `info` fields from their columns."""
    pass

def kicad_property(which: KiCadProperty, comment='', **kwargs) -> Column[Any]:
    """Define a table column to represent a KiCAD property."""
    if 'default' not in kwargs:
        kwargs['default'] = None
    info = dict(
        KiCadColumn=True,
        which=which,
        comment=comment
    )
    print(info)
    if which.startswith('exclude'):
        kwargs['default'] = False
        return Column(Boolean, info=info, **kwargs)
    else:
        kwargs['default'] = ''
        return Column(String, info=info, **kwargs)


def kicad_field(name: str, visible_on_add: bool = False, visible_in_chooser: bool = False, show_name: bool = False, inherit_properties: bool = False, comment='', **kwargs) -> Column[Any]:
    """Define a table column to represent a KiCAD field."""
    info = dict(
        KiCadColumn=True,
        name=name,
        visible_on_add=visible_on_add,
        visible_in_chooser=visible_in_chooser,
        show_name=show_name,
        inherit_properties=inherit_properties,
        comment=comment,
    )
    return Column(String, default='', info=info, **kwargs)



Base: Type[Any] = declarative_base()


class KiCadDatabaseTable(Base):
    """Base class for all KiCad database tables. This is used to define the common properties of all tables."""
    __abstract__ = True
