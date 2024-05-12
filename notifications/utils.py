from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail


def send_order_confirmation_email(user, order_instance, products, order_number, total):
    # Define email subject
    subject = 'Order Confirmation'

    # Render email template with necessary data
    email_content = render_to_string('order_confirmation_email.html', {
        'user': user,
        'order_instance': order_instance,
        'products': products,
        'order_number': order_number,
        'total': total
    })

    # Send email with HTML content
    send_mail(subject, None, 'your@example.com', [user.email], html_message=email_content)




def send_cart_abandonment_email(user, cart_items):

    subject = "Reminder: You have abandoned items in your cart"
    html_message = render_to_string('cart_abandonment_email.html', {'cart_items': cart_items})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, None, [user.email], html_message=html_message)

def send_wishlist_abandonment_email(user):

    subject = "Reminder: You have abandoned items in your wishlist"
    html_message = render_to_string('wishlist_abandonment_email.html')
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, None, [user.email], html_message=html_message)