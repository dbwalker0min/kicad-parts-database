from sqlmodel import Field, SQLModel, create_engine
from kicad_parts_database.kicad_db import KiCadDatabase, KiCadTableField, KiCadFieldProperty

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

class BasePart(SQLModel, KiCadDatabase):
    """
    Base definition for symblols. These are common for all tables. The datatypes are all strings because that's all that KiCAD allows.
    """
    part_number: str = Field(primary_key=True, index=True, description="Part number of the component", info=KiCadTableField(name="Part Number", inherit_properties=True))
    value: str = Field(default=None, description="Value of the component", info=KiCadTableField(name="Value", inherit_properties=True))
    description: str = Field(default='', description="Description of the component", info=KiCadTableField(name="Description", inherit_properties=True))
    datasheet: str = Field(default=None, description="URL to the datasheet of the component", info=KiCadTableField(name="Datasheet", inherit_properties=True))
    keywords: str = Field(default=None, description="Type of the component. Formatted as a path, like typeA/typeB", info=KiCadFieldProperty.keywords)
    footprint: str = Field(default=None, description="Footprint of the component", info=KiCadTableField(name="Footprint", inherit_properties=True)) 
    symbol: str = Field(default=None, description="Symbol of the component", info=KiCadTableField(name="Symbol", inherit_properties=True))
    step_model: str = Field(default=None, description="Step model for the component")
    number_of_pins: str = Field(default=None, description="Number of pins for the component")
    package_type: str = Field(default=None, description="Short package type for the component, like QFNnn, TQFPnn, etc.")
    series: str = Field(default='', description="Series of the component")

class Capacitor(BasePart, table=True):
    """
    Capacitor table definition. Inherits from BasePart. The value property gives the capacitance.
    """
    voltage_rating: str = Field(default=None, description="Voltage rating of the capacitor")
    tolerance: str = Field(default=None, description="Tolerance of the capacitor")
    dielectric: str = Field(default=None, description="Dielectric of the capacitor")

    def prefix(self):
        return "CAP"

class Connector(BasePart, table=True):
    """
    Connector table definition. Inherits from BasePart. The value property gives it the name of the connector.
    """
    connector_type: str = Field(default=None, description="Type of connector")
    pitch: str = Field(default=None, description="Pitch of the connector")

    def prefix(self):
        return "CON"

class CrystalOscillator(BasePart, table=True):
    """
    Crystal and Oscillator table definition. Inherits from BasePart. The value property gives the frequency.
    """
    accuracy: str = Field(default=None, description="Accuracy of the crystal or oscillator")
    load_capacitance: str = Field(default=None, description="Load capacitance of the crystal or oscillator")

    def prefix(self):
        return "XTL"

class Diode(BasePart, table=True):
    """
    Diode table definition. Inherits from BasePart. The value property gives the part number of the diode.
    """
    diode_type: str = Field(default=None, description="Type of diode")
    reverse_voltage: str = Field(default=None, description="Reverse voltage of the diode")
    forward_current: str = Field(default=None, description="Forward current of the diode")

    def prefix(self):
        return "DIO"

class IC(BasePart, table=True):
    """
    IC table definition. Inherits from BasePart. The value property gives the part number of the IC.
    """
    ic_type: str = Field(default=None, description="Type of IC")

    def prefix(self):
        return "IC"

class Inductor(BasePart, table=True):
    """
    Inductor table definition. Inherits from BasePart. The value property gives the inductance.
    """
    current_rating: str = Field(default=None, description="Current rating of the inductor")
    dc_resistance: str = Field(default=None, description="DC resistance of the inductor")

    def prefix(self):
        return "IND"

class Mechanical(BasePart, table=True):
    """
    Mechanical table definition. Inherits from BasePart. The value property gives the name of the mechanical part.
    """
    mechanical_type: str = Field(default=None, description="Type of mechanical part")

    def prefix(self):    
        return "MECH"

class Misc(BasePart, table=True):
    """
    Misc table definition. Inherits from BasePart. The value property gives the name of the part.
    """
    misc_type: str = Field(default=None, description="Type of misc part")   

    def prefix(self):    
        return "MIS"

class Relay(BasePart, table=True):
    """
    Relay table definition. Inherits from BasePart. The value property gives the part number of the relay.
    """
    relay_type: str = Field(default=None, description="Type of relay")
    coil_voltage: str = Field(default=None, description="Coil voltage of the relay")
    contact_rating: str = Field(default=None, description="Contact rating of the relay")

    def prefix(self):
        return "REL"    

class Resistor(BasePart, table=True):
    """
    Resistor table definition. Inherits from BasePart. The value property gives the resistance.
    """
    power_rating: str = Field(default=None, description="Power rating of the resistor in watts")
    tolerance: str = Field(default=None, description="Tolerance of the resistor")

    def prefix(self):
        return "RES"    

class Switch(BasePart, table=True):
    """
    Switch table definition. Inherits from BasePart. The value property gives the name of the switch.
    """
    switch_type: str = Field(default=None, description="Type of switch")
    current_rating: str = Field(default=None, description="Current rating of the switch")
    voltage_rating: str = Field(default=None, description="Voltage rating of the switch")   

    def prefix(self):
        return "SW"

class Transformer(BasePart, table=True):
    """
    Transformer table definition. Inherits from BasePart. The value property gives the name of the transformer.
    """
    transformer_type: str = Field(default=None, description="Type of transformer")
    power_rating: str = Field(default=None, description="Power rating of the transformer")

    def prefix(self):
        return "XFR"    

class Transistor(BasePart, table=True):
    """
    Transistor table definition. Inherits from BasePart. The value property gives the part number of the transistor.
    """
    transistor_type: str = Field(default=None, description="Type of transistor")
    current: str = Field(default=None, description="Collector current or drain current of the transistor")
    voltage: str = Field(default=None, description="Collector emitter or drain source voltage of the transistor")

    def prefix(self):
        return "XTR"

class Manufacturer(SQLModel, table=True):
    """
    Manufacturer table definition. This is a separate table because it can be used for all parts. The part number is a foreign key to the part number in the part table.
    """
    manufacturer_id: int = Field(primary_key=True, index=True, description="Manufacturer ID")
    manufacturer_name: str = Field(default=None, description="Manufacturer name")
    manufacturer_part_number: str = Field(default=None, description="Manufacturer's part number of the component")


class Distributor(SQLModel, table=True):
    """
    Distributor table definition. This is a separate table because it can be used for all parts. The part number is a foreign key to the part number in the part table.
    """
    distributor_id: int = Field(primary_key=True, index=True, description="Distributor ID")
    distributor_name: str = Field(default=None, description="Distributor name")
    distributor_part_number: str = Field(default=None, description="Distributor's part number of the component")
    url: str = Field(default=None, description="URL of the distributor for the component")
    price: str = Field(default=None, description="Price of the component from the distributor")
    quantity: str = Field(default=None, description="Quantity of the component from the distributor")

def main():
    engine = create_engine("postgresql+psycopg2://kicad-user:QAiaw8do7NHa4PvDakdR@eplant-eng.info:5432/kicad_part_database")

    print('Creating database tables...')
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    main()