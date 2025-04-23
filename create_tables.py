from sqlalchemy import create_engine
from kicad_parts_database.kicad_db import Base
from kicad_parts_database.schema.database import *

def create_tables():
    engine = create_engine("postgresql+psycopg2://kicad-user:QAiaw8do7NHa4PvDakdR@eplant-eng.info:5432/kicad_part_database")
    Base.metadata.create_all(engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()