from dataclasses import dataclass, field
from typing import Any, Self
from sqlalchemy import Column, Integer, String, ForeignKey, Table, MetaData, Boolean
from sqlalchemy.schema import CreateTable
from enum import StrEnum
from copy import deepcopy

metadata = MetaData()


# See https://docs.kicad.org/master/en/eeschema/eeschema_advanced.html#database-libraries for more information on the database libraries.

class KiCadPropertySpec(StrEnum):
    """Enum to represent identify a database field as a KiCAD property"""
    FOOTPRINT_FILTERS = 'footprint_filters',
    VALUE = 'value',
    DATASHEET = 'datasheet',
    KEYWORDS = 'keywords',
    DESCRIPTION = 'description',
    EXCLUDE_FROM_BOM = 'exclude_from_bom',
    EXCLUDE_FROM_BOARD = 'exclude_from_board',
    EXCLUDE_FROM_SIM = 'exclude_from_sim',


def _copy_column_with_new_name(column: Column, new_name: str) -> Column:
    """Create a copy of a SQLAlchemy Column with a new name.
    This necessary because SQLAlchemy does not allow to change the name of a column after it has been created.

    Args
    ----------
    column: Column
        The column to copy.
    new_name: str
        The new name of the column.
    """
    return Column(
        new_name,  # Override the name
        column.type,  # Copy the type
        *column.foreign_keys,  # Copy foreign keys
        primary_key=column.primary_key,
        autoincrement=column.autoincrement,
        nullable=column.nullable,
        default=column.default,
        server_default=column.server_default,
        unique=column.unique,
        index=column.index,
        comment=column.comment,
        info=column.info,
    )


@dataclass
class KiCadField:
    """Dataclass to represent a KiCad value.

    Dataclass Items
    ----------
    name: str
        The name of the KiCad property.  
    visible_on_add: bool
        Whether the field is visible when adding a new part.
    visible_in_chooser: bool
        Whether the field is visible in the chooser.
    show_name: bool
        Whether to show the name of the field.
    inherit_properties: bool
        Whether to inherit properties from the parent.
    description: str
        The description of the field.
    computed: str
        The computed value of the field. This is a SQLAlchemy expression that can be used to generate the value of the field.   
    other_column_options: dict
        Other options for the column. This is a dictionary that can contain any additional options for the column.
    """
    name: str
    visible_on_add: bool = False
    visible_in_chooser: bool = False
    show_name: bool = False
    inherit_properties: bool = False
    description: str = ''
    computed: str = ''
    other_column_options: dict = field(default_factory=dict)


@dataclass
class KiCadProperty:
    """Dataclass to represent a KiCad property.

    Dataclass Items
    ----------
    which: KiCadPropertySpec
        The KiCad property specification.
    description: str
        The description of the property.
    """
    which: KiCadPropertySpec
    description: str = ''


"""This type is used to represent a KiCad database column."""
KiCadDatabaseColumn = Column | KiCadField | KiCadProperty


