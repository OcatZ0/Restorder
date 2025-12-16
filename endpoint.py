import implementations.customer as cs
import implementations.employee as em
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from functools import wraps

endpoint = Blueprint('endpoint', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('endpoint.login'))
        return f(*args, **kwargs)
    return decorated_function

@endpoint.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    
    # GET request - Show login page
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST request - Process login
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Validate input
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username dan password harus diisi'
            }), 400
        
        # Authenticate user
        isLoginSuccess = em.auth(username, password)
        
        if isLoginSuccess:
            # Store user session
            session['username'] = username
            session['logged_in'] = True
            
            return jsonify({
                'success': True,
                'message': 'Login berhasil',
                'redirect': '/orders'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Username atau password salah'
            }), 401

@endpoint.route('/')
def index():
    """Main page route - display menu"""
    menu_items = cs.get_menu_items()
    
    # Initialize cart in session if not exists
    if 'cart' not in session:
        session['cart'] = []
    
    return render_template('index.html', menu_items=menu_items, cart=session['cart'])

@endpoint.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    data = request.get_json()
    menu_id = data.get('menu_id')
    quantity = data.get('quantity', 1)
    
    # Get menu item details
    menu_item = cs.get_menu_item_by_id(menu_id)
    if not menu_item:
        return jsonify({'success': False, 'message': 'Menu item not found'}), 404
    
    # Initialize cart if not exists
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    
    # Check if item already in cart
    found = False
    for item in cart:
        if item['menu_id'] == menu_id:
            item['jumlah'] += quantity
            item['subtotal'] = item['jumlah'] * item['harga']
            found = True
            break
    
    # Add new item if not found
    if not found:
        cart.append({
            'menu_id': menu_id,
            'nama': menu_item['nama'],
            'harga': float(menu_item['harga']),
            'jumlah': quantity,
            'subtotal': float(menu_item['harga']) * quantity,
            'foto': menu_item['foto']
        })
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'cart_count': len(cart)})

@endpoint.route('/update-cart', methods=['POST'])
def update_cart():
    """Update cart item quantity"""
    data = request.get_json()
    menu_id = data.get('menu_id')
    quantity = data.get('quantity', 1)
    
    if 'cart' not in session:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400
    
    cart = session['cart']
    
    for item in cart:
        if item['menu_id'] == menu_id:
            if quantity <= 0:
                cart.remove(item)
            else:
                item['jumlah'] = quantity
                item['subtotal'] = item['jumlah'] * item['harga']
            break
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'cart_count': len(cart)})

@endpoint.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    data = request.get_json()
    menu_id = data.get('menu_id')
    
    if 'cart' not in session:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400
    
    cart = session['cart']
    cart = [item for item in cart if item['menu_id'] != menu_id]
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'cart_count': len(cart)})

@endpoint.route('/checkout', methods=['POST'])
def checkout():
    """Process checkout and create order"""
    data = request.get_json()
    note = data.get('note', '')
    
    if 'cart' not in session or len(session['cart']) == 0:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400
    
    # Create order
    success, result = cs.create_order(note, session['cart'])
    
    if success:
        order_id = result
        # Clear cart
        session['cart'] = []
        session.modified = True
        
        return jsonify({
            'success': True, 
            'message': 'Order placed successfully!',
            'order_id': order_id
        })
    else:
        return jsonify({
            'success': False, 
            'message': f'Failed to create order: {result}'
        }), 500

@endpoint.route('/order/<int:order_id>')
def view_order(order_id):
    """View order details"""
    order = cs.get_order_details(order_id)
    
    if not order:
        return "Pesanan tidak ditemukan", 404
    
    return render_template('order_detail.html', order=order)

@endpoint.route('/get-cart')
def get_cart():
    """Get current cart"""
    cart = session.get('cart', [])
    total = sum(item['subtotal'] for item in cart)
    
    return jsonify({
        'cart': cart,
        'total': total,
        'count': len(cart)
    })

@endpoint.route('/orders')
@login_required
def order_list():
    """View all orders (for employees)"""
    orders = em.get_all_orders()
    return render_template('order_list.html', orders=orders)

@endpoint.route('/complete-order/<int:order_id>', methods=['POST'])
@login_required
def complete_order(order_id):
    """Mark order as completed"""
    success, message = em.complete_order(order_id)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 500