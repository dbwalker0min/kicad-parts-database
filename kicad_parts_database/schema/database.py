from sqlalchemy import Column, String, Integer, Boolean, create_engine, Computed
from kicad_parts_database.kicad_db import KiCadDatabaseTable, KiCadProperty, kicad_field, kicad_property, generate_kicad_dbl, Base
from sqlalchemy.orm import class_mapper

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


class BasePart(KiCadDatabaseTable):
    """
    Base definition for symblols. These are common for all tables. The field datatypes are all strings because that's all that KiCAD allows.
    """
    __abstract__ = True

    prefix: str = 'TBD'
    pretty_table_name: str = 'TBD'

    # this is a sequence number for each new component. It is only used as an index.
    sequence_number = Column(Integer, autoincrement=True, primary_key=True, index=True,
                                 comment="Sequence number of the component")

    # these properties *must* be defined in the KiCAD `.kicad_dbl` file
    footprint = Column(String, default='TBD', comment="Footprint of the component")
    symbol = Column(String, default=None, comment="Symbol of the component")

    # these are fields and propertites that can be transsferred to KiCAD
    part_number = kicad_field(name='Part Number', visible_in_chooser=True,
                                   visible_on_add=False, show_name=False, inherit_properties=True,
                                   server_default=Computed(f'{prefix}-{sequence_number}'), 
                                   comment="Part number of the component")

    value = kicad_property(KiCadProperty.VALUE, comment="Value of the component")
    comment = kicad_property(KiCadProperty.comment, comment="comment of the component")
    datasheet = kicad_property(KiCadProperty.DATASHEET, comment="URL to the datasheet of the component")
    keywords = kicad_property(KiCadProperty.KEYWORDS, comment="Type of the component. Formatted as a path, like typeA/typeB")
    step_model = kicad_field('Step Model', comment="Step model for the component")
    package_type = kicad_field('Package Type', visible_in_chooser=True, visible_on_add=False, show_name=False, inherit_properties=True,
        comment="Human readable package type for the component, like QFNnn, TQFPnn, etc.")

    # these are fields that are not used in KiCAD, but can be used for other purposes (like BOM generation)
    number_of_pins = Column(Integer, default=None, comment="Number of pins for the component")
    series = Column(String, default='', comment="Series of the component")
    manufacturer_name = Column(String, default=None, comment="Manufacturer name")
    manufacturer_part_number = Column(String, default=None, comment="Manufacturer's part number of the component")

class KiCadTableProperties:
    # define the table properties
    key = 'part_number'
    symbol = 'symbol'
    footprint = 'footprint'


class Capacitor(BasePart):
    """
    Capacitor table definition. Inherits from BasePart. The value property gives the capacitance.
    """
    __tablename__ = 'capacitors'

    prefix: str = 'CAP'
    pretty_table_name: str = 'Capacitors'


    voltage_rating = kicad_field(
        name="Voltage", comment="Voltage rating of the capacitor")
    tolerance = kicad_field(
        name="Tolerance", comment="Tolerance of the capacitor")
    dielectric = kicad_field(
        name="Dielectric", comment="Dielectric of the capacitor")



class Resistor(BasePart):
    """
    Resistor table definition. Inherits from BasePart. The value property gives the resistance.
    """

    __tablename__ = 'resistors'

    prefix: str = 'RES'
    pretty_table_name: str = 'Resistors'


    power_rating = kicad_field('Power', comment="Power rating of the resistor in watts")
    tolerance = kicad_field('Tolerance', comment="Tolerance of the resistor")


# The following classes are not used in the current implementation, but are left here for reference. They can be used in the future if needed.
def Field(*args, **kwargs):
    pass

