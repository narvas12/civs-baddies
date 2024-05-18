from django.db import models


class ProductManager(models.manager):
    def get_product_history(product):
        """
        Retrieves the history of a product, including associated orders, customers, and order details.

        Args:
            product (Product): The product instance for which to retrieve history.

        Returns:
            list: A list of dictionaries representing each purchase history entry.
            Each entry contains:
                - order_number (str): Order number associated with the purchase.
                - customer_name (str): Full name of the customer who bought the product.
                - date_ordered (datetime): Date and time the order was placed.
                - order_status (str): Current status of the order.
                - quantity (int): Quantity of the product purchased in the order.
        """

        history = []
        for order_item in product.orderitems.all():  # Loop through order items linked to the product
            order = order_item.order
            customer = order.buyer
            history.append({
                'order_number': order.order_number,
                'customer_name': f"{customer.first_name} {customer.last_name}",  # Assuming first and last name fields
                'date_ordered': order.created_at,
                'order_status': order.get_status_display(),  # Use get_status_display() for human-readable status
                'quantity': order_item.quantity,
            })
        return history