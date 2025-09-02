import asyncio
from sqlmodel import select
from src.db import init_db, get_session
from src.definitions.parts import Category, Part

async def seed():
    await init_db(install_triggers=True)
    async for session in get_session():
        cat = (await session.exec(select(Category).limit(1))).first()
        if not cat:
            cat = Category(display_name="Capacitors (0805)")
            session.add(cat); 
            await session.commit(); 
            await session.refresh(cat)

        part = (await session.exec(select(Part).limit(1))).first()
        if not part:
            p = Part(
                name="10uF_X5R_16V-00001",
                category_id=cat.id,
                value="10uF",
                footprint="Capacitor_SMD:C_0805_2012Metric",
                symbol_id="Device:C",
                description="10uF 16V X5R 0805",
                datasheet="https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BR61C106KE15-01.pdf",
                fields={
                    "Manufacturer": "Murata",
                    "MPN": "GRM21BR61C106KE15L",
                    "LCSC": "C15850",
                    "Voltage": {"value": "16V", "visible": True},
                    "Dielectric": {"value": "X5R", "visible": True},
                    "Tolerance": "±10%",
                    "ESR": {"value": "—", "visible": False},
                },
            )
            session.add(p); await session.commit()

async def main():
    await seed()

if __name__ == "__main__":
    asyncio.run(main())

