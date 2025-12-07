import json
import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    API для авторизации пользователей через Google/Яндекс OAuth
    Поддерживает регистрацию и вход через внешних провайдеров
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
    
    if method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        action = body_data.get('action')
        
        if action == 'oauth_callback':
            return handle_oauth_callback(body_data)
        elif action == 'verify_token':
            return verify_token(body_data)
        elif action == 'logout':
            return logout_user()
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }

def handle_oauth_callback(data: Dict[str, Any]) -> Dict[str, Any]:
    import psycopg2
    
    provider = data.get('provider')
    user_info = data.get('user_info')
    
    if not provider or not user_info:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Missing provider or user_info'}),
            'isBase64Encoded': False
        }
    
    dsn = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    
    try:
        email = user_info.get('email')
        name = user_info.get('name', 'User')
        avatar_url = user_info.get('avatar_url', '')
        provider_id = user_info.get('id', user_info.get('sub', ''))
        
        cursor.execute(
            "SELECT id, email, name, avatar_url, referral_code, referral_earnings, first_order_discount_used, created_at FROM users WHERE auth_provider_id = %s AND auth_provider = %s",
            (provider_id, provider)
        )
        user = cursor.fetchone()
        
        if user:
            user_id, user_email, user_name, user_avatar, ref_code, ref_earnings, discount_used, created_at = user
        else:
            referral_code = generate_referral_code()
            cursor.execute(
                "INSERT INTO users (email, name, avatar_url, auth_provider, auth_provider_id, referral_code) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, email, name, avatar_url, referral_code, referral_earnings, first_order_discount_used, created_at",
                (email, name, avatar_url, provider, provider_id, referral_code)
            )
            user = cursor.fetchone()
            user_id, user_email, user_name, user_avatar, ref_code, ref_earnings, discount_used, created_at = user
            conn.commit()
        
        jwt_secret = os.environ.get('JWT_SECRET', 'default_secret_key_change_me')
        token = jwt.encode({
            'user_id': user_id,
            'email': user_email,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, jwt_secret, algorithm='HS256')
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'token': token,
                'user': {
                    'id': user_id,
                    'email': user_email,
                    'name': user_name,
                    'avatar_url': user_avatar,
                    'referral_code': ref_code,
                    'referral_earnings': float(ref_earnings) if ref_earnings else 0,
                    'first_order_discount_used': discount_used,
                    'created_at': created_at.isoformat() if created_at else None
                }
            }),
            'isBase64Encoded': False
        }
    finally:
        cursor.close()
        conn.close()

def verify_token(data: Dict[str, Any]) -> Dict[str, Any]:
    import psycopg2
    
    token = data.get('token')
    if not token:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'No token provided'}),
            'isBase64Encoded': False
        }
    
    try:
        jwt_secret = os.environ.get('JWT_SECRET', 'default_secret_key_change_me')
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        user_id = payload['user_id']
        
        dsn = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(dsn)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, email, name, avatar_url, referral_code, referral_earnings, first_order_discount_used, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'User not found'}),
                'isBase64Encoded': False
            }
        
        user_id, email, name, avatar_url, ref_code, ref_earnings, discount_used, created_at = user
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'valid': True,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'avatar_url': avatar_url,
                    'referral_code': ref_code,
                    'referral_earnings': float(ref_earnings) if ref_earnings else 0,
                    'first_order_discount_used': discount_used,
                    'created_at': created_at.isoformat() if created_at else None
                }
            }),
            'isBase64Encoded': False
        }
    except jwt.ExpiredSignatureError:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Token expired'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid token'}),
            'isBase64Encoded': False
        }

def logout_user() -> Dict[str, Any]:
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'success': True, 'message': 'Logged out successfully'}),
        'isBase64Encoded': False
    }

def generate_referral_code() -> str:
    return 'ROCKET' + secrets.token_hex(4).upper()
