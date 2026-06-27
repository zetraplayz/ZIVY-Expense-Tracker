import sys
import os
import csv
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QMessageBox, QDateTimeEdit, QGridLayout,
    QGraphicsObject, QGraphicsView, QGraphicsScene, QAbstractItemView,
    QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt, QDateTime, QRectF, QSize
from PyQt6.QtGui import QFont, QPainter, QBrush, QPen, QColor, QPixmap, QIcon
import pyqtgraph as pg

from src.controllers.app_controller import AppController
from src.views.theme import PREMIUM_DARK_THEME
from src.views.edit_dialog import EditTransactionDialog, EXPENSE_CATEGORIES, INCOME_CATEGORIES

# Configure pyqtgraph globally to prevent it from inheriting theme font sizes
pg.setConfigOption("foreground", "#8E929C")
pg.setConfigOption("background", "#111217")


def _make_axis_style():
    """Return a font style dict for pyqtgraph axes that avoids the QFont -1 warning."""
    return {"color": "#8E929C", "font-size": "11pt"}


class PieChartItem(QGraphicsObject):
    def __init__(self, data_dict):
        super().__init__()
        self.data = data_dict
        self.colors = [
            QColor("#45D18F"), QColor("#4DA8DA"), QColor("#F46C75"),
            QColor("#F9C851"), QColor("#9854CB"), QColor("#FF8A65"),
            QColor("#26C6DA"), QColor("#FF7043"), QColor("#A5D6A7"),
            QColor("#80DEEA"),
        ]

    def boundingRect(self):
        return QRectF(-180, -180, 580, 400)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        total = sum(self.data.values())
        if total == 0:
            return

        start_angle = 0
        items = [(k, v) for k, v in self.data.items() if v > 0]

        for i, (label, val) in enumerate(items):
            span_angle = (val / total) * 360 * 16
            color = self.colors[i % len(self.colors)]

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#0B0C10"), 3))
            painter.drawPie(QRectF(-155, -150, 290, 290), int(start_angle), int(span_angle))
            start_angle += span_angle

        # Draw legend separately — 2 columns, right of chart
        legend_font = QFont("Segoe UI", 8)
        legend_font.setPixelSize(13)
        painter.setFont(legend_font)

        for i, (label, val) in enumerate(items):
            color = self.colors[i % len(self.colors)]
            col = i % 2
            row_idx = i // 2
            lx = 155 + col * 160
            ly = -150 + row_idx * 30

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(lx, ly, 12, 12, 3, 3)

            painter.setPen(QPen(QColor("#C5C6C7")))
            pct = (val / total) * 100
            short_lbl = (label[:13] + "…") if len(label) > 15 else label
            painter.drawText(lx + 18, ly + 11, f"{short_lbl} ({pct:.1f}%)")


