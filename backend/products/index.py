import json
import os
import psycopg2
from typing import Dict, Any, List

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    API для управления товарами магазина
    Получение каталога, поиск, фильтрация товаров
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
    
    if method == 'GET':
        return get_products(event)
    elif method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        action = body_data.get('action')
        
        if action == 'init_catalog':
            return init_catalog()
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }

def get_products(event: Dict[str, Any]) -> Dict[str, Any]:
    dsn = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    
    try:
        params = event.get('queryStringParameters') or {}
        category = params.get('category')
        search = params.get('search')
        
        query = "SELECT id, name, category, price, description, image_url, is_active FROM products WHERE is_active = TRUE"
        query_params = []
        
        if category:
            query += " AND category = %s"
            query_params.append(category)
        
        if search:
            query += " AND name ILIKE %s"
            query_params.append(f'%{search}%')
        
        query += " ORDER BY category, name"
        
        cursor.execute(query, query_params)
        products = cursor.fetchall()
        
        result = []
        for p in products:
            result.append({
                'id': p[0],
                'name': p[1],
                'category': p[2],
                'price': float(p[3]),
                'description': p[4],
                'image_url': p[5],
                'is_active': p[6]
            })
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'products': result}),
            'isBase64Encoded': False
        }
    finally:
        cursor.close()
        conn.close()

