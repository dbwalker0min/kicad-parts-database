from dataclasses import dataclass, field
from sqlalchemy import Column, Integer, String, ForeignKey, Table, MetaData, Boolean
from sqlalchemy.schema import CreateTable
from enum import StrEnum

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


def copy_column_with_new_name(column: Column, new_name: str) -> Column:
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
    """
    name: str
    visible_on_add: bool = False
    visible_in_chooser: bool = False
    show_name: bool = False
    inherit_properties: bool = False
    description: str = ''
    computed: str = None
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

KiCadDatabaseColumn = Column | KiCadField | KiCadProperty

class KiCadTableDefinition:
    """Base class for KiCad table definitions."""

    _registered_tables = []

    def __init_subclass__(cls, table: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)
        if table:
            KiCadTableDefinition._registered_tables.append(cls)

    @classmethod
    def get_registered_tables(cls):
        """Get the registered tables."""
        return cls._registered_tables   


    @classmethod
    def get_kicad_fields(cls):
        """Get the KiCad fields of the table."""
        fields = {}
        for attr in dir(cls):
            value = getattr(cls, attr)
            if isinstance(value, KiCadDatabaseColumn):
                fields[attr] = value
        return fields

    @classmethod
    def generate_table(cls):
        """Generate a SQLAlchemy table definition."""

        fields = cls.get_kicad_fields()
        columns: list[Column] = []
        for name, field in fields.items():
            if isinstance(field, KiCadField):
                # KiCAD fields are *always* strings
                if field.computed:
                    expression = field.computed.format(prefix=cls.prefix)
                    field.other_column_options = {'server_default': expression}
                columns.append(Column(name, String, comment=field.description, **field.other_column_options))
            elif isinstance(field, KiCadProperty):
                # The type depends on the property. If there is "except" in the name, it is a boolean, otherwise it is a string
                if field.which in (KiCadPropertySpec.EXCLUDE_FROM_BOM, KiCadPropertySpec.EXCLUDE_FROM_BOARD, KiCadPropertySpec.EXCLUDE_FROM_SIM):
                    columns.append(Column(name, field.which.value, Boolean, comment=field.description))
                else:
                    columns.append(Column(name, String, comment=field.description))
            elif isinstance(field, Column):
                # This is already a SQLAlchemy column. I need to adjust the name of the field to the name of the field

                columns.append(copy_column_with_new_name(field, name))
        tab = Table(cls.__name__.lower(), metadata, *columns)

        sql = str(CreateTable(tab).compile(compile_kwargs={"literal_binds": True}))
        print(sql)
        return tab