import time

from app.core.queue import Queue
from app.db.session import SessionLocal
from app.services.notification_service import NotificationService

def process_notification_job(job: dict):
    db = SessionLocal()

    try:
        service = NotificationService(db)

        notification = service.create_notification(
            user_id=job["user_id"],
            order_id=job["order_id"],
            notification_type=job["type"],
            message=job["message"],
        )

        db.commit()

        print(
            f"Notification created: "
            f"id={notification.id}, "
            f"user_id={notification.user_id}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

def run_worker():
    print("Notification worker started...")

    while True:
        job = Queue.dequeue()

        if job is None:
            time.sleep(1)
            continue

        try:
            process_notification_job(job)

        except Exception as exc:
            print(f"Failed to process job: {exc}")


if __name__ == "__main__":
    run_worker()