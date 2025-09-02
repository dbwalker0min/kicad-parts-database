from src.api.v1.main import part_to_kicad_fields
from src.definitions.parts import Part
from pprint import pprint

test_part = Part(
    id=1,
    sequence_number=1,
    name="10uF_X5R_16V-00001",
    category_id=1,
    value="10uF",
    footprint="Capacitor_SMD:C_0805_2012Metric",
    symbol_id="Device:C",
    description="10uF 16V X5R 0805",
    reference="C?",
    keywords="capacitor 10uF X5R 16V",
    datasheet="https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BR61C106KE15-01.pdf",
)


def test_part_to_kicad_fields_minimal():
    result = {'exclude_from_board': 'False',
              'exclude_from_bom': 'False',
              'exclude_from_sim': 'False',
              'fields': {'datasheet': {'value': 'https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BR61C106KE15-01.pdf', 'visible': 'False'},
                         'description': {'value': '10uF 16V X5R 0805', 'visible': 'False'},
                         'footprint': {'value': 'Capacitor_SMD:C_0805_2012Metric',
                                       'visible': 'False'},
                         'keywords': {'value': 'capacitor 10uF X5R 16V', 'visible': 'False'},
                         'reference': {'value': 'C?', 'visible': 'True'},
                         'value': {'value': '10uF', 'visible': 'True'}},
              'id': '1',
              'name': '10uF_X5R_16V-00001',
              'symbolIdStr': 'Device:C'}

    fields = part_to_kicad_fields(test_part)
    pprint(fields)
    assert fields == result


def test_part_with_custom_field1():
    p = test_part.model_copy(update={
        "fields": dict(Manufacturer="Murata")
        })

    fields = part_to_kicad_fields(p)
    assert fields["fields"]["Manufacturer"] == {
        "value": "Murata", "visible": "False"}


def test_part_with_custom_field2():
    p = test_part.model_copy(update={
        "fields": dict(
            Manufacturer="Murata",
            Voltage=dict(value="16V", visible=True),
        )})

    fields=part_to_kicad_fields(p)
    assert fields["fields"]["Voltage"] == dict(value="16V", visible="True")

def test_part_with_custom_field3():
    p = test_part.model_copy(update={
        "fields": dict(
            Manufacturer="Murata",
            Voltage=dict(value="16V", visible=False),
        )})

    fields=part_to_kicad_fields(p)
    assert fields["fields"]["Voltage"] == dict(value="16V", visible="False")
