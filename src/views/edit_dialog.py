from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDateTimeEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import QDateTime
from src.views.theme import PREMIUM_DARK_THEME

EXPENSE_CATEGORIES = [
    "Food Expense", "Healthcare", "Travel & Transportation",
    "Loans & EMI", "Entertainment", "Utilities & Bills & Shopping",
    "Family and Education Expenses", "Housing & Rent", "Subscriptions", "Other"
]

INCOME_CATEGORIES = [
    "Salary", "Freelance", "Investments", "Gifts", "Other"
]


class EditTransactionDialog(QDialog):
    def __init__(self, t_id, timestamp, category, t_type, amount, note, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Transaction")
        self.setMinimumWidth(420)
        self.setStyleSheet(PREMIUM_DARK_THEME)

        self.t_id = t_id
        self.initial_timestamp = timestamp
        self.initial_category = category
        self.initial_type = t_type
        self.initial_amount = amount
        self.initial_note = note or ""

        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Edit Transaction")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #FFFFFF; background: transparent;")
        layout.addWidget(title)

        # Type
        layout.addWidget(self._make_label("Type"))
        self.input_type = QComboBox()
        self.input_type.addItems(["Expense", "Income"])
        self.input_type.currentTextChanged.connect(self._update_categories)
        layout.addWidget(self.input_type)

        # Category
        layout.addWidget(self._make_label("Category"))
        self.input_category = QComboBox()
        layout.addWidget(self.input_category)

        # Date & Time
        layout.addWidget(self._make_label("Date & Time"))
        self.input_datetime = QDateTimeEdit()
        self.input_datetime.setCalendarPopup(True)
        self.input_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        layout.addWidget(self.input_datetime)

        # Amount
        layout.addWidget(self._make_label("Amount"))
        self.input_amount = QLineEdit()
        self.input_amount.setPlaceholderText("0.00")
        layout.addWidget(self.input_amount)

        # Note
        layout.addWidget(self._make_label("Note (optional)"))
        self.input_note = QLineEdit()
        self.input_note.setPlaceholderText("Add a note...")
        layout.addWidget(self.input_note)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save Changes")
        btn_save.setProperty("actionrole", "primary")
        btn_save.clicked.connect(self._validate_and_accept)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def _make_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #8E929C; font-size: 12px; font-weight: 600; background: transparent;")
        return lbl

    def _update_categories(self, t_type):
        self.input_category.clear()
        if t_type == "Expense":
            self.input_category.addItems(EXPENSE_CATEGORIES)
        else:
            self.input_category.addItems(INCOME_CATEGORIES)

    def _populate_data(self):
        # Set type first so category dropdown populates correctly
        self.input_type.setCurrentText(self.initial_type)
        self._update_categories(self.initial_type)
        self.input_category.setCurrentText(self.initial_category)

        # Parse the stored timestamp; fall back to now if invalid
        dt = QDateTime.fromString(self.initial_timestamp, "yyyy-MM-dd HH:mm")
        if not dt.isValid():
            dt = QDateTime.fromString(self.initial_timestamp, "yyyy-MM-dd")
        self.input_datetime.setDateTime(dt if dt.isValid() else QDateTime.currentDateTime())

        self.input_amount.setText(f"{self.initial_amount:.2f}")
        self.input_note.setText(self.initial_note)

    def _validate_and_accept(self):
        raw = self.input_amount.text().strip()
        try:
            amount = float(raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid positive amount.")
            return
        self.accept()

    def get_data(self):
        try:
            return {
                "amount": float(self.input_amount.text().strip()),
                "category": self.input_category.currentText(),
                "type": self.input_type.currentText(),
                "timestamp": self.input_datetime.dateTime().toString("yyyy-MM-dd HH:mm"),
                "note": self.input_note.text().strip()
            }
        except ValueError:
            return None
