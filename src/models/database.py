import sqlite3
import os
from contextlib import closing

class Database:
    def __init__(self, db_name="transactions.db"):
        from pathlib import Path
        app_dir = os.path.join(str(Path.home()), ".zivy_expense_tracker")
        if not os.path.exists(app_dir):
            os.makedirs(app_dir, exist_ok=True)
            
        self.db_path = os.path.join(app_dir, db_name)
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        note TEXT
                    )
                ''')

    def add_transaction(self, amount: float, category: str, t_type: str, timestamp: str, note: str = "") -> int:
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO transactions (amount, category, type, timestamp, note)
                    VALUES (?, ?, ?, ?, ?)
                ''', (amount, category, t_type, timestamp, note))
                return cursor.lastrowid

    def edit_transaction(self, t_id: int, amount: float, category: str, t_type: str, timestamp: str, note: str = "") -> bool:
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE transactions 
                    SET amount = ?, category = ?, type = ?, timestamp = ?, note = ?
                    WHERE id = ?
                ''', (amount, category, t_type, timestamp, note, t_id))
                return cursor.rowcount > 0

    def delete_transaction(self, t_id: int) -> bool:
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM transactions WHERE id = ?', (t_id,))
                return cursor.rowcount > 0

    def bulk_delete_transactions(self, t_ids: list) -> bool:
        if not t_ids:
            return False
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.cursor()
                placeholders = ','.join(['?'] * len(t_ids))
                cursor.execute(f'DELETE FROM transactions WHERE id IN ({placeholders})', t_ids)
                return cursor.rowcount > 0

    def delete_all_transactions(self) -> bool:
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM transactions')
                return True

    def get_transactions(self, limit=None) -> list:
        with closing(self._get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = 'SELECT * FROM transactions ORDER BY timestamp DESC, id DESC'
            if limit:
                query += f' LIMIT {limit}'
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_summary_analytics(self) -> dict:
        with closing(self._get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT type, SUM(amount) as total 
                FROM transactions 
                GROUP BY type
            ''')
            results = cursor.fetchall()
            
            income = 0.0
            expense = 0.0
            for row in results:
                if row[0].lower() == 'income':
                    income = row[1]
                elif row[0].lower() == 'expense':
                    expense = row[1]
                    
            return {
                'total_income': income,
                'total_expense': expense,
                'balance': income - expense
            }

    def get_expenses_by_category(self) -> dict:
        with closing(self._get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, SUM(amount) as total 
                FROM transactions 
                WHERE LOWER(type) = 'expense'
                GROUP BY category
            ''')
            return {row[0]: row[1] for row in cursor.fetchall()}

    def get_daily_trends(self) -> dict:
        """For line chart (Returns dict of date -> {income: amount, expense: amount})."""
        with closing(self._get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Extract just the YYYY-MM-DD part of the timestamp (first 10 chars)
            cursor.execute('''
                SELECT substr(timestamp, 1, 10) as date_only, type, SUM(amount) as total
                FROM transactions
                GROUP BY date_only, type
                ORDER BY date_only ASC
            ''')
            
            trends = {}
            for row in cursor.fetchall():
                date_str = row['date_only']
                t_type = row['type'].lower()
                amount = row['total']
                
                if date_str not in trends:
                    trends[date_str] = {'income': 0.0, 'expense': 0.0}
                
                trends[date_str][t_type] = amount
                
            return trends

    def get_monthly_trends(self) -> dict:
        """For line chart (Returns dict of YYYY-MM -> {income: amount, expense: amount})."""
        with closing(self._get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Extract YYYY-MM (first 7 chars)
            cursor.execute('''
                SELECT substr(timestamp, 1, 7) as month_only, type, SUM(amount) as total
                FROM transactions
                GROUP BY month_only, type
                ORDER BY month_only ASC
            ''')
            
            trends = {}
            for row in cursor.fetchall():
                month_str = row['month_only']
                t_type = row['type'].lower()
                amount = row['total']
                
                if month_str not in trends:
                    trends[month_str] = {'income': 0.0, 'expense': 0.0}
                
                trends[month_str][t_type] = amount
                
            return trends
