import aiosqlite

DB_NAME = 'quiz_bot.db'

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, score INTEGER)''')
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            return results[0] if results is not None else 0
        
async def get_quiz_score(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            return results[0] if results is not None else -1

async def update_quiz_status(user_id, index, score):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, ?)', (user_id, index, score))
        await db.commit()

async def get_stats(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, score FROM quiz_state ORDER BY score DESC LIMIT ?', (limit,)) as cursor:
            results = await cursor.fetchall()
            return results