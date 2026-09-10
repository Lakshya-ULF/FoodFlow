from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.restaurant import Restaurant
from app.models.main_menu import MenuItem


MENU_DATA = {
    "FoodFlow Kitchen": [
        {
            "name": "Chicken Biryani",
            "description": "Aromatic basmati rice with spiced chicken and traditional biryani masala.",
            "price": Decimal("280.00"),
        },
        {
            "name": "Butter Chicken",
            "description": "Tender chicken cooked in a rich, creamy tomato and butter gravy.",
            "price": Decimal("320.00"),
        },
        {
            "name": "Paneer Tikka",
            "description": "Grilled Indian cottage cheese marinated with spices and yogurt.",
            "price": Decimal("260.00"),
        },
        {
            "name": "Garlic Naan",
            "description": "Soft tandoor-baked naan topped with garlic and butter.",
            "price": Decimal("80.00"),
        },
        {
            "name": "Mango Lassi",
            "description": "Refreshing yogurt-based drink blended with ripe mango.",
            "price": Decimal("120.00"),
        },
    ],

    "Spice Route": [
        {
            "name": "Hyderabadi Chicken Biryani",
            "description": "Fragrant basmati rice layered with spiced chicken and saffron.",
            "price": Decimal("300.00"),
        },
        {
            "name": "Paneer Butter Masala",
            "description": "Paneer cooked in a mildly spiced tomato and butter gravy.",
            "price": Decimal("250.00"),
        },
        {
            "name": "Masala Dosa",
            "description": "Crispy South Indian dosa filled with spiced potato masala.",
            "price": Decimal("140.00"),
        },
        {
            "name": "Chicken Tikka",
            "description": "Char-grilled chicken pieces marinated in yogurt and Indian spices.",
            "price": Decimal("280.00"),
        },
        {
            "name": "Gulab Jamun",
            "description": "Soft milk-solid dumplings served in warm sugar syrup.",
            "price": Decimal("100.00"),
        },
    ],

    "Urban Bites": [
        {
            "name": "Classic Cheeseburger",
            "description": "Juicy chicken patty with cheese, lettuce, tomato and house sauce.",
            "price": Decimal("220.00"),
        },
        {
            "name": "Peri Peri Chicken Wrap",
            "description": "Grilled chicken, vegetables and peri peri sauce wrapped in a soft tortilla.",
            "price": Decimal("240.00"),
        },
        {
            "name": "Loaded Fries",
            "description": "Crispy fries topped with cheese, herbs and house seasoning.",
            "price": Decimal("160.00"),
        },
        {
            "name": "Margherita Pizza",
            "description": "Classic pizza with tomato sauce, mozzarella and basil.",
            "price": Decimal("280.00"),
        },
        {
            "name": "Cold Coffee",
            "description": "Chilled creamy coffee served over ice.",
            "price": Decimal("130.00"),
        },
    ],
}


def get_restaurant(db, name: str):
    return db.scalar(
        select(Restaurant).where(Restaurant.name == name)
    )


def seed_menu():
    db = SessionLocal()

    try:
        inserted = 0
        skipped = 0

        for restaurant_name, menu_items in MENU_DATA.items():

            restaurant = get_restaurant(db, restaurant_name)

            if restaurant is None:
                print(
                    f"WARNING: Restaurant '{restaurant_name}' not found. "
                    "Skipping."
                )
                continue

            print(f"\nSeeding menu for: {restaurant_name}")

            for item_data in menu_items:

                existing_item = db.scalar(
                    select(MenuItem).where(
                        MenuItem.restaurant_id == restaurant.id,
                        MenuItem.name == item_data["name"],
                    )
                )

                if existing_item:
                    skipped += 1
                    print(f"  SKIP: {item_data['name']}")
                    continue

                menu_item = MenuItem(
                    restaurant_id=restaurant.id,
                    name=item_data["name"],
                    description=item_data["description"],
                    price=item_data["price"],
                    is_available=True,
                )

                db.add(menu_item)
                inserted += 1

                print(f"  ADD:  {item_data['name']}")

        db.commit()

        print("\n" + "=" * 50)
        print("MENU SEED COMPLETED")
        print("=" * 50)
        print(f"Inserted: {inserted}")
        print(f"Skipped:  {skipped}")
        print(f"Total:    {inserted + skipped}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_menu()