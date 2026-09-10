from app.db.session import SessionLocal
from app.models.restaurant import Restaurant


def seed():
    db = SessionLocal()

    try:
        restaurants = [
            Restaurant(
                name=f"Benchmark Restaurant {i}",
                address=f"Benchmark Address {i}",
                owner_id=1,
                is_active=True,
            )
            for i in range(1000)
        ]

        db.add_all(restaurants)
        db.commit()

        print("Inserted 1000 benchmark restaurants.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()