class KiCadTableDefinition:
    """Base class for KiCad table definitions

    Keyword arguments
    ----------
        table: bool : str, optional
            If true, the table will be generated
        key : str, optional
            The column name containing a unique key that will be used to identify parts from the table. If
            this field does not occur in the model, it will be automatically created. Defaults to 'key'.
        symbol : str, optional
            The column name containing KiCad symbol references. If
            this field does not occur in the model, it will be automatically created. Defaults to 'symbol'.
        footprint : str, optional
            The column name containing KiCad footprint references. If
            this field does not occur in the model, it will be automatically created. Defaults to 'footprint'.
        computed_vars : dict, optional
            A dictionary of variables to be used in created columns for the table. Defaults to an empty dictionary.
        **kwargs : dict
            Additional keyword arguments passed to the superclass initializer.
    """

    """Class variables:
    ----------
    _key_column_name: str
        The column name containing a unique key that will be used to identify parts from the table.
    _symbol_column_name: str
        The column name containing KiCad symbol references.
    _footprint_column_name: str
        The column name containing KiCad footprint references.
    _computed_vars: dict
        A dictionary of variables to be used in created columns for the table.
    _table_name: str
        The name of the table.
    _registered_tables: list[Self]
        A list of all registered KiCad database tables.
    """

    _key_column_name: str = 'key'
    _symbol_column_name: str = 'symbol'
    _footprint_column_name: str = 'footprint'
    _computed_vars: dict[str, Any] = dict()
    _table_name: str = ''
    _registered_tables: list[Self] = []

    def __init_subclass__(cls, table: bool = False, key: str = '', symbol: str = '', footprint: str = '', computed_vars: dict[str, Any] = {}, **kwargs):
        """This method is called when a class is subclassed."""
        super().__init_subclass__(**kwargs)

        # save these parameters for later use

        if key:
            cls._key_column_name = key
        if symbol:
            cls._symbol_column_name = symbol
        if footprint:
            cls._footprint_column_name = footprint
        cls._set_computed_vars(computed_vars)

        # if any parameters are defined, then I intend on building the table
        if table:
            cls._table_name = cls.__name__.lower()
            cls._register_table()

    @classmethod
    def get_kicad_fields(cls) -> dict[str, KiCadDatabaseColumn]:
        """Get the KiCad fields of the table as a dictionary."""
        return {k: getattr(cls, k) for k in dir(cls) if isinstance(getattr(cls, k), KiCadDatabaseColumn)}

    @classmethod
    def _generate_table_columns(cls) -> list[Column]:
        """Generate the SQLAlchemy table definition."""

        fields = cls.get_kicad_fields()
        columns: list[Column] = cls._default_columns(fields)

        for name, field in fields.items():
            if isinstance(field, KiCadField):
                if not field.name:
                    raise ValueError(f"Field {name} has no name defined. Please define the name of the field in the KiCadField definition.")
                
                # KiCAD fields are *always* strings
                options: dict[str, Any] = field.other_column_options.copy()
                if field.computed:
                    options['server_default'] = field.computed.format(
                        **cls._get_computed_vars())
                columns.append(
                    Column(name, String, comment=field.description, **options))
            elif isinstance(field, KiCadProperty):
                # The type depends on the property. If there is "except" in the name, it is a boolean, otherwise it is a string
                if field.which in (KiCadPropertySpec.EXCLUDE_FROM_BOM, KiCadPropertySpec.EXCLUDE_FROM_BOARD, KiCadPropertySpec.EXCLUDE_FROM_SIM):
                    columns.append(Column(name, Boolean, comment=field.description))
                else:
                    columns.append(Column(name, String, comment=field.description))
            elif isinstance(field, Column):
                # This is already a SQLAlchemy column. I need to adjust the name of the field to the name of the field
                columns.append(_copy_column_with_new_name(field, name))

        return columns

    @classmethod
    def _default_columns(cls, fields: dict[str, KiCadDatabaseColumn]) -> list[Column]:
        """Add default columns (key, symbol, footprint) if not defined."""
        columns: list[Column] = []

        # default for the key, symbol and footprint columns
        defaults = [
            (cls._key_column_name, String, "Unique key for the part", True),
            (cls._symbol_column_name, String, "KiCad symbol reference", False),
            (cls._footprint_column_name, String, "KiCad footprint reference", False),
        ]
        return [
            Column(name, col_type, primary_key=is_primary, comment=comment)
            for name, col_type, comment, is_primary in defaults
            if name not in fields
        ]

    @classmethod
    def _get_computed_vars(cls) -> dict[str, Any]:
        """Get a copy of the computed variables."""
        return deepcopy(cls._computed_vars)
    
    @classmethod
    def _set_computed_vars(cls, vars: dict[str, Any]):
        """Set a computed variable."""
        cls._computed_vars = deepcopy(vars)

    @classmethod
    def _register_table(cls):
        """Register the table."""
        if cls not in cls._registered_tables:
            cls._registered_tables.append(cls)
    
    @classmethod
    def _get_registered_tables(cls) -> list[Self]:
        """Get the registered tables."""
        return cls._registered_tables.copy()
    
    @property
    def table(self) -> Table:
        """Get the SQLAlchemy table definition."""
        return Table(self._table_name, metadata, *self._generate_table_columns(), extend_existing=True)

def build_tables() -> list[Table]:
    """Build the tables."""
    return [table.table for table in KiCadTableDefinition._get_registered_tables()]
