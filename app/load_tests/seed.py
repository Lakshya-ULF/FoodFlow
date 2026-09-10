from pwdlib import PasswordHash
from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.delivery_partner import DeliveryPartner
from app.core.constants import UserRole


password_hash = PasswordHash.recommended()


USERS = [
    {
        "email": "owner1@foodflow.com",
        "password": "Owner123!",
        "role": UserRole.RESTAURANT_OWNER,
    },
    {
        "email": "owner2@foodflow.com",
        "password": "Owner123!",
        "role": UserRole.RESTAURANT_OWNER,
    },
    {
        "email": "owner3@foodflow.com",
        "password": "Owner123!",
        "role": UserRole.RESTAURANT_OWNER,
    },
    {
        "email": "delivery1@foodflow.com",
        "password": "Delivery123!",
        "role": UserRole.DELIVERY_PARTNER,
    },
    {
        "email": "delivery2@foodflow.com",
        "password": "Delivery123!",
        "role": UserRole.DELIVERY_PARTNER,
    },
    {
        "email": "delivery3@foodflow.com",
        "password": "Delivery123!",
        "role": UserRole.DELIVERY_PARTNER,
    },
    {
        "email": "customer1@foodflow.com",
        "password": "Customer123!",
        "role": UserRole.CUSTOMER,
    },
    {
        "email": "customer2@foodflow.com",
        "password": "Customer123!",
        "role": UserRole.CUSTOMER,
    },
]


def get_or_create_user(db, email, password, role):
    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user:
        return user

    user = User(
        email=email,
        password_hash=password_hash.hash(password),
        role=role,
    )

    db.add(user)
    db.flush()

    return user


def get_or_create_restaurant(db, name, address, owner_id):
    restaurant = db.scalar(
        select(Restaurant).where(Restaurant.name == name)
    )

    if restaurant:
        return restaurant

    restaurant = Restaurant(
        name=name,
        address=address,
        owner_id=owner_id,
        is_active=True,
    )

    db.add(restaurant)
    db.flush()

    return restaurant


def get_or_create_delivery_partner(db, user_id):
    partner = db.scalar(
        select(DeliveryPartner).where(
            DeliveryPartner.user_id == user_id
        )
    )

    if partner:
        return partner

    partner = DeliveryPartner(
        user_id=user_id,
        is_online=True,
    )

    db.add(partner)
    db.flush()

    return partner


def seed():
    db = SessionLocal()

    try:
        # -------------------------
        # Users
        # -------------------------

        users = {}

        for data in USERS:
            users[data["email"]] = get_or_create_user(
                db,
                data["email"],
                data["password"],
                data["role"],
            )

        # -------------------------
        # Real test restaurants
        # -------------------------

        restaurants = [
            (
                "FoodFlow Kitchen",
                "MG Road, Bangalore",
                users["owner1@foodflow.com"].id,
            ),
            (
                "Spice Route",
                "Koramangala, Bangalore",
                users["owner2@foodflow.com"].id,
            ),
            (
                "Urban Bites",
                "Indiranagar, Bangalore",
                users["owner3@foodflow.com"].id,
            ),
        ]

        for name, address, owner_id in restaurants:
            get_or_create_restaurant(
                db,
                name,
                address,
                owner_id,
            )

        # -------------------------
        # Delivery partners
        # -------------------------

        for email in [
            "delivery1@foodflow.com",
            "delivery2@foodflow.com",
            "delivery3@foodflow.com",
        ]:
            get_or_create_delivery_partner(
                db,
                users[email].id,
            )

        # -------------------------
        # 1000 benchmark restaurants
        # -------------------------

        benchmark_owner_id = users["owner1@foodflow.com"].id

        existing_count = db.scalar(
            select(func.count())
            .select_from(Restaurant)
            .where(
                Restaurant.name.like("Benchmark Restaurant %")
            )
        )

        if existing_count < 1000:
            start = existing_count

            benchmark_restaurants = [
                Restaurant(
                    name=f"Benchmark Restaurant {i}",
                    address=f"Benchmark Address {i}",
                    owner_id=benchmark_owner_id,
                    is_active=True,
                )
                for i in range(start, 1000)
            ]

            db.add_all(benchmark_restaurants)

            print(
                f"Inserted {len(benchmark_restaurants)} "
                "benchmark restaurants."
            )
        else:
            print("1000 benchmark restaurants already exist.")

        db.commit()

        print("\nSeed completed successfully.")
        print("Users: 8")
        print("Restaurant owners: 3")
        print("Delivery partners: 3")
        print("Customers: 2")
        print("Test restaurants: 3")
        print("Benchmark restaurants: 1000")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()