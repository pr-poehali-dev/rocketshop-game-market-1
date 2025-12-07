import json
import os
import psycopg2
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    API для управления корзиной покупок
    Добавление, удаление товаров, получение содержимого корзины
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
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
        return get_cart(user_id)
    elif method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        return add_to_cart(user_id, body_data)
    elif method == 'DELETE':
        body_data = json.loads(event.get('body', '{}'))
        return remove_from_cart(user_id, body_data)
    
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

def get_cart(user_id: int) -> Dict[str, Any]:
    dsn = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT c.id, c.product_id, c.quantity, p.name, p.price, p.image_url
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (user_id,))
        
        items = cursor.fetchall()
        cart_items = []
        total = 0
        
        for item in items:
            item_total = float(item[4]) * item[2]
            total += item_total
            cart_items.append({
                'id': item[0],
                'product_id': item[1],
                'quantity': item[2],
                'name': item[3],
                'price': float(item[4]),
                'image_url': item[5],
                'total': item_total
            })
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'items': cart_items,
                'total': total,
                'count': len(cart_items)
            }),
            'isBase64Encoded': False
        }
    finally:
        cursor.close()
        conn.close()

def add_to_cart(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'product_id required'}),
            'isBase64Encoded': False
        }
    
    dsn = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(
                "UPDATE cart SET quantity = quantity + %s WHERE user_id = %s AND product_id = %s",
                (quantity, user_id, product_id)
            )
        else:
            cursor.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (user_id, product_id, quantity)
            )
        
        conn.commit()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': True, 'message': 'Added to cart'}),
            'isBase64Encoded': False
        }
    finally:
        cursor.close()
        conn.close()

def remove_from_cart(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    cart_item_id = data.get('cart_item_id')
    
    if not cart_item_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'cart_item_id required'}),
            'isBase64Encoded': False
        }
    
    dsn = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM cart WHERE id = %s AND user_id = %s", (cart_item_id, user_id))
        conn.commit()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': True, 'message': 'Removed from cart'}),
            'isBase64Encoded': False
        }
    finally:
        cursor.close()
        conn.close()
