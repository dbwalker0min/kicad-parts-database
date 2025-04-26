
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


class Capacitor(BaseTable, table=True, computed_vars={'prefix': 'CAP'}):
    """
    Capacitor table definition. Inherits from BaseTable. The value property gives the capacitance.
    """
    voltage_rating = KiCadField(
        name="Voltage", description="Voltage rating of the capacitor")
    tolerance = KiCadField(
        name="Tolerance", description="Tolerance of the capacitor")
    dielectric = KiCadField(
        name="Dielectric", description="Dielectric of the capacitor")


class Connector(BaseTable, table=True, computed_vars={'prefix': 'CON'}):
    """
    Connector table definition. Inherits from BaseTable. The value property gives it the name of the connector.
    """
    connector_type: str = KiCadField('Type', description="Type of connector")
    pitch: str = KiCadField('Pitch', description="Pitch of the connector")


class CrystalOscillator(BaseTable, table=True, computed_vars={'prefix': 'XTL'}):
    """
    Crystal and Oscillator table definition. Inherits from BaseTable. The value property gives the frequency.
    """
    accuracy: str = KiCadField(
        "Accuracy", description="Accuracy of the crystal or oscillator")
    load_capacitance: str = KiCadField("Load Capacitance",
                                       description="Load capacitance of the crystal or oscillator")


class IC(BaseTable, table=True, computed_vars={'prefix': 'IC'}):
    """
    IC table definition. Inherits from BaseTable. The value property gives the part number of the IC.
    """
    ic_type: str = KiCadField('IC Type', description="Type of IC")


class Inductor(BaseTable, table=True, computed_vars={'prefix': 'IND'}):
    """
    Inductor table definition. Inherits from BaseTable. The value property gives the inductance.
    """
    current_rating: str = KiCadField(
        'Current Rating', description="Current rating of the inductor")
    dc_resistance: str = KiCadField(
        'DC Resistance', description="DC resistance of the inductor")


class Mechanical(BaseTable, table=True, computed_vars={'prefix': 'MECH'}):
    """
    Mechanical table definition. Inherits from BaseTable. The value property gives the name of the mechanical part.
    """
    mechanical_type: str = KiCadField(
        'Type', description="Type of mechanical part")


class Misc(BaseTable, table=True, computed_vars={'prefix': 'MIS'}):
    """
    Misc table definition. Inherits from BaseTable. The value property gives the name of the part.
    """
    misc_type: str = KiCadField('Type', description="Type of misc part")


class Relay(BaseTable, table=True, computed_vars={'prefix': 'RLY'}):
    """
    Relay table definition. Inherits from BaseTable. The value property gives the part number of the relay.
    """
    relay_type: str = KiCadField('Type', description="Type of relay")
    coil_voltage: str = KiCadField(
        'Voltage', description="Coil voltage of the relay")
    contact_rating: str = KiCadField(
        'Current', description="Contact rating of the relay")


class Switch(BaseTable, table=True, computed_vars={'prefix': 'SW'}):
    """
    Switch table definition. Inherits from BaseTable. The value property gives the name of the switch.
    """
    switch_type: str = KiCadField('Type', description="Type of switch")
    current_rating: str = KiCadField(
        'Current', description="Current rating of the switch")
    voltage_rating: str = KiCadField('Voltage',
                                     description="Voltage rating of the switch")


class Transformer(BaseTable, table=True, computed_vars={'prefix': 'XFR'}):
    """
    Transformer table definition. Inherits from BaseTable. The value property gives the name of the transformer.
    """
    transformer_type: str = KiCadField('Type',
                                       description="Type of transformer")
    power_rating: str = KiCadField('Power',
                                   description="Power rating of the transformer")


class Transistor(BaseTable, table=True, computed_vars={'prefix': 'XTR'}):
    """
    Transistor table definition. Inherits from BaseTable. The value property gives the part number of the transistor.
    """
    transistor_type: str = KiCadField('Type',
                                      description="Type of transistor")
    current: str = KiCadField(
        'Current', description="Collector current or drain current of the transistor")
    voltage: str = KiCadField(
        'Voltage', description="Collector emitter or drain source voltage of the transistor")


if __name__ == "__main__":
    tabs = build_tables()
    engine = create_engine(
        'postgresql+psycopg2://kicad-user:QAiaw8do7NHa4PvDakdR@eplant-eng.info:5432/kicad_part_database', echo=True)
    metadata.create_all(engine)
