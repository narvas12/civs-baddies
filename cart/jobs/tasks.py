# tasks.py

from datetime import datetime, timedelta
from cart.models import CartItem, WishlistItem
from notifications.utils import send_cart_abandonment_email, send_wishlist_abandonment_email
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger



def mark_abandoned_items_and_send_reminders():
    # Get the date two weeks ago
    two_weeks_ago = datetime.now() - timedelta(seconds=5)

    # Get abandoned cart items
    abandoned_cart_items = CartItem.objects.filter(created_at__lte=two_weeks_ago, abandoned=False)

    # Mark abandoned cart items and send reminders
    for cart_item in abandoned_cart_items:
        cart_item.abandoned = True
        cart_item.save()
        send_cart_abandonment_email(cart_item.user)

    # Get abandoned wishlist items
    abandoned_wishlist_items = WishlistItem.objects.filter(added_date__lte=two_weeks_ago)

    # Mark abandoned wishlist items and send reminders
    for wishlist_item in abandoned_wishlist_items:
        wishlist_item.delete()
        send_wishlist_abandonment_email(wishlist_item.user)



# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

# Schedule the task to run daily
scheduler.add_job(mark_abandoned_items_and_send_reminders, IntervalTrigger(seconds=5))

# Start the scheduler

def start():
    scheduler.start()
