import json
import os
import psycopg2
from typing import Dict, Any
from datetime import datetime

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    API для создания и управления заказами
    Оформление заказа, получение истории, статус оплаты
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Auth-Token',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    headers = event.get('headers', {})
    user_token = headers.get('X-Auth-Token') or headers.get('x-auth-token')
    
    if not user_token:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Authentication required'}),
            'isBase64Encoded': False
        }
    
    user_id = verify_user_token(user_token)
    if not user_id:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid token'}),
            'isBase64Encoded': False
        }
    
    if method == 'GET':
        return get_orders(user_id)
    elif method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        action = body_data.get('action')
        
        if action == 'create':
            return create_order(user_id, body_data)
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }

def verify_user_token(token: str) -> int:
    import jwt
    try:
        jwt_secret = os.environ.get('JWT_SECRET', 'default_secret_key_change_me')
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        return payload.get('user_id')
    except:
        return None

def get_orders(user_id: int) -> Dict[str, Any]:
    dsn = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, total_amount, discount_amount, final_amount, payment_method, payment_status, status, created_at
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        orders = cursor.fetchall()
        result = []
        
        for order in orders:
            order_id = order[0]
            
            cursor.execute("""
                SELECT product_name, product_price, quantity, total_price
                FROM order_items
                WHERE order_id = %s
            """, (order_id,))
            
            items = cursor.fetchall()
            order_items = []
            for item in items:
                order_items.append({
                    'product_name': item[0],
                    'product_price': float(item[1]),
                    'quantity': item[2],
                    'total_price': float(item[3])
                })
            
            result.append({
                'id': order_id,
                'total_amount': float(order[1]),
                'discount_amount': float(order[2]),
                'final_amount': float(order[3]),
                'payment_method': order[4],
                'payment_status': order[5],
                'status': order[6],
                'created_at': order[7].isoformat() if order[7] else None,
                'items': order_items
            })
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'orders': result}),
            'isBase64Encoded': False
        }
    finally:
        cursor.close()
        conn.close()

def create_order(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    payment_method = data.get('payment_method')
    use_discount = data.get('use_discount', False)
    
    if not payment_method:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'payment_method required'}),
            'isBase64Encoded': False
        }
    
    dsn = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT c.product_id, c.quantity, p.name, p.price
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (user_id,))
        
        cart_items = cursor.fetchall()
        
        if not cart_items:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Cart is empty'}),
                'isBase64Encoded': False
            }
        
        total_amount = sum(float(item[3]) * item[1] for item in cart_items)
        discount_amount = 0
        
        if use_discount:
            cursor.execute("SELECT first_order_discount_used FROM users WHERE id = %s", (user_id,))
            discount_used = cursor.fetchone()[0]
            
            if not discount_used:
                discount_amount = total_amount * 0.20
                cursor.execute("UPDATE users SET first_order_discount_used = TRUE WHERE id = %s", (user_id,))
        
        final_amount = total_amount - discount_amount
        
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount, discount_amount, final_amount, payment_method, payment_status, status)
            VALUES (%s, %s, %s, %s, %s, 'pending', 'pending')
            RETURNING id
        """, (user_id, total_amount, discount_amount, final_amount, payment_method))
        
        order_id = cursor.fetchone()[0]
        
        for item in cart_items:
            product_id, quantity, name, price = item
            item_total = float(price) * quantity
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, total_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (order_id, product_id, name, price, quantity, item_total))
        
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        
        conn.commit()
        
        payment_info = {}
        if payment_method == 'sberbank':
            payment_info = {
                'card_number': '2202 2083 9585 3485',
                'recipient': 'Никита Владимирович Т.',
                'bank': 'Сбербанк'
            }
        elif payment_method == 'sbp':
            payment_info = {
                'phone': '+7 (XXX) XXX-XX-XX',
                'recipient': 'Никита Владимирович Т.',
                'bank': 'СБП'
            }
        elif payment_method == 'tbank':
            payment_info = {
                'status': 'coming_soon',
                'message': 'Скоро'
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'success': True,
                'order_id': order_id,
                'final_amount': final_amount,
                'payment_info': payment_info,
                'message': 'Order created successfully'
            }),
            'isBase64Encoded': False
        }
    finally:
        cursor.close()
        conn.close()