if 0:
    class Connector(BasePart, table=True):
        """
        Connector table definition. Inherits from BasePart. The value property gives it the name of the connector.
        """
        connector_type: str = Field(
            default=None, comment="Type of connector")
        pitch: str = Field(default=None, comment="Pitch of the connector")

        def prefix(self):
            return "CON"

        def pretty_table_name(self) -> str:
            return "Connectors"

    class CrystalOscillator(BasePart, table=True):
        """
        Crystal and Oscillator table definition. Inherits from BasePart. The value property gives the frequency.
        """
        accuracy: str = Field(
            default=None, comment="Accuracy of the crystal or oscillator")
        load_capacitance: str = Field(
            default=None, comment="Load capacitance of the crystal or oscillator")

        def prefix(self):
            return "XTL"

        def pretty_table_name(self) -> str:
            return "Crystals and Oscillators"

    class Diode(BasePart, table=True):
        """
        Diode table definition. Inherits from BasePart. The value property gives the part number of the diode.
        """
        diode_type: str = Field(default=None, comment="Type of diode")
        reverse_voltage: str = Field(
            default=None, comment="Reverse voltage of the diode")
        forward_current: str = Field(
            default=None, comment="Forward current of the diode")

        def prefix(self):
            return "DIO"

    class IC(BasePart, table=True):
        """
        IC table definition. Inherits from BasePart. The value property gives the part number of the IC.
        """
        ic_type: str = Field(default=None, comment="Type of IC")

        def prefix(self):
            return "IC"

    class Inductor(BasePart, table=True):
        """
        Inductor table definition. Inherits from BasePart. The value property gives the inductance.
        """
        current_rating: str = Field(
            default=None, comment="Current rating of the inductor")
        dc_resistance: str = Field(
            default=None, comment="DC resistance of the inductor")

        def prefix(self):
            return "IND"

    class Mechanical(BasePart, table=True):
        """
        Mechanical table definition. Inherits from BasePart. The value property gives the name of the mechanical part.
        """
        mechanical_type: str = Field(
            default=None, comment="Type of mechanical part")

        def prefix(self):
            return "MECH"

    class Misc(BasePart, table=True):
        """
        Misc table definition. Inherits from BasePart. The value property gives the name of the part.
        """
        misc_type: str = Field(default=None, comment="Type of misc part")

        def prefix(self):
            return "MIS"

    class Relay(BasePart, table=True):
        """
        Relay table definition. Inherits from BasePart. The value property gives the part number of the relay.
        """
        relay_type: str = Field(default=None, comment="Type of relay")
        coil_voltage: str = Field(
            default=None, comment="Coil voltage of the relay")
        contact_rating: str = Field(
            default=None, comment="Contact rating of the relay")

        def prefix(self):
            return "REL"

    class Switch(BasePart, table=True):
        """
        Switch table definition. Inherits from BasePart. The value property gives the name of the switch.
        """
        switch_type: str = Field(default=None, comment="Type of switch")
        current_rating: str = Field(
            default=None, comment="Current rating of the switch")
        voltage_rating: str = Field(
            default=None, comment="Voltage rating of the switch")

        def prefix(self):
            return "SW"

    class Transformer(BasePart, table=True):
        """
        Transformer table definition. Inherits from BasePart. The value property gives the name of the transformer.
        """
        transformer_type: str = Field(
            default=None, comment="Type of transformer")
        power_rating: str = Field(
            default=None, comment="Power rating of the transformer")

        def prefix(self):
            return "XFR"

    class Transistor(BasePart, table=True):
        """
        Transistor table definition. Inherits from BasePart. The value property gives the part number of the transistor.
        """
        transistor_type: str = Field(
            default=None, comment="Type of transistor")
        current: str = Field(
            default=None, comment="Collector current or drain current of the transistor")
        voltage: str = Field(
            default=None, comment="Collector emitter or drain source voltage of the transistor")

        def prefix(self):
            return "XTR"

    class Distributor():
        """
        Distributor table definition. This is a separate table because it can be used for all parts. The part number is a foreign key to the part number in the part table.
        """
        distributor_id: int = Field(
            primary_key=True, index=True, comment="Distributor ID")
        distributor_name: str = Field(
            default=None, comment="Distributor name")
        distributor_part_number: str = Field(
            default=None, comment="Distributor's part number of the component")
        url: str = Field(
            default=None, comment="URL of the distributor for the component")
        price: str = Field(
            default=None, comment="Price of the component from the distributor")
        quantity: str = Field(
            default=None, comment="Quantity of the component from the distributor")


def main():
    engine = create_engine(
        "postgresql+psycopg2://kicad-user:QAiaw8do7NHa4PvDakdR@eplant-eng.info:5432/kicad_part_database")
    
    # Base.metadata.create_all(engine)

    def introspect_model(model):
        """Print the columns and their `info` metadata for a given ORM model."""
        mapper = class_mapper(model)
        print(f"Table: {mapper.local_table.name}")
        for column in mapper.columns:
            print(f"  Column: {column.name}")
            print(f"    Info: {column.info}")

    # Example usage
    introspect_model(Capacitor)
    introspect_model(Resistor)


if __name__ == "__main__":
    main()
