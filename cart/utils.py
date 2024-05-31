def add_to_session_cart(request, product_id, quantity):
    session_cart = request.session.get('cart', [])
    for item in session_cart:
        if item['product_id'] == product_id:
            item['quantity'] += int(quantity)
            request.session['cart'] = session_cart
            return item
    
    cart_item = {
        'product_id': product_id,
        'quantity': int(quantity)
    }
    session_cart.append(cart_item)
    request.session['cart'] = session_cart
    return cart_item
