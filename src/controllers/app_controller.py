from src.models.database import Database

class AppController:
    def __init__(self):
        self.db = Database()

    def get_summary(self):
        return self.db.get_summary_analytics()

    def add_transaction(self, amount, category, t_type, timestamp, note):
        return self.db.add_transaction(float(amount), category, t_type, timestamp, note)
    
    def edit_transaction(self, t_id, amount, category, t_type, timestamp, note):
        return self.db.edit_transaction(t_id, float(amount), category, t_type, timestamp, note)
    
    def delete_transaction(self, t_id):
        return self.db.delete_transaction(t_id)

    def bulk_delete_transactions(self, t_ids):
        return self.db.bulk_delete_transactions(t_ids)

    def delete_all_transactions(self):
        return self.db.delete_all_transactions()

    def get_recent_transactions(self, limit=10):
        return self.db.get_transactions(limit=limit)
    
    def get_all_transactions(self):
        return self.db.get_transactions()
        
    def get_category_data(self):
        return self.db.get_expenses_by_category()
        
    def get_trend_data(self, period="daily"):
        if period == "monthly":
            return self.db.get_monthly_trends()
        return self.db.get_daily_trends()
