from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


@dataclass
class KiCadTableField:
    """Class to represent a field in a KiCad table. This represents extra data to generate a KiCad database symbol library. See [KiCAD documentation](https://docs.kicad.org/8.0/en/eeschema/eeschema_advanced.html#database-libraries)]

    Attributes:
        name (str): The name of the KiCad field to populate from the database.
        visible_on_add (bool): If true, this field will be visible in the schematic when a symbol is added
        visible_in_chooser (bool): If true, this field will be shown in the Symbol Chooser as a column
        show_name (bool): If true, the fields name will be shown in addition to its value in the schematic
        inherit_properties (bool): If true, and a field with the given name already exists on the source symbol, only the field contents will be updated from the database, and the other properties (visible_on_add, show_name, etc) will be kept as they were set in the source symbol. If the given field name does not exist in the source symbol, this setting is ignored
    """
    name: str
    visible_on_add: bool = False
    visible_in_chooser: bool = False
    show_name: bool = False
    inherit_properties: bool = False


KiCadFieldProperty = {
    "exclude_from_bom",
    "exclude_from_board",
    "exclude_from_sim",
    "keywords",
}

class KiCadDatabase(ABC):
    @abstractmethod
    def prefix(self):
        """Return the prefix for the component type"""
        ...
