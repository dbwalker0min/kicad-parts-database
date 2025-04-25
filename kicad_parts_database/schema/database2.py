
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.schema import CreateTable
from kicad_parts_database.kicad_db.db_definitions import KiCadTableDefinition, KiCadField, KiCadProperty, KiCadPropertySpec, metadata, build_tables

# See https://docs.kicad.org/master/en/eeschema/eeschema_advanced.html#database-libraries for more information on the database libraries.

"""
The libraries defined are:
    * Capacitors (prefix "CAP")
    * Connectors (prefix "CON")
    * Crystals and Oscillators (prefix "XTL")
    * Diodes (prefix "DIO")
    * ICs (prefix "IC")
    * Inductors (prefix "IND")
    * Mechanical (prefix "MECH")
    * Misc (prefix "MIS")
    * Relays (prefix "REL")
    * Resistors (prefix "RES")
    * Switches (prefix "SW")
    * Transformers (prefix "XFR")
    * Transistors (prefix "XTR")
"""


class BaseTable(KiCadTableDefinition, key='part_number'):
    """Base class for KiCad table definitions."""

    sequence_number = Column(Integer, autoincrement=True, primary_key=True, index=True,
                             comment="Sequence number of the component")
    # these properties *must* be defined in the KiCAD `.kicad_dbl` file
    footprint = Column(String, default='TBD',
                       comment="Footprint of the component")
    symbol = Column(String, default=None, comment="Symbol of the component")

    # these are fields and propertites that can be transsferred to KiCAD
    part_number = KiCadField('Part Number', visible_in_chooser=True,
                             computed="{prefix} || '-' || LPAD(sequence_number::TEXT, 5, '0')",
                             description="Part number of the component")

    value = KiCadProperty(KiCadPropertySpec.VALUE,
                          description="Value of the component")
    description = KiCadProperty(
        KiCadPropertySpec.DESCRIPTION, description="Description of the component")
    datasheet = KiCadProperty(KiCadPropertySpec.DATASHEET,
                              description="URL to the datasheet of the component")
    keywords = KiCadProperty(KiCadPropertySpec.KEYWORDS,
                             description="Type of the component. Formatted as a path, like typeA/typeB")
    exclude_from_bom = KiCadProperty(
        KiCadPropertySpec.EXCLUDE_FROM_BOM, description="Exclude from BOM")
    step_model = KiCadField(
        'Step Model', description="Step model for the component")
    package_type = KiCadField('Package Type', visible_in_chooser=True, visible_on_add=False, show_name=False, inherit_properties=True,
                              description="Human readable package type for the component, like QFNnn, TQFPnn, etc.")

    # these are fields that are not used in KiCAD, but can be used for other purposes (like BOM generation)
    number_of_pins = Column(Integer, default=None,
                            comment="Number of pins for the component")
    series = Column(String, default='', comment="Series of the component")
    manufacturer_name = Column(
        String, default=None, comment="Manufacturer name")
    manufacturer_part_number = Column(
        String, default=None, comment="Manufacturer's part number of the component")


class Resistors(BaseTable, table=True, computed_vars={'prefix': 'RES'}):

    """Class for Resistors table definition."""
    power_rating = KiCadField(
        'Power', description="Power rating of the resistor in watts")
    tolerance = KiCadField(
        'Tolerance', description="Tolerance of the resistor")


if __name__ == "__main__":
    tabs = build_tables()
    print(type(tabs[0]))
    print(metadata.tables)
    #engine = create_engine('postgresql+psycopg2://kicad-user:QAiaw8do7NHa4PvDakdR@eplant-eng.info:5432/kicad_part_database', echo=True)
    #metadata.create_all(engine)