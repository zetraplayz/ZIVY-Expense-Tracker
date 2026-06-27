import os
import pytest
from src.models.database import Database

@pytest.fixture
def test_db():
    db = Database("test_expense_tracker.db")
    yield db
    # Teardown
    if os.path.exists(db.db_path):
        os.remove(db.db_path)

def test_initialization(test_db):
    assert os.path.exists(test_db.db_path)

def test_add_transaction(test_db):
    t_id = test_db.add_transaction(150.0, "Groceries", "Expense", "2026-06-25", "Walmart")
    assert t_id is not None
    assert t_id > 0

    txs = test_db.get_transactions()
    assert len(txs) == 1
    assert txs[0]['amount'] == 150.0
    assert txs[0]['category'] == "Groceries"
    assert txs[0]['type'] == "Expense"

def test_edit_transaction(test_db):
    t_id = test_db.add_transaction(50.0, "Transport", "Expense", "2026-06-25")
    
    success = test_db.edit_transaction(t_id, 75.0, "Transport", "Expense", "2026-06-26", "Uber")
    assert success is True
    
    txs = test_db.get_transactions()
    assert txs[0]['amount'] == 75.0
    assert txs[0]['timestamp'] == "2026-06-26"
    assert txs[0]['note'] == "Uber"

def test_delete_transaction(test_db):
    t_id = test_db.add_transaction(10.0, "Food", "Expense", "2026-06-25")
    assert len(test_db.get_transactions()) == 1
    
    success = test_db.delete_transaction(t_id)
    assert success is True
    assert len(test_db.get_transactions()) == 0

def test_summary_analytics(test_db):
    test_db.add_transaction(2000.0, "Salary", "Income", "2026-06-01")
    test_db.add_transaction(500.0, "Rent", "Expense", "2026-06-02")
    test_db.add_transaction(100.0, "Utilities", "Expense", "2026-06-03")
    
    summary = test_db.get_summary_analytics()
    assert summary['total_income'] == 2000.0
    assert summary['total_expense'] == 600.0
    assert summary['balance'] == 1400.0

def test_category_analytics(test_db):
    test_db.add_transaction(50.0, "Food", "Expense", "2026-06-01")
    test_db.add_transaction(20.0, "Food", "Expense", "2026-06-02")
    test_db.add_transaction(100.0, "Transport", "Expense", "2026-06-03")
    
    categories = test_db.get_expenses_by_category()
    assert categories["Food"] == 70.0
    assert categories["Transport"] == 100.0

def test_daily_trends(test_db):
    test_db.add_transaction(100.0, "Food", "Expense", "2026-06-01")
    test_db.add_transaction(200.0, "Salary", "Income", "2026-06-01")
    test_db.add_transaction(50.0, "Transport", "Expense", "2026-06-02")
    
    trends = test_db.get_daily_trends()
    assert "2026-06-01" in trends
    assert trends["2026-06-01"]["expense"] == 100.0
    assert trends["2026-06-01"]["income"] == 200.0
    assert trends["2026-06-02"]["expense"] == 50.0
    assert trends["2026-06-02"]["income"] == 0.0
