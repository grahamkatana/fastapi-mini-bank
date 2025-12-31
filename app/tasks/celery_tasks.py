from app.tasks.celery_app import celery_app
import time


@celery_app.task
def process_large_transaction(transaction_id: int, amount: str):
    """
    Sample long-running task to process large transactions
    In a real application, this might involve fraud detection,
    compliance checks, or notifications.
    """
    print(f"Processing large transaction {transaction_id} of amount {amount}")
    
    # Simulate long-running operation
    time.sleep(5)
    
    # Here you might:
    # - Send notifications
    # - Run fraud detection algorithms
    # - Generate reports
    # - Update external systems
    
    print(f"Transaction {transaction_id} processed successfully")
    return {"status": "completed", "transaction_id": transaction_id}


@celery_app.task
def send_monthly_report(user_id: int):
    """
    Sample task to generate and send monthly reports
    """
    print(f"Generating monthly report for user {user_id}")
    
    # Simulate report generation
    time.sleep(10)
    
    print(f"Monthly report sent to user {user_id}")
    return {"status": "completed", "user_id": user_id}


@celery_app.task
def cleanup_old_data():
    """
    Sample task for data cleanup operations
    """
    print("Starting data cleanup...")
    
    # Simulate cleanup operation
    time.sleep(15)
    
    print("Data cleanup completed")
    return {"status": "completed", "records_cleaned": 100}
