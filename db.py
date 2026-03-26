import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import pytz

MOSCOW_TZ = pytz.timezone('Europe/Moscow')

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found")
    
    conn = psycopg2.connect(database_url, sslmode='require')
    return conn

def init_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            avatar_url TEXT,
            email VARCHAR(255) UNIQUE,
            auth_type VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP WITH TIME ZONE,
            days_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            is_banned BOOLEAN DEFAULT FALSE,
            is_vip BOOLEAN DEFAULT FALSE
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            chat_id VARCHAR(255),
            role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            key VARCHAR(255) NOT NULL,
            value TEXT NOT NULL,
            category VARCHAR(50) DEFAULT 'general',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, key)
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS money (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            balance DECIMAL(10, 2) DEFAULT 0.00,
            total_deposited DECIMAL(10, 2) DEFAULT 0.00,
            total_spent DECIMAL(10, 2) DEFAULT 0.00,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            amount DECIMAL(10, 2) NOT NULL,
            type VARCHAR(50) NOT NULL,
            description TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS telegram_codes (
            id SERIAL PRIMARY KEY,
            code VARCHAR(6) NOT NULL,
            unique_link VARCHAR(255) NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def create_user_telegram(telegram_id, username, first_name, last_name, avatar_url):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    moscow_now = datetime.now(MOSCOW_TZ)
    
    cur.execute("""
        INSERT INTO users (telegram_id, username, first_name, last_name, avatar_url, auth_type, last_login)
        VALUES (%s, %s, %s, %s, %s, 'telegram', %s)
        ON CONFLICT (telegram_id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            avatar_url = EXCLUDED.avatar_url,
            last_login = EXCLUDED.last_login
        RETURNING *
    """, (telegram_id, username, first_name, last_name, avatar_url, moscow_now))
    
    user = cur.fetchone()
    
    cur.execute("""
        INSERT INTO money (user_id, balance)
        VALUES (%s, 0.00)
        ON CONFLICT (user_id) DO NOTHING
    """, (user['id'],))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return dict(user)

def get_user_by_telegram_id(telegram_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    return dict(user) if user else None

def update_user_days_count(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("UPDATE users SET days_count = days_count + 1 WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def save_message(user_id, chat_id, role, content):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO messages (user_id, chat_id, role, content)
        VALUES (%s, %s, %s, %s)
    """, (user_id, chat_id, role, content))
    
    conn.commit()
    cur.close()
    conn.close()

def get_chat_history(user_id, chat_id, limit=50):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT * FROM messages 
        WHERE user_id = %s AND chat_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (user_id, chat_id, limit))
    
    messages = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(m) for m in messages]

def save_fact(user_id, key, value, category='general'):
    conn = get_db_connection()
    cur = conn.cursor()
    
    moscow_now = datetime.now(MOSCOW_TZ)
    
    cur.execute("""
        INSERT INTO facts (user_id, key, value, category, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id, key) DO UPDATE SET
            value = EXCLUDED.value,
            category = EXCLUDED.category,
            updated_at = EXCLUDED.updated_at
    """, (user_id, key, value, category, moscow_now))
    
    conn.commit()
    cur.close()
    conn.close()

def get_facts(user_id, category=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if category:
        cur.execute("""
            SELECT * FROM facts 
            WHERE user_id = %s AND category = %s
            ORDER BY updated_at DESC
        """, (user_id, category))
    else:
        cur.execute("""
            SELECT * FROM facts 
            WHERE user_id = %s
            ORDER BY updated_at DESC
        """, (user_id,))
    
    facts = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(f) for f in facts]

def get_balance(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM money WHERE user_id = %s", (user_id,))
    balance = cur.fetchone()
    cur.close()
    conn.close()
    
    return dict(balance) if balance else None

def create_telegram_code(code, unique_link):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO telegram_codes (code, unique_link)
        VALUES (%s, %s)
        RETURNING id
    """, (code, unique_link))
    
    code_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return code_id

def verify_telegram_code(code, unique_link):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT * FROM telegram_codes 
        WHERE code = %s AND unique_link = %s AND used = FALSE
    """, (code, unique_link))
    
    result = cur.fetchone()
    
    if result:
        cur.execute("UPDATE telegram_codes SET used = TRUE WHERE id = %s", (result['id'],))
        conn.commit()
    
    cur.close()
    conn.close()
    
    return dict(result) if result else None

def get_user_stats(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT COUNT(*) as message_count FROM messages WHERE user_id = %s", (user_id,))
    message_count = cur.fetchone()['message_count']
    
    cur.execute("SELECT COUNT(*) as fact_count FROM facts WHERE user_id = %s", (user_id,))
    fact_count = cur.fetchone()['fact_count']
    
    cur.execute("SELECT days_count FROM users WHERE id = %s", (user_id,))
    days_count = cur.fetchone()['days_count']
    
    cur.close()
    conn.close()
    
    return {
        'message_count': message_count,
        'fact_count': fact_count,
        'days_count': days_count
    }

if __name__ == '__main__':
    init_database()
    print("Database initialized!")