def init_catalog() -> Dict[str, Any]:
    dsn = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()
    
    products_data = [
        ('Пополнение Steam (любая сумма)', 'steam', 0, 'Пополнение баланса Steam аккаунта на любую сумму (RUB, USD, KZT)', '🎮'),
        
        ('100 Робуксов (гейм пасс)', 'robux_gamepass', 120, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        ('200 Робуксов (гейм пасс)', 'robux_gamepass', 200, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        ('300 Робуксов (гейм пасс)', 'robux_gamepass', 270, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        ('400 Робуксов (гейм пасс)', 'robux_gamepass', 340, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        ('500 Робуксов (гейм пасс)', 'robux_gamepass', 440, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        ('600 Робуксов (гейм пасс)', 'robux_gamepass', 520, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        ('700 Робуксов (гейм пасс)', 'robux_gamepass', 600, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        ('800 Робуксов (гейм пасс)', 'robux_gamepass', 650, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        ('900 Робуксов (гейм пасс)', 'robux_gamepass', 740, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        ('1000 Робуксов (гейм пасс)', 'robux_gamepass', 820, 'Робуксы через гейм пасс - ожидание 5 дней', '🎮'),
        
        ('100 Робуксов (моментально)', 'robux_instant', 160, 'Робукс паки - моментальная доставка', '⚡'),
        ('200 Робуксов (моментально)', 'robux_instant', 400, 'Робукс паки - моментальная доставка', '⚡'),
        ('400 Робуксов (моментально)', 'robux_instant', 600, 'Робукс паки - моментальная доставка', '⚡'),
        ('800 Робуксов (моментально)', 'robux_instant', 1000, 'Робукс паки - моментальная доставка', '⚡'),
        
        ('Brawl Pass (Особая скидка)', 'brawl_stars', 360, 'Brawl Stars - Brawl Pass с особой скидкой', '⭐'),
        ('Brawl Pass (Обычный)', 'brawl_stars', 640, 'Brawl Stars - Обычный Brawl Pass', '⭐'),
        ('Brawl Pass (Plus)', 'brawl_stars', 1000, 'Brawl Stars - Brawl Pass Plus', '⭐'),
        ('Улучшение Brawl Pass', 'brawl_stars', 440, 'Улучшение Brawl Pass с обычного на Plus', '⭐'),
        ('Pro Pass', 'brawl_stars', 2500, 'Brawl Stars Pro Pass', '⭐'),
        ('Обращение в поддержку РФ', 'brawl_stars', 50, 'Способ обращения в поддержку Brawl Stars в РФ', '⭐'),
        
        ('Apple/iTunes 500₽ (RU)', 'apple_gift', 660, 'Подарочная карта Apple Store и iTunes, регион Россия', '🍎'),
        ('Apple/iTunes 1000₽ (RU)', 'apple_gift', 1350, 'Подарочная карта Apple Store и iTunes, регион Россия', '🍎'),
        ('Apple/iTunes 1500₽ (RU)', 'apple_gift', 2000, 'Подарочная карта Apple Store и iTunes, регион Россия', '🍎'),
        ('Apple/iTunes 2000₽ (RU)', 'apple_gift', 2600, 'Подарочная карта Apple Store и iTunes, регион Россия', '🍎'),
        ('Apple/iTunes 2$ (USA)', 'apple_gift', 230, 'Подарочная карта Apple Store и iTunes, регион США', '🍎'),
        ('Apple/iTunes 3$ (USA)', 'apple_gift', 330, 'Подарочная карта Apple Store и iTunes, регион США', '🍎'),
        ('Apple/iTunes 4$ (USA)', 'apple_gift', 440, 'Подарочная карта Apple Store и iTunes, регион США', '🍎'),
        ('Apple/iTunes 6$ (USA)', 'apple_gift', 650, 'Подарочная карта Apple Store и iTunes, регион США', '🍎'),
        
        ('Spotify Premium 1 месяц', 'spotify', 250, 'Подписка Spotify Premium Individual (оформление 10:00-18:00 МСК)', '🎵'),
        ('Spotify Premium 3 месяца', 'spotify', 750, 'Подписка Spotify Premium Individual (оформление 10:00-18:00 МСК)', '🎵'),
        ('Spotify Premium 6 месяцев', 'spotify', 1300, 'Подписка Spotify Premium Individual (оформление 10:00-18:00 МСК)', '🎵'),
        ('Spotify Premium 12 месяцев', 'spotify', 2150, 'Подписка Spotify Premium Individual (оформление 10:00-18:00 МСК)', '🎵'),
        
        ('PUBG Mobile 60 UC', 'pubg', 100, 'Игровая валюта PUBG Mobile', '🎮'),
        ('PUBG Mobile 300+25 UC', 'pubg', 430, 'Игровая валюта PUBG Mobile с бонусом', '🎮'),
        ('PUBG Mobile 600+60 UC', 'pubg', 850, 'Игровая валюта PUBG Mobile с бонусом', '🎮'),
        ('PUBG Mobile 985 UC', 'pubg', 1240, 'Игровая валюта PUBG Mobile', '🎮'),
        ('PUBG Prime 1 месяц', 'pubg', 140, 'Подписка PUBG Mobile Prime', '🎮'),
        ('PUBG Prime 3 месяца', 'pubg', 340, 'Подписка PUBG Mobile Prime', '🎮'),
        ('PUBG Prime 6 месяцев', 'pubg', 640, 'Подписка PUBG Mobile Prime', '🎮'),
        
        ('Black Russia BC', 'black_russia', 0, 'BC любое количество на ваш аккаунт. Акция X2 в выходные!', '🎮'),
        
        ('Standoff 2 - 100 Gold', 'standoff', 130, 'Игровая валюта Standoff 2', '🔫'),
        ('Standoff 2 - 500 Gold', 'standoff', 550, 'Игровая валюта Standoff 2', '🔫'),
        ('Standoff 2 - 1000 Gold', 'standoff', 1000, 'Игровая валюта Standoff 2', '🔫'),
        ('Standoff 2 - 3000 Gold', 'standoff', 2200, 'Игровая валюта Standoff 2', '🔫'),
        ('Standoff 2 - Gold Pass', 'standoff', 900, 'Gold Pass для Standoff 2', '🔫'),
        ('Standoff 2 - Gold Pass +10 lvl', 'standoff', 1400, 'Gold Pass +10 уровней для Standoff 2', '🔫'),
        
        ('Valorant 240 VP (RU)', 'valorant', 300, 'Валюта Valorant Points, регион Россия', '⚔️'),
        ('Valorant 475 VP (RU)', 'valorant', 470, 'Валюта Valorant Points, регион Россия', '⚔️'),
        ('Valorant 1000 VP (RU)', 'valorant', 900, 'Валюта Valorant Points, регион Россия', '⚔️'),
        ('Valorant 2050 VP (RU)', 'valorant', 1950, 'Валюта Valorant Points, регион Россия', '⚔️'),
        ('Valorant 130 VP (TR)', 'valorant', 270, 'Валюта Valorant Points, регион Турция', '⚔️'),
        ('Valorant 475 VP (TR)', 'valorant', 300, 'Валюта Valorant Points, регион Турция', '⚔️'),
        ('Valorant 1000 VP (TR)', 'valorant', 640, 'Валюта Valorant Points, регион Турция', '⚔️'),
        ('Valorant 2050 VP (TR)', 'valorant', 1200, 'Валюта Valorant Points, регион Турция', '⚔️'),
        
        ('Telegram 50 звезд', 'telegram', 100, 'Звезды Telegram', '⭐'),
        ('Telegram 75 звезд', 'telegram', 140, 'Звезды Telegram', '⭐'),
        ('Telegram 100 звезд', 'telegram', 180, 'Звезды Telegram', '⭐'),
        ('Telegram 150 звезд', 'telegram', 270, 'Звезды Telegram', '⭐'),
        ('Telegram 250 звезд', 'telegram', 420, 'Звезды Telegram', '⭐'),
        ('Telegram 350 звезд', 'telegram', 580, 'Звезды Telegram', '⭐'),
        ('Telegram 500 звезд', 'telegram', 830, 'Звезды Telegram', '⭐'),
        ('Telegram 750 звезд', 'telegram', 1260, 'Звезды Telegram', '⭐'),
        ('Telegram 1000 звезд', 'telegram', 1640, 'Звезды Telegram', '⭐'),
        ('Telegram Premium 1 месяц', 'telegram', 310, 'Подписка Telegram Premium', '✨'),
        ('Telegram Premium 3 месяца', 'telegram', 1100, 'Подписка Telegram Premium', '✨'),
        ('Telegram Premium 6 месяцев', 'telegram', 1440, 'Подписка Telegram Premium', '✨'),
        ('Telegram Premium 12 месяцев', 'telegram', 2570, 'Подписка Telegram Premium', '✨'),
        
        ('GTA V Premium Online Edition', 'games', 1200, 'Grand Theft Auto V Premium Online Edition (Rockstar), Регион: Россия', '🎮'),
        ('Metro Exodus Gold Edition', 'games', 650, 'Metro Exodus Gold Edition (Steam)', '🎮'),
        ('Red Dead Redemption 2', 'games', 1100, 'Red Dead Redemption 2 (Steam)', '🎮'),
        ('Assassins Creed Valhalla', 'games', 580, 'Assassins Creed Valhalla', '🎮'),
        ('Assassins Creed Odyssey', 'games', 450, 'Assassins Creed Odyssey', '🎮'),
        ('BioShock Remastered', 'games', 200, 'BioShock Remastered', '🎮'),
        ('Hollow Knight Silksong', 'games', 800, 'Hollow Knight: Silksong', '🎮'),
    ]
    
    try:
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        
        if count == 0:
            for product in products_data:
                cursor.execute(
                    "INSERT INTO products (name, category, price, description, image_url, is_active) VALUES (%s, %s, %s, %s, %s, TRUE)",
                    product
                )
            conn.commit()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': f'Initialized {len(products_data)} products'}),
                'isBase64Encoded': False
            }
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Catalog already initialized'}),
                'isBase64Encoded': False
            }
    finally:
        cursor.close()
        conn.close()
