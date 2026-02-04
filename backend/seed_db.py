"""
Seed script for database.
"""
import asyncio
from sqlalchemy import text

async def seed_database():
    from app.db.session import async_session_maker
    
    async with async_session_maker() as session:
        # Seed categories
        await session.execute(text("""
            INSERT IGNORE INTO categories (slug, title, description) VALUES
            ('protein-bars', 'Protein Bars', 'High protein snack bars'),
            ('breakfast-cereals', 'Breakfast Cereals', 'Cereals and breakfast foods')
        """))
        
        # Seed sugar aliases
        sugar_aliases = [
            'glucose syrup', 'maltodextrin', 'dextrose', 'fructose', 'sucrose',
            'invert sugar', 'corn syrup', 'high fructose corn syrup', 'hfcs',
            'jaggery', 'honey', 'agave', 'maple syrup', 'molasses', 'brown sugar',
            'cane sugar', 'coconut sugar', 'date syrup', 'rice syrup', 'barley malt'
        ]
        
        for alias in sugar_aliases:
            await session.execute(text(f"""
                INSERT IGNORE INTO rules (category_id, rule_type, `key`, value, is_active)
                VALUES (NULL, 'sugar_alias', :key, :value, 1)
            """), {"key": alias, "value": f'{{"alias": "{alias}", "is_sugar": true}}'})
        
        await session.commit()
        print("Database seeded successfully!")
        
        # Verify
        result = await session.execute(text("SELECT COUNT(*) FROM categories"))
        cat_count = result.scalar()
        
        result = await session.execute(text("SELECT COUNT(*) FROM rules"))
        rule_count = result.scalar()
        
        print(f"Categories: {cat_count}")
        print(f"Rules: {rule_count}")

if __name__ == "__main__":
    asyncio.run(seed_database())
