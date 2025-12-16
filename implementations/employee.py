from mysql.connector import Error
from connection import get_db_connection
from datetime import datetime

def auth(username, password):
    """Authenticate employee"""
    connection = get_db_connection()
    if connection is None:
        return False

    try:
        cursor = connection.cursor(dictionary=True)
        sql = """
            SELECT id, username, password
            FROM user
            WHERE username = %s
            LIMIT 1
        """
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        if not user:
            return False

        # Compare hashed password
        if user['password'] == password:
            return True   # success
        else:
            return False

    except Error as e:
        print(f"Error authentication: {e}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_all_orders():
    """Fetch all orders with basic info"""
    connection = get_db_connection()
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.id, o.total, o.note, o.waktu_order, o.waktu_selesai,
                   COUNT(d.id) as item_count
            FROM `order` o
            LEFT JOIN detail_order d ON o.id = d.order_id
            GROUP BY o.id
            ORDER BY o.waktu_order DESC
        """)
        orders = cursor.fetchall()
        return orders
    except Error as e:
        print(f"Error fetching orders: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def complete_order(order_id):
    """Mark order as completed"""
    connection = get_db_connection()
    if connection is None:
        return False, 'Database connection failed'
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE `order` SET waktu_selesai = %s WHERE id = %s",
            (datetime.now(), order_id)
        )
        connection.commit()
        return True, 'Pesanan telah diselesaikan'
    except Error as e:
        connection.rollback()
        print(f"Error completing order: {e}")
        return False, f'Failed to complete order: {str(e)}'
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()