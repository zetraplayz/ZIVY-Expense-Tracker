PREMIUM_DARK_THEME = """
QMainWindow, QDialog {
    background-color: #0B0C10;
}

QWidget {
    background-color: #0B0C10;
    color: #C5C6C7;
    font-family: 'Segoe UI', Roboto, Arial, sans-serif;
    font-size: 14px;
}

/* ── Sidebar ────────────────────────────────── */
QFrame#sidebar {
    background-color: #111217;
    border-right: 1px solid #1F2129;
}

QFrame#sidebar QPushButton {
    background-color: transparent;
    color: #8E929C;
    border: none;
    padding: 12px 20px;
    text-align: left;
    font-size: 15px;
    font-weight: 600;
    border-radius: 8px;
    margin: 4px 12px;
}

QFrame#sidebar QPushButton:hover {
    background-color: #1A1C23;
    color: #FFFFFF;
}

QFrame#sidebar QPushButton:checked {
    background-color: #1A2235;
    color: #4DA8DA;
    border: 1px solid #23324C;
}

/* ── Dashboard Cards ────────────────────────── */
QFrame#DashboardCard {
    background-color: #111217;
    border-radius: 12px;
    border: 1px solid #1F2129;
}

/* ── Tables ─────────────────────────────────── */
QTableWidget {
    background-color: #111217;
    border-radius: 10px;
    border: 1px solid #1F2129;
    gridline-color: #1A1C23;
    font-size: 14px;
    outline: none;
    selection-background-color: #1A2235;
}

QTableWidget::item {
    padding: 10px 8px;
    border: none;
    color: #C5C6C7;
}

QTableWidget::item:selected {
    background-color: #1A2235;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #0B0C10;
    color: #8E929C;
    padding: 12px 8px;
    border: none;
    border-bottom: 1px solid #1F2129;
    font-weight: 600;
    font-size: 13px;
    text-align: left;
}

/* ── Form Inputs ────────────────────────────── */
QLineEdit, QDateTimeEdit {
    background-color: #111217;
    border: 1px solid #1F2129;
    border-radius: 6px;
    padding: 9px 12px;
    color: #FFFFFF;
    font-size: 14px;
    selection-background-color: #1A2235;
}

QLineEdit:focus, QDateTimeEdit:focus {
    border: 1px solid #4DA8DA;
    background-color: #131620;
}

QComboBox {
    background-color: #111217;
    border: 1px solid #1F2129;
    border-radius: 6px;
    padding: 9px 12px;
    color: #FFFFFF;
    font-size: 14px;
}

QComboBox:focus {
    border: 1px solid #4DA8DA;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #1A1C23;
    border: 1px solid #1F2129;
    border-radius: 6px;
    color: #FFFFFF;
    selection-background-color: #1A2235;
    outline: none;
}

/* Calendar Widget styling */
QCalendarWidget {
    background-color: #111217;
    color: #FFFFFF;
    border: 1px solid #1F2129;
    border-radius: 8px;
}

QCalendarWidget QAbstractItemView {
    background-color: #111217;
    color: #FFFFFF;
    selection-background-color: #1A2235;
    selection-color: #4DA8DA;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #0B0C10;
    border-bottom: 1px solid #1F2129;
}

QCalendarWidget QPushButton {
    background-color: transparent;
    color: #8E929C;
    border: none;
    padding: 4px 8px;
}

QCalendarWidget QPushButton:hover {
    color: #FFFFFF;
}

QCalendarWidget QToolButton {
    background-color: transparent;
    color: #C5C6C7;
    border: none;
    font-size: 14px;
    font-weight: 600;
    padding: 4px 8px;
}

QCalendarWidget QToolButton:hover {
    color: #4DA8DA;
}

QDateTimeEdit::up-button, QDateTimeEdit::down-button {
    background-color: #1F2129;
    border: none;
    width: 16px;
}

/* ── Scrollbars ─────────────────────────────── */
QScrollBar:vertical {
    border: none;
    background: #0B0C10;
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #2D303C;
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #4DA8DA;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0;
}

/* ── Buttons ────────────────────────────────── */
QPushButton[actionrole="primary"] {
    background-color: #4DA8DA;
    color: #0B0C10;
    border: none;
    border-radius: 6px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 14px;
}

QPushButton[actionrole="primary"]:hover {
    background-color: #66B5E0;
}

QPushButton[actionrole="primary"]:pressed {
    background-color: #3A8FBF;
}

QPushButton[actionrole="danger"] {
    background-color: transparent;
    color: #F46C75;
    border: 1px solid #F46C75;
    border-radius: 6px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 14px;
}

QPushButton[actionrole="danger"]:hover {
    background-color: #F46C75;
    color: #0B0C10;
}

/* ── Message Boxes ──────────────────────────── */
QMessageBox {
    background-color: #111217;
    color: #FFFFFF;
}
"""
