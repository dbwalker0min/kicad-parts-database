from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    display_name: str = Field(description="human-friendly name, e.g. 'Resistors (Thick Film)'")
    description: Optional[str] = Field(default=None, description="longer text description")
    is_active: bool = Field(default=True, nullable=False, description="soft delete flag")

    # NOTE: only back_populates; no positional target
    parts: list["Part"] = Relationship(back_populates="category")


class Part(SQLModel, table=True):
    __tablename__ = "parts"
    # (keep your other __table_args__ as needed)

    sequence_number: Optional[int] = Field(default=None, primary_key=True)
    name: str

    category_id: int = Field(foreign_key="categories.id", index=True)

    # The other side of the relationship
    category: Category = Relationship(back_populates="parts")

    value: str = Field(description="e.g. '10k', '1uF', 'NPN', 'LM317'")
    reference: str = Field(default="R?", description="e.g. 'R?', 'C?', 'U?'")
    footprint: str = Field(description="e.g. 'Resistor_SMD:R_0805_2012Metric'")
    symbol_id: str = Field(description="e.g. 'Device:R'")
    description: Optional[str] = Field(default=None, description="longer text description")
    datasheet: Optional[str] = Field(default=None, description="URL to datasheet")
    keywords: Optional[str] = Field(default="", index=True, description="search keywords, space separated")

    fields: Dict[str, str | dict] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, server_default=text("'{}'::jsonb")),
        description="additional custom fields as JSONB",
    )

    exclude_from_bom: bool = Field(default=False, nullable=False, description="exclude from BOM exports")
    exclude_from_board: bool = Field(default=False, nullable=False, description="exclude from board layout exports")
    exclude_from_sim: bool = Field(default=False, nullable=False, description="exclude from simulation exports")

    is_active: bool = Field(default=True, nullable=False, description="soft delete flag")

    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    )
