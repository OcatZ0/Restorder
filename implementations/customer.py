from mysql.connector import Error
from connection import get_db_connection
from datetime import datetime

def get_menu_items():
    """Fetch all menu items from database"""
    connection = get_db_connection()
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nama, deskripsi, harga, foto FROM menu ORDER BY id")
        menu_items = cursor.fetchall()
        return menu_items
    except Error as e:
        print(f"Error fetching menu items: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_menu_item_by_id(menu_id):
    """Fetch single menu item by id"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nama, deskripsi, harga, foto FROM menu WHERE id = %s", (menu_id,))
        menu_item = cursor.fetchone()
        return menu_item
    except Error as e:
        print(f"Error fetching menu item: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def create_order(note, items):
    """Create a new order with details"""
    connection = get_db_connection()
    if connection is None:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Calculate total
        total = sum(item['subtotal'] for item in items)
        
        # Insert into order table
        cursor.execute(
            "INSERT INTO `order` (total, note, waktu_order, waktu_selesai) VALUES (%s, %s, %s, NULL)",
            (total, note, datetime.now())
        )
        order_id = cursor.lastrowid
        
        # Insert into detail_order table
        for item in items:
            cursor.execute(
                "INSERT INTO detail_order (order_id, menu_id, jumlah, subtotal) VALUES (%s, %s, %s, %s)",
                (order_id, item['menu_id'], item['jumlah'], item['subtotal'])
            )
        
        connection.commit()
        return True, order_id
    except Error as e:
        connection.rollback()
        print(f"Error creating order: {e}")
        return False, str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_order_details(order_id):
    """Fetch order with all details"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get order info
        cursor.execute(
            "SELECT id, total, note, waktu_order, waktu_selesai FROM `order` WHERE id = %s",
            (order_id,)
        )
        order = cursor.fetchone()
        
        if order:
            # Get order details with menu info
            cursor.execute("""
                SELECT d.id, d.menu_id, d.jumlah, d.subtotal, 
                       m.nama, m.harga, m.foto
                FROM detail_order d
                JOIN menu m ON d.menu_id = m.id
                WHERE d.order_id = %s
            """, (order_id,))
            order['order_items'] = cursor.fetchall()
            
            # Ensure order_items is a list, not None
            if order['order_items'] is None:
                order['order_items'] = []
        
        return order
    except Error as e:
        print(f"Error fetching order details: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()