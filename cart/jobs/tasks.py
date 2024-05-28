
from datetime import datetime, timedelta
from cart.models import CartItem, WishlistItem
from notifications.utils import send_cart_abandonment_email, send_wishlist_abandonment_email
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger



def mark_abandoned_items_and_send_reminders():
    two_weeks_ago = datetime.now() - timedelta(seconds=5)

    abandoned_cart_items = CartItem.objects.filter(created_at__lte=two_weeks_ago, abandoned=False)

    for cart_item in abandoned_cart_items:
        cart_item.abandoned = True
        cart_item.save()
        send_cart_abandonment_email(cart_item.user)

    abandoned_wishlist_items = WishlistItem.objects.filter(added_date__lte=two_weeks_ago)

    for wishlist_item in abandoned_wishlist_items:
        wishlist_item.delete()
        send_wishlist_abandonment_email(wishlist_item.user)



scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

scheduler.add_job(mark_abandoned_items_and_send_reminders, IntervalTrigger(seconds=5))


def start():
    scheduler.start()
