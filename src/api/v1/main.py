# routes_kicad.py
from fastapi import APIRouter, Depends, HTTPException, FastAPI
from sqlmodel import SQLModel, Field, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.definitions import Category, Part
from src.db import get_session, engine
from dataclasses import dataclass

app = FastAPI()

router = APIRouter(prefix="/kicad-api/v1")

@dataclass
class CommonFieldSpec:
    """Dataclass to hold info about fields that KiCad always wants (including the visibility)"""
    name: str
    visible: bool = False
    
# These are fields that KiCad always needs. As such, they are fixed in the database schema. I don't want collisions with the json fields.
# If you want to add more fields, add them to the `fields` JSONB column.
# Note that KiCad will show all fields by default unless you set "visible" to "False" in the field dict.
# Example: fields = {"footprint": {"value": "Resistor_SMD:R_0805_2012Metric", "visible": "False"}, "my_custom_field": {"value": "foo", "visible": "True"}}
FIXED_FIELDS: list[CommonFieldSpec] = [
    CommonFieldSpec("footprint", False),
    CommonFieldSpec("datasheet", False),
    CommonFieldSpec("value", True),
    CommonFieldSpec("reference", True),
    CommonFieldSpec("description", False),
    CommonFieldSpec("keywords", False),
]

FIXED_FIELD_NAMES = (f.name.lower() for f in FIXED_FIELDS)

def part_to_kicad_fields(part: Part) -> dict[str, str | dict]:
    """
    Convert a Part instance to the dict format KiCad expects for part details.
    This includes converting all values to strings, and ensuring certain fields are always present.
    This is a separate function to allow easier unit testing.
    """                     
    # KiCad wants string booleans and a nested fields dict with {"value", "visible"}
    def to_bool_str(x: str | bool | int) -> str:  # ensure strings only
        if isinstance(x, str) and x.lower() in ("1", "true", "yes", "y"):
            return "True"
        elif isinstance(x, (bool, int)):
            return str(x)
        else:
            return "False"

    fields = {}

    # these are fields that KiCad always wants
    for item in FIXED_FIELDS:
        val = getattr(part, item.name, "")
        fields[item.name] = dict(value= "" if val is None else str(val), visible= to_bool_str(item.visible))

    for k, v in (part.fields or {}).items():

        # check to make sure we don't overwrite fixed fields
        # This supports both {"field": "value"} and {"field": {"value": "x", "visible": "True"}}.
        if k.lower() not in FIXED_FIELD_NAMES:
            if isinstance(v, dict) and "value" in v:
                visibility = v.get("visible", "False")
                fields[k] = dict(value= "" if v["value"] is None else str(v["value"]), visible= to_bool_str(v.get("visible", False)))
            elif isinstance(v, str):
                fields[k] = {"value": v, "visible": "False"}

    return {
        "id": str(part.sequence_number),
        "name": part.name or str(part.sequence_number),
        "symbolIdStr": part.symbol_id,
        "exclude_from_bom": to_bool_str(part.exclude_from_bom),
        "exclude_from_board": to_bool_str(part.exclude_from_board),
        "exclude_from_sim": to_bool_str(part.exclude_from_sim),
        "fields": fields,                              # all strings inside
    }

@router.get("/")
async def index():
    """API Root - KiCad only validates keys here."""
    return {"categories": "", "parts": ""}  # values unused by KiCad

# --- 1) Categories: array of {id, name} ---
@router.get("/categories.json")
async def list_categories(session: AsyncSession = Depends(get_session)):
    """List all active categories. Return the id and display name."""
    result = await session.exec(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.display_name)
    )
    rows = result.all()
    return [{"id": str(r.id), "name": r.display_name} for r in rows]

@router.get("/parts/category/{cid}.json")
async def parts_for_category(cid: str, session: AsyncSession = Depends(get_session)):
    """List all active parts in a given category ID. Return id, name, description."""
    parts = await session.exec(
        select(Part.sequence_number, Part.name, Part.description)
        .where(Part.category_id == int(cid))
        .order_by(Part.name)
    )
    return [
        {"id": str(r[0]), "name": r[1] or r[0], "description": r[2] or ""} for r in parts
    ]


# --- 3) Part details: one object with symbolIdStr + fields map ---
@router.get("/parts/{pid}.json")
async def part_detail(pid: str, session: AsyncSession = Depends(get_session)):
    """Get detailed info for a given part ID."""
    # Have a view that already joins your preferred MPN/SKU and strings everything
    res = await session.exec(select(Part).where(Part.sequence_number == int(pid)))
    row = res.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Unknown part")
    return part_to_kicad_fields(row)


# This must be done once all the endpoints are defined
app.include_router(router)