class DashboardCard(QFrame):
    def __init__(self, title, value_obj_name, color):
        super().__init__()
        self.setObjectName("DashboardCard")
        self.setMinimumHeight(110)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        title_label = QLabel(title.upper())
        title_label.setStyleSheet(
            "color: #8E929C; font-size: 11px; font-weight: 600; "
            "letter-spacing: 1.5px; background: transparent;"
        )

        self.value_label = QLabel("$0.00")
        self.value_label.setObjectName(value_obj_name)
        self.value_label.setStyleSheet(
            f"color: {color}; font-size: 30px; font-weight: 700; background: transparent;"
        )

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = AppController()

        self.setWindowTitle("ZIVY Expense Tracker")
        self.setMinimumSize(1150, 760)
        self.setStyleSheet(PREMIUM_DARK_THEME)

        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        self._setup_ui(logo_path)
        self._refresh_data()

    def _setup_ui(self, logo_path):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 24, 0, 24)
        sidebar_layout.setSpacing(4)

        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaled(
                140, 140,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setContentsMargins(0, 0, 0, 20)
            sidebar_layout.addWidget(logo_label)
        else:
            fallback = QLabel("ZIVY")
            fallback.setStyleSheet(
                "font-size: 26px; font-weight: 800; color: #4DA8DA; padding: 20px; background: transparent;"
            )
            fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sidebar_layout.addWidget(fallback)

        icon_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons")
        self.btn_dashboard = QPushButton("  Dashboard")
        self.btn_dashboard.setIcon(QIcon(os.path.join(icon_dir, "dashboard.svg")))
        self.btn_dashboard.setCheckable(True)
        self.btn_dashboard.setChecked(True)

        self.btn_transactions = QPushButton("  Transactions")
        self.btn_transactions.setIcon(QIcon(os.path.join(icon_dir, "transactions.svg")))
        self.btn_transactions.setCheckable(True)

        self.btn_analytics = QPushButton("  Analytics")
        self.btn_analytics.setIcon(QIcon(os.path.join(icon_dir, "analytics.svg")))
        self.btn_analytics.setCheckable(True)

        self.btn_dashboard.clicked.connect(lambda: self._switch_tab(0))
        self.btn_transactions.clicked.connect(lambda: self._switch_tab(1))
        self.btn_analytics.clicked.connect(lambda: self._switch_tab(2))

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_transactions)
        sidebar_layout.addWidget(self.btn_analytics)
        sidebar_layout.addStretch()

        # ── Main Content ─────────────────────────
        self.stacked_widget = QStackedWidget()
        self._setup_dashboard_tab()
        self._setup_transactions_tab()
        self._setup_analytics_tab()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)

    def _switch_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.btn_dashboard.setChecked(index == 0)
        self.btn_transactions.setChecked(index == 1)
        self.btn_analytics.setChecked(index == 2)
        self._refresh_data()

    # ─── Tab: Dashboard ──────────────────────────
    def _setup_dashboard_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(24)

        header = QLabel("Overview")
        header.setStyleSheet(
            "font-size: 26px; font-weight: 700; color: #FFFFFF; background: transparent;"
        )
        layout.addWidget(header)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(18)
        self.card_income = DashboardCard("Total Income", "IncomeValue", "#45D18F")
        self.card_expense = DashboardCard("Total Expense", "ExpenseValue", "#F46C75")
        self.card_balance = DashboardCard("Net Balance", "BalanceValue", "#4DA8DA")

        cards_layout.addWidget(self.card_income)
        cards_layout.addWidget(self.card_expense)
        cards_layout.addWidget(self.card_balance)
        layout.addLayout(cards_layout)

        recent_label = QLabel("Recent Transactions")
        recent_label.setStyleSheet(
            "font-size: 17px; font-weight: 600; color: #FFFFFF; "
            "background: transparent; margin-top: 10px;"
        )
        layout.addWidget(recent_label)

        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["Date & Time", "Category", "Type", "Amount"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.recent_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setAlternatingRowColors(False)
        layout.addWidget(self.recent_table)

        self.stacked_widget.addWidget(page)

    # ─── Tab: Transactions ───────────────────────
    def _setup_transactions_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(20)

        # Header row
        header_layout = QHBoxLayout()
        header = QLabel("Manage Transactions")
        header.setStyleSheet(
            "font-size: 26px; font-weight: 700; color: #FFFFFF; background: transparent;"
        )

        icon_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons")
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search transactions...")
        self.search_bar.addAction(QIcon(os.path.join(icon_dir, "search.svg")), QLineEdit.ActionPosition.LeadingPosition)
        self.search_bar.setFixedWidth(260)
        self.search_bar.textChanged.connect(self._filter_transactions)

        btn_export = QPushButton("Export CSV")
        btn_export.setProperty("actionrole", "primary")
        btn_export.clicked.connect(self._export_csv)

        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(btn_export)
        layout.addLayout(header_layout)

        # Add transaction form
        form_layout = QHBoxLayout()
        form_layout.setSpacing(10)

        self.input_datetime = QDateTimeEdit()
        self.input_datetime.setCalendarPopup(True)
        self.input_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.input_datetime.setDateTime(QDateTime.currentDateTime())
        self.input_datetime.setMinimumWidth(165)

        self.input_type = QComboBox()
        self.input_type.addItems(["Expense", "Income"])
        self.input_type.setFixedWidth(110)
        self.input_type.currentTextChanged.connect(self._update_form_categories)

        self.input_category = QComboBox()
        self.input_category.setMinimumWidth(200)
        self._update_form_categories("Expense")

        self.input_amount = QLineEdit()
        self.input_amount.setPlaceholderText("Amount (₹)")
        self.input_amount.setFixedWidth(120)

        self.input_note = QLineEdit()
        self.input_note.setPlaceholderText("Note (optional)")

        btn_add = QPushButton("+ Add")
        btn_add.setProperty("actionrole", "primary")
        btn_add.setFixedWidth(90)
        btn_add.clicked.connect(self._add_transaction)

        form_layout.addWidget(self.input_datetime)
        form_layout.addWidget(self.input_type)
        form_layout.addWidget(self.input_category)
        form_layout.addWidget(self.input_amount)
        form_layout.addWidget(self.input_note)
        form_layout.addWidget(btn_add)
        layout.addLayout(form_layout)

        # Transactions table (column 0 = hidden ID)
        self.all_table = QTableWidget()
        self.all_table.setColumnCount(6)
        self.all_table.setHorizontalHeaderLabels(
            ["ID", "Date & Time", "Category", "Type", "Amount", "Note"]
        )
        self.all_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.all_table.hideColumn(0)
        self.all_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.all_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.all_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.all_table.verticalHeader().setVisible(False)
        layout.addWidget(self.all_table)

        # Action buttons row
        action_layout = QHBoxLayout()

        btn_delete_all = QPushButton(" Delete All")
        btn_delete_all.setIcon(QIcon(os.path.join(icon_dir, "trash.svg")))
        btn_delete_all.setProperty("actionrole", "danger")
        btn_delete_all.clicked.connect(self._delete_all_transactions)

        action_layout.addWidget(btn_delete_all)
        action_layout.addStretch()

        btn_edit = QPushButton(" Edit Selected")
        btn_edit.setIcon(QIcon(os.path.join(icon_dir, "edit.svg")))
        btn_edit.setProperty("actionrole", "primary")
        btn_edit.clicked.connect(self._open_edit_dialog)

        btn_delete = QPushButton(" Delete Selected")
        btn_delete.setIcon(QIcon(os.path.join(icon_dir, "x.svg")))
        btn_delete.setProperty("actionrole", "danger")
        btn_delete.clicked.connect(self._delete_transaction)

        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        layout.addLayout(action_layout)

        self.stacked_widget.addWidget(page)

    def _update_form_categories(self, t_type):
        self.input_category.clear()
        if t_type == "Expense":
            self.input_category.addItems(EXPENSE_CATEGORIES)
        else:
            self.input_category.addItems(INCOME_CATEGORIES)

    # ─── Tab: Analytics ─────────────────────────
    def _setup_analytics_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(20)

        header = QLabel("Analytics & Insights")
        header.setStyleSheet(
            "font-size: 26px; font-weight: 700; color: #FFFFFF; background: transparent;"
        )
        layout.addWidget(header)

        self.chart_layout = QGridLayout()
        self.chart_layout.setSpacing(18)
        layout.addLayout(self.chart_layout)

        # ── Trend Line Chart ─────────────────────
        self.trend_plot = pg.PlotWidget()
        self.trend_plot.setBackground("#111217")
        self.trend_plot.showGrid(x=True, y=True, alpha=0.12)
        self.trend_plot.setMinimumHeight(220)

        # Use setLabel with explicit pt font to prevent -1 warning
        self.trend_plot.setLabel("bottom", "", **_make_axis_style())
        self.trend_plot.setLabel("left", "Amount (₹)", **_make_axis_style())
        self.trend_plot.getAxis("bottom").setPen(pg.mkPen("#8E929C", width=1))
        self.trend_plot.getAxis("left").setPen(pg.mkPen("#8E929C", width=1))

        trend_title_layout = QHBoxLayout()
        trend_title_layout.setContentsMargins(0, 0, 0, 0)

        trend_title = QLabel("SPENDING TREND")
        trend_title.setStyleSheet(
            "color: #8E929C; font-size: 11px; font-weight: 700; "
            "letter-spacing: 1.5px; background: transparent;"
        )

        self.trend_period_combo = QComboBox()
        self.trend_period_combo.addItems(["Daily", "Monthly"])
        self.trend_period_combo.setFixedWidth(110)
        self.trend_period_combo.currentTextChanged.connect(self._refresh_data)

        trend_title_layout.addWidget(trend_title)
        trend_title_layout.addStretch()
        trend_title_layout.addWidget(self.trend_period_combo)

        trend_header_widget = QWidget()
        trend_header_widget.setLayout(trend_title_layout)

        self.chart_layout.addWidget(trend_header_widget, 0, 0, 1, 2)
        self.chart_layout.addWidget(self.trend_plot, 1, 0, 1, 2)

        # ── Pie Chart ────────────────────────────
        self.pie_view = QGraphicsView()
        self.pie_view.setStyleSheet(
            "background-color: #111217; border: 1px solid #1F2129; border-radius: 10px;"
        )
        self.pie_scene = QGraphicsScene()
        self.pie_view.setScene(self.pie_scene)
        self.pie_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.pie_view.setMinimumHeight(260)

        pie_title = QLabel("EXPENSES BY CATEGORY")
        pie_title.setStyleSheet(
            "color: #8E929C; font-size: 11px; font-weight: 700; "
            "letter-spacing: 1.5px; background: transparent;"
        )
        self.chart_layout.addWidget(pie_title, 2, 0)
        self.chart_layout.addWidget(self.pie_view, 3, 0)

        # ── Income vs Expense Bar Chart ──────────
        self.bar_plot = pg.PlotWidget()
        self.bar_plot.setBackground("#111217")
        self.bar_plot.setMinimumHeight(260)
        self.bar_plot.setLabel("left", "Amount (₹)", **_make_axis_style())
        self.bar_plot.setLabel("bottom", "", **_make_axis_style())
        self.bar_plot.getAxis("bottom").setPen(pg.mkPen("#8E929C", width=1))
        self.bar_plot.getAxis("left").setPen(pg.mkPen("#8E929C", width=1))

        bar_title = QLabel("INCOME VS EXPENSES")
        bar_title.setStyleSheet(
            "color: #8E929C; font-size: 11px; font-weight: 700; "
            "letter-spacing: 1.5px; background: transparent;"
        )
        self.chart_layout.addWidget(bar_title, 2, 1)
        self.chart_layout.addWidget(self.bar_plot, 3, 1)

        self.stacked_widget.addWidget(page)

    # ─── Data Refresh ────────────────────────────
    def _refresh_data(self):
        summary = self.controller.get_summary()
        self.card_income.value_label.setText(f"₹{summary['total_income']:,.2f}")
        self.card_expense.value_label.setText(f"₹{summary['total_expense']:,.2f}")

        balance = summary["balance"]
        self.card_balance.value_label.setText(f"₹{balance:,.2f}")
        balance_color = "#4DA8DA" if balance >= 0 else "#F46C75"
        self.card_balance.value_label.setStyleSheet(
            f"color: {balance_color}; font-size: 30px; font-weight: 700; background: transparent;"
        )

        self._populate_table(self.recent_table, self.controller.get_recent_transactions(15))
        self._populate_table(
            self.all_table, self.controller.get_all_transactions(),
            show_id=True, show_note=True
        )
        self._refresh_charts(summary)

    def _refresh_charts(self, summary):
        # ── Pie Chart ────────────────────────────
        cat_data = self.controller.get_category_data()
        self.pie_scene.clear()
        if cat_data:
            pie = PieChartItem(cat_data)
            self.pie_scene.addItem(pie)
            self.pie_scene.setSceneRect(pie.boundingRect())
            self.pie_view.fitInView(pie.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

        # ── Trend Line Chart ─────────────────────
        period = self.trend_period_combo.currentText().lower()
        trend_data = self.controller.get_trend_data(period=period)
        self.trend_plot.clear()

        if trend_data:
            dates = list(trend_data.keys())
            expenses = [trend_data[d].get("expense", 0) for d in dates]
            incomes = [trend_data[d].get("income", 0) for d in dates]
            x_indices = list(range(len(dates)))

            x_axis = self.trend_plot.getAxis("bottom")
            x_axis.setTicks([[(i, d) for i, d in enumerate(dates)]])

            exp_pen = pg.mkPen("#F46C75", width=2)
            exp_brush = pg.mkBrush(244, 108, 117, 45)
            self.trend_plot.plot(
                x_indices, expenses, pen=exp_pen,
                fillLevel=0, fillBrush=exp_brush,
                symbol="o", symbolSize=6,
                symbolBrush="#F46C75", symbolPen=pg.mkPen(None),
                name="Expense"
            )

            inc_pen = pg.mkPen("#45D18F", width=2)
            inc_brush = pg.mkBrush(69, 209, 143, 45)
            self.trend_plot.plot(
                x_indices, incomes, pen=inc_pen,
                fillLevel=0, fillBrush=inc_brush,
                symbol="o", symbolSize=6,
                symbolBrush="#45D18F", symbolPen=pg.mkPen(None),
                name="Income"
            )

        # ── Bar Chart ────────────────────────────
        self.bar_plot.clear()
        total_inc = summary["total_income"]
        total_exp = summary["total_expense"]

        if total_inc > 0 or total_exp > 0:
            bg_inc = pg.BarGraphItem(x=[1], height=[total_inc], width=0.5, brush="#45D18F")
            bg_exp = pg.BarGraphItem(x=[2], height=[total_exp], width=0.5, brush="#F46C75")
            self.bar_plot.addItem(bg_inc)
            self.bar_plot.addItem(bg_exp)
            self.bar_plot.getAxis("bottom").setTicks([[(1, "Income"), (2, "Expense")]])

    def _populate_table(self, table, data, show_id=False, show_note=False):
        table.setRowCount(0)
        for i, row in enumerate(data):
            table.insertRow(i)
            col = 0

            if show_id:
                table.setItem(i, col, QTableWidgetItem(str(row["id"])))
                col += 1

            table.setItem(i, col, QTableWidgetItem(row["timestamp"]))
            col += 1
            table.setItem(i, col, QTableWidgetItem(row["category"]))
            col += 1

            type_item = QTableWidgetItem(row["type"])
            color = "#45D18F" if row["type"].lower() == "income" else "#F46C75"
            type_item.setForeground(QColor(color))
            table.setItem(i, col, type_item)
            col += 1

            amount_item = QTableWidgetItem(f"₹{row['amount']:,.2f}")
            table.setItem(i, col, amount_item)
            col += 1

            if show_note:
                note_text = row.get("note") or ""
                table.setItem(i, col, QTableWidgetItem(note_text))
                col += 1

    # ─── Transaction Actions ─────────────────────
    def _add_transaction(self):
        raw = self.input_amount.text().strip()
        if not raw:
            QMessageBox.warning(self, "Input Error", "Please enter an amount.")
            return
        try:
            amount = float(raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a positive number.")
            return

        category = self.input_category.currentText()
        t_type = self.input_type.currentText()
        timestamp = self.input_datetime.dateTime().toString("yyyy-MM-dd HH:mm")
        note = self.input_note.text().strip()

        self.controller.add_transaction(amount, category, t_type, timestamp, note)
        self.input_amount.clear()
        self.input_note.clear()
        self._refresh_data()

    def _get_selected_row_ids(self):
        """Return a list of transaction IDs from all selected rows."""
        selected = self.all_table.selectedItems()
        if not selected:
            return []
        rows = sorted(set(item.row() for item in selected))
        ids = []
        for row in rows:
            id_item = self.all_table.item(row, 0)
            if id_item:
                ids.append(int(id_item.text()))
        return ids

    def _get_selected_row_id(self):
        """Return (t_id, row_index) for the first selected row, or (None, None)."""
        selected = self.all_table.selectedItems()
        if not selected:
            return None, None
        row = selected[0].row()
        id_item = self.all_table.item(row, 0)
        if id_item is None:
            return None, None
        return int(id_item.text()), row

    def _delete_transaction(self):
        t_ids = self._get_selected_row_ids()
        if not t_ids:
            QMessageBox.warning(
                self, "Selection Error",
                "Please select at least one transaction to delete.\n(Use Ctrl+Click for multiple.)"
            )
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {len(t_ids)} selected transaction(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.bulk_delete_transactions(t_ids)
            self._refresh_data()

    def _delete_all_transactions(self):
        total = self.all_table.rowCount()
        if total == 0:
            QMessageBox.information(self, "Nothing to Delete", "There are no transactions to delete.")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete All",
            f"This will permanently delete ALL {total} transactions.\n\nThis action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.delete_all_transactions()
            self._refresh_data()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Transactions", "ZIVY_Transactions.csv", "CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            transactions = self.controller.get_all_transactions()
            if not transactions:
                QMessageBox.information(self, "Nothing to Export", "No transactions to export.")
                return

            with open(path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date & Time", "Category", "Type", "Amount (INR)", "Note"])
                for t in transactions:
                    writer.writerow([
                        t["id"], t["timestamp"], t["category"],
                        t["type"], t["amount"], t.get("note") or ""
                    ])
            QMessageBox.information(
                self, "Export Successful", f"Exported {len(transactions)} transactions to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")

    def _filter_transactions(self, text):
        search_text = text.lower().strip()
        for row in range(self.all_table.rowCount()):
            match = not search_text
            if not match:
                for col in range(1, 6):  # Skip hidden ID column
                    item = self.all_table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
            self.all_table.setRowHidden(row, not match)

    def _open_edit_dialog(self):
        t_id, row = self._get_selected_row_id()
        if t_id is None:
            QMessageBox.warning(self, "Selection Error", "Please select a transaction to edit.")
            return

        timestamp = (self.all_table.item(row, 1) or QTableWidgetItem("")).text()
        category = (self.all_table.item(row, 2) or QTableWidgetItem("")).text()
        t_type = (self.all_table.item(row, 3) or QTableWidgetItem("")).text()
        amount_str = (
            (self.all_table.item(row, 4) or QTableWidgetItem("0")).text()
            .replace("₹", "").replace(",", "")
        )
        note = (self.all_table.item(row, 5) or QTableWidgetItem("")).text()

        try:
            amount = float(amount_str)
        except ValueError:
            amount = 0.0

        dialog = EditTransactionDialog(t_id, timestamp, category, t_type, amount, note, self)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                self.controller.edit_transaction(
                    t_id, data["amount"], data["category"],
                    data["type"], data["timestamp"], data["note"]
                )
                self._refresh_data()
