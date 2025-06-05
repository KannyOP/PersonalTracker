import sys
import json
import os
from datetime import datetime
import sqlite3

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
        QDateEdit, QDoubleSpinBox, QMessageBox, QDialog, QGroupBox, QFileDialog,
        QHeaderView, QMenu, QTabWidget
    )
    from PyQt6.QtCore import Qt, QDate
    from PyQt6.QtGui import QIcon, QColor, QAction
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt6 is not installed. Please install it using: pip install PyQt6")
    sys.exit(1)

try:
    from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
    from PyQt6.QtGui import QPainter, QFont
    QTCHARTS_AVAILABLE = True
except ImportError:
    QTCHARTS_AVAILABLE = False
    # This will be handled in the UI if user tries to access the chart tab

from styles import STYLESHEET


DATABASE_FILE = "budget.db"
VALID_USERS = {"admin": "password123", "user": "test"}

GE_TRANSLATIONS = {
    "LoginWindowTitle": "ავტორიზაცია",
    "LoginTitleLabel": "ავტორიზაცია",
    "UsernameLabel": "სახელი:",
    "UsernamePlaceholder": "მომხმარებლის სახელი",
    "PasswordLabel": "პაროლი:",
    "PasswordPlaceholder": "შეიყვანეთ პაროლი",
    "LoginButton": "შესვლა",
    "InvalidCredentials": "მომხმარებლის სახელი ან პაროლი არასწორია.",

    "MainWindowTitle": "მოგესალმებით {username}",
    "MainTitleLabel": "პერსონალური ფინანსების მართვის სისტემა",
    "AddTransactionGroup": "ახალი ტრანზაქციის დამატება",
    "TypeLabel": "ტიპი:",
    "CategoryLabel": "კატეგორია:",
    "Expense": "ხარჯი",
    "Income": "შემოსავალი",
    "DateLabel": "თარიღი:",
    "DescriptionLabel": "აღწერა:",
    "DescriptionPlaceholder": "მაგ., სურსათი, ხელფასი",
    "AmountLabel": "თანხა:",
    "AddTransactionButton": "ტრანზაქციის დამატება",
    
    "TransactionsGroup": "ტრანზაქციები",
    "TransactionsTab": "ტრანზაქციები",
    "VisualizationTab": "ვიზუალიზაცია",
    "ExpenseBreakdownChartTitle": "ხარჯების განაწილება კატეგორიების მიხედვით",

    "TableHeaderDate": "თარიღი",
    "TableHeaderType": "ტიპი",
    "TableHeaderCategory": "კატეგორია",
    "TableHeaderDescription": "აღწერა",
    "TableHeaderAmount": "თანხა",
    # "TableHeaderAction": "მოქმედება", # Removed

    "SummaryActionsGroup": "შეჯამება და მოქმედებები",
    "TotalIncomeLabel": "სულ შემოსავალი:",
    "TotalExpensesLabel": "სულ ხარჯები:",
    "BalanceLabel": "ბალანსი:",
    "ExportPDFButton": "რეპორტის ექსპორტი (PDF)",
    "DeleteHintLabel": "მინიშნება: ტრანზაქციის წასაშლელად დააწკაპუნეთ მასზე მარჯვენა ღილაკით ცხრილში.",
    "DeleteActionText": "ტრანზაქციის წაშლა",
    
    "ErrorMsg": "შეცდომა",
    "InvalidTransactionDelete": "წასაშლელად არჩეულია არასწორი ტრანზაქცია.",
    "ConfirmDeleteTitle": "წაშლის დადასტურება",
    "ConfirmDeleteMsg": "დარწმუნებული ხართ, რომ გსურთ ამ ტრანზაქციის წაშლა: '{description}'?",
    "InputErrorTitle": "შეყვანის შეცდომა",
    "EmptyDescriptionError": "აღწერა არ შეიძლება იყოს ცარიელი (თუ კატეგორია არაა საკმარისი).",
    "EmptyCategoryError": "აირჩიეთ კატეგორია.",
    "ZeroAmountError": " თანხა უნდა იყოს ნულზე მეტი.",
    
    "DataLoadErrorTitle": "მონაცემების ჩატვირთვის შეცდომა",
    "DBErrorMsg": "მონაცემთა ბაზასთან დაკავშირების ან ოპერაციის შეცდომა: {error}",
    "UnexpectedLoadErrorMsg": "მონაცემების ჩატვირთვისას მოხდა მოულოდნელი შეცდომა: {error}",
    "SaveErrorMsg": "{file} ფაილში მონაცემების შენახვა ვერ მოხერხდა: {error}", # Kept for context, though DB errors handled differently
    
    "NoDataToExportTitle": "მონაცემები არ არის",
    "NoDataToExportMsg": "საექსპორტო ტრანზაქციები არ არსებობს.",
    "SavePDFDialogTitle": "PDF რეპორტის შენახვა",
    "PDFFilesFilter": "PDF ფაილები (*.pdf)",
    "PDFReportTitle": "ბიუჯეტის ანგარიში",
    "PDFReportGeneratedBy": "ანგარიში გენერირებულია მომხმარებლის მიერ: {username}",
    "PDFReportGeneratedOn": "გენერირების თარიღი: {datetime}",
    "PDFTotalIncome": "სულ შემოსავალი: {currency_symbol}{amount:.2f}",
    "PDFTotalExpenses": "სულ ხარჯები: {currency_symbol}{amount:.2f}",
    "PDFFinalBalance": "საბოლოო ბალანსი: {currency_symbol}{amount:.2f}",
    "PDFExpensesByCategoryTitle": "ხარჯები კატეგორიების მიხედვით:",
    "ExportSuccessTitle": "ექსპორტი წარმატებულია",
    "ExportSuccessMsg": "რეპორტი შენახულია აქ: {path}",
    "ExportErrorTitle": "ექსპორტის შეცდომა",
    "ExportErrorMsg": "PDF-ის გენერირება ვერ მოხერხდა: {error}",
    "ReportLabMissingError": "ReportLab ბიბლიოთეკა არ არის დაყენებული. გთხოვთ დააყენოთ PDF ექსპორტისთვის (pip install reportlab).",
    "QtChartsMissingError": "PyQtCharts მოდული არ არის დაყენებული ან ვერ ჩაიტვირთა. ვიზუალიზაცია მიუწვდომელია. (pip install PyQt6-Charts)",
    "CurrencySymbol": "₾",

    # Categories
    "SALARY_CAT": "ხელფასი",
    "GIFT_CAT": "საჩუქარი",
    "INVESTMENT_INCOME_CAT": "ინვესტიცია (შემოსავალი)",
    "OTHER_INCOME_CAT": "სხვა შემოსავალი",
    "FOOD_CAT": "სურსათი",
    "UTILITIES_CAT": "კომუნალური გადასახადები",
    "RENT_MORTGAGE_CAT": "ქირა/იპოთეკა",
    "TRANSPORT_CAT": "ტრანსპორტი",
    "HEALTHCARE_CAT": "ჯანდაცვა",
    "EDUCATION_CAT": "განათლება",
    "ENTERTAINMENT_CAT": "გართობა",
    "CLOTHING_CAT": "ტანსაცმელი",
    "PERSONAL_CARE_CAT": "პირადი ჰიგიენა",
    "DEBT_PAYMENT_CAT": "ვალის გადახდა",
    "SAVINGS_INVESTMENT_EXPENSE_CAT": "დანაზოგი/ინვესტიცია (ხარჯი)",
    "OTHER_EXPENSE_CAT": "სხვა ხარჯი"
}
T = GE_TRANSLATIONS

INTERNAL_TYPE_EXPENSE = "Expense"
INTERNAL_TYPE_INCOME = "Income"

TYPE_INTERNAL_TO_DISPLAY = {
    INTERNAL_TYPE_EXPENSE: T["Expense"],
    INTERNAL_TYPE_INCOME: T["Income"]
}
TYPE_DISPLAY_TO_INTERNAL = {
    T["Expense"]: INTERNAL_TYPE_EXPENSE,
    T["Income"]: INTERNAL_TYPE_INCOME
}

CATEGORIES_MAP = {
    INTERNAL_TYPE_INCOME: {
        "SALARY": T["SALARY_CAT"],
        "GIFT": T["GIFT_CAT"],
        "INVESTMENT_INCOME": T["INVESTMENT_INCOME_CAT"],
        "OTHER_INCOME": T["OTHER_INCOME_CAT"]
    },
    INTERNAL_TYPE_EXPENSE: {
        "FOOD": T["FOOD_CAT"],
        "UTILITIES": T["UTILITIES_CAT"],
        "RENT_MORTGAGE": T["RENT_MORTGAGE_CAT"],
        "TRANSPORT": T["TRANSPORT_CAT"],
        "HEALTHCARE": T["HEALTHCARE_CAT"],
        "EDUCATION": T["EDUCATION_CAT"],
        "ENTERTAINMENT": T["ENTERTAINMENT_CAT"],
        "CLOTHING": T["CLOTHING_CAT"],
        "PERSONAL_CARE": T["PERSONAL_CARE_CAT"],
        "DEBT_PAYMENT": T["DEBT_PAYMENT_CAT"],
        "SAVINGS_INVESTMENT_EXPENSE": T["SAVINGS_INVESTMENT_EXPENSE_CAT"],
        "OTHER_EXPENSE": T["OTHER_EXPENSE_CAT"]
    }
}

# Create reverse maps for categories (Display Name -> Internal Key)
CATEGORIES_DISPLAY_TO_INTERNAL = {
    trans_type: {v: k for k, v in cats.items()}
    for trans_type, cats in CATEGORIES_MAP.items()
}


def init_db():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL,
                username TEXT NOT NULL 
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        # This error might occur before GUI is up, so print or basic dialog
        print(f"Database initialization error: {e}")
        # In a real app, might need a more robust way to handle this startup error
        QMessageBox.critical(None, T["ErrorMsg"], T["DBErrorMsg"].format(error=e))
        sys.exit(1)


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T["LoginWindowTitle"])
        self.setModal(True)
        self.user = None

        layout = QGridLayout(self)
        self.setStyleSheet(STYLESHEET)

        self.title_label = QLabel(T["LoginTitleLabel"])
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 0, 0, 1, 2)

        layout.addWidget(QLabel(T["UsernameLabel"]), 1, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(T["UsernamePlaceholder"])
        layout.addWidget(self.username_input, 1, 1)

        layout.addWidget(QLabel(T["PasswordLabel"]), 2, 0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(T["PasswordPlaceholder"])
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input, 2, 1)

        self.login_button = QPushButton(T["LoginButton"])
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button, 3, 0, 1, 2)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label, 4, 0, 1, 2)

        self.setLayout(layout)
        self.setFixedSize(350, 250)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username in VALID_USERS and VALID_USERS[username] == password:
            self.user = username
            self.accept()
        else:
            self.status_label.setText(T["InvalidCredentials"])
            self.password_input.clear()


class BudgetApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.db_conn = None
        try:
            self.db_conn = sqlite3.connect(DATABASE_FILE)
        except sqlite3.Error as e:
            QMessageBox.critical(self, T["ErrorMsg"], T["DBErrorMsg"].format(error=e))
            sys.exit(1)

        self.setWindowTitle(T["MainWindowTitle"].format(username=username))
        self.setGeometry(100, 100, 1200, 800) # Increased size for tabs
        self.setStyleSheet(STYLESHEET)

        self.transactions = []
        
        self.init_ui()
        self.load_data() # This will also call update_all_views

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel(T["MainTitleLabel"])
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- Transactions Tab ---
        transactions_tab_widget = QWidget()
        transactions_layout = QVBoxLayout(transactions_tab_widget)
        
        grid_layout = QGridLayout() # For inputs and table/summary
        transactions_layout.addLayout(grid_layout)

        input_group = QGroupBox(T["AddTransactionGroup"])
        input_layout = QGridLayout(input_group)

        input_layout.addWidget(QLabel(T["TypeLabel"]), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems([TYPE_INTERNAL_TO_DISPLAY[INTERNAL_TYPE_INCOME], TYPE_INTERNAL_TO_DISPLAY[INTERNAL_TYPE_EXPENSE]])
        self.type_combo.currentIndexChanged.connect(self.update_category_combo)
        input_layout.addWidget(self.type_combo, 0, 1)

        input_layout.addWidget(QLabel(T["CategoryLabel"]), 0, 2)
        self.category_combo = QComboBox()
        input_layout.addWidget(self.category_combo, 0, 3)
        self.update_category_combo() # Initial population

        input_layout.addWidget(QLabel(T["DateLabel"]), 1, 0)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        input_layout.addWidget(self.date_edit, 1, 1)

        input_layout.addWidget(QLabel(T["AmountLabel"]), 1, 2)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 10000000.00)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix(T["CurrencySymbol"] + " ")
        input_layout.addWidget(self.amount_input, 1, 3)
        
        input_layout.addWidget(QLabel(T["DescriptionLabel"]), 2, 0)
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText(T["DescriptionPlaceholder"])
        input_layout.addWidget(self.desc_input, 2, 1, 1, 3) # Span 3 columns

        self.add_button = QPushButton(T["AddTransactionButton"])
        self.add_button.setObjectName("successButton")
        self.add_button.clicked.connect(self.add_transaction)
        input_layout.addWidget(self.add_button, 3, 0, 1, 4) # Span all 4 columns

        input_layout.setColumnStretch(1, 1)
        input_layout.setColumnStretch(3, 1)
        grid_layout.addWidget(input_group, 0, 0, 1, 2) # Span 2 columns in main grid

        table_group = QGroupBox(T["TransactionsGroup"])
        table_layout = QVBoxLayout(table_group)
        self.table = QTableWidget()
        self.table.setColumnCount(5) # Date, Type, Category, Description, Amount
        self.table.setHorizontalHeaderLabels([
            T["TableHeaderDate"], T["TableHeaderType"], T["TableHeaderCategory"],
            T["TableHeaderDescription"], T["TableHeaderAmount"]
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Description
        self.table.setColumnWidth(3, 300)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)
        table_layout.addWidget(self.table)
        grid_layout.addWidget(table_group, 1, 0) # Row 1, Col 0

        summary_actions_group = QGroupBox(T["SummaryActionsGroup"])
        summary_actions_layout = QVBoxLayout(summary_actions_group)
        summary_grid = QGridLayout()

        summary_grid.addWidget(QLabel(T["TotalIncomeLabel"]), 0, 0)
        self.total_income_label = QLabel(f"{T['CurrencySymbol']}0.00")
        self.total_income_label.setStyleSheet("color: green; font-weight: bold;")
        summary_grid.addWidget(self.total_income_label, 0, 1, Qt.AlignmentFlag.AlignRight)

        summary_grid.addWidget(QLabel(T["TotalExpensesLabel"]), 1, 0)
        self.total_expenses_label = QLabel(f"{T['CurrencySymbol']}0.00")
        self.total_expenses_label.setStyleSheet("color: red; font-weight: bold;")
        summary_grid.addWidget(self.total_expenses_label, 1, 1, Qt.AlignmentFlag.AlignRight)

        summary_grid.addWidget(QLabel(T["BalanceLabel"]), 2, 0)
        self.balance_label = QLabel(f"{T['CurrencySymbol']}0.00")
        self.balance_label.setObjectName("balanceLabelPositive")
        summary_grid.addWidget(self.balance_label, 2, 1, Qt.AlignmentFlag.AlignRight)
        
        summary_actions_layout.addLayout(summary_grid)
        summary_actions_layout.addStretch(1)

        self.export_pdf_button = QPushButton(T["ExportPDFButton"])
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        summary_actions_layout.addWidget(self.export_pdf_button)
        grid_layout.addWidget(summary_actions_group, 1, 1) # Row 1, Col 1

        grid_layout.setColumnStretch(0, 3) # Table takes more space
        grid_layout.setColumnStretch(1, 1) # Summary takes less

        info_label = QLabel(T["DeleteHintLabel"])
        info_label.setObjectName("infoLabel")
        transactions_layout.addWidget(info_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.tabs.addTab(transactions_tab_widget, T["TransactionsTab"])

        # --- Visualization Tab ---
        visualization_tab_widget = QWidget()
        visualization_layout = QVBoxLayout(visualization_tab_widget)
        if QTCHARTS_AVAILABLE:
            self.chart_view = QChartView()
            self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            visualization_layout.addWidget(self.chart_view)
        else:
            error_label = QLabel(T["QtChartsMissingError"])
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setWordWrap(True)
            visualization_layout.addWidget(error_label)
        
        self.tabs.addTab(visualization_tab_widget, T["VisualizationTab"])
        
    def update_category_combo(self):
        current_type_display = self.type_combo.currentText()
        current_type_internal = TYPE_DISPLAY_TO_INTERNAL.get(current_type_display)

        self.category_combo.clear()
        if current_type_internal and current_type_internal in CATEGORIES_MAP:
            categories = CATEGORIES_MAP[current_type_internal]
            self.category_combo.addItems(categories.values())

    def show_table_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item: return
        row = item.row()
        if not (0 <= row < len(self.transactions)): return

        menu = QMenu(self.table)
        delete_action = QAction(T["DeleteActionText"], self)
        # self.transactions[row]['id'] will give the DB id
        delete_action.triggered.connect(lambda: self.delete_transaction(self.transactions[row]['id'], self.transactions[row]['description']))
        menu.addAction(delete_action)
        menu.exec(self.table.mapToGlobal(pos))

    def delete_transaction(self, transaction_id, transaction_desc):
        reply = QMessageBox.question(self, T["ConfirmDeleteTitle"],
                                     T["ConfirmDeleteMsg"].format(description=transaction_desc),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id = ? AND username = ?", (transaction_id, self.username))
                self.db_conn.commit()
                self.load_data() # Reload and update all views
            except sqlite3.Error as e:
                QMessageBox.critical(self, T["ErrorMsg"], T["DBErrorMsg"].format(error=e))

    def add_transaction(self):
        ttype_display = self.type_combo.currentText()
        ttype_internal = TYPE_DISPLAY_TO_INTERNAL[ttype_display]
        
        category_display = self.category_combo.currentText()
        if not category_display:
            QMessageBox.warning(self, T["InputErrorTitle"], T["EmptyCategoryError"])
            return
        category_internal = CATEGORIES_DISPLAY_TO_INTERNAL[ttype_internal][category_display]
        
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        desc = self.desc_input.text().strip()
        amount = self.amount_input.value()

        # Description can be empty if category is specific enough
        # if not desc:
        #     QMessageBox.warning(self, T["InputErrorTitle"], T["EmptyDescriptionError"])
        #     return
        if amount <= 0:
            QMessageBox.warning(self, T["InputErrorTitle"], T["ZeroAmountError"])
            return

        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (date, type, category, description, amount, username)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, ttype_internal, category_internal, desc, amount, self.username))
            self.db_conn.commit()
            
            self.load_data() # Reload and update all views

            self.desc_input.clear()
            self.amount_input.setValue(self.amount_input.minimum()) # Reset to minimum
            self.type_combo.setCurrentIndex(0) # Default to first type (Income)
            self.update_category_combo() # Ensure categories for Income are shown
            self.category_combo.setCurrentIndex(0) # Default to first category
            self.date_edit.setDate(QDate.currentDate())

        except sqlite3.Error as e:
            QMessageBox.critical(self, T["ErrorMsg"], T["DBErrorMsg"].format(error=e))


    def update_all_views(self):
        self.update_table()
        self.update_summary()
        if QTCHARTS_AVAILABLE:
            self.update_pie_chart()
        else:
            # Potentially update a message in the chart tab if it's currently visible
            if self.tabs.currentWidget() == self.tabs.widget(1): # Assuming visualization is tab 1
                 # Find the label if it exists and re-affirm the error or a "no data" message
                 pass


    def update_table(self):
        self.table.setRowCount(0)
        for i, t in enumerate(self.transactions):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(t["date"]))
            
            display_type = TYPE_INTERNAL_TO_DISPLAY[t["type"]]
            type_item = QTableWidgetItem(display_type)
            type_item.setForeground(QColor("green") if t["type"] == INTERNAL_TYPE_INCOME else QColor("red"))
            self.table.setItem(i, 1, type_item)

            category_display = CATEGORIES_MAP[t["type"]].get(t["category"], t["category"]) # Fallback to raw if not in map
            self.table.setItem(i, 2, QTableWidgetItem(category_display))
            
            self.table.setItem(i, 3, QTableWidgetItem(t["description"]))
            
            amount_item = QTableWidgetItem(f"{T['CurrencySymbol']}{t['amount']:.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 4, amount_item)

    def update_summary(self):
        total_income = sum(t["amount"] for t in self.transactions if t["type"] == INTERNAL_TYPE_INCOME)
        total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == INTERNAL_TYPE_EXPENSE)
        balance = total_income - total_expenses

        self.total_income_label.setText(f"{T['CurrencySymbol']}{total_income:.2f}")
        self.total_expenses_label.setText(f"{T['CurrencySymbol']}{total_expenses:.2f}")
        self.balance_label.setText(f"{T['CurrencySymbol']}{balance:.2f}")

        self.balance_label.setObjectName("balanceLabelPositive" if balance >= 0 else "balanceLabelNegative")
        self.balance_label.setStyleSheet(STYLESHEET) # Reapply stylesheet for object name change

    def update_pie_chart(self):
        if not QTCHARTS_AVAILABLE: return

        series = QPieSeries()
        series.setHoleSize(0.35) # Donut chart

        expenses_by_category = {}
        for t in self.transactions:
            if t["type"] == INTERNAL_TYPE_EXPENSE:
                cat_display = CATEGORIES_MAP[INTERNAL_TYPE_EXPENSE].get(t["category"], t["category"])
                expenses_by_category[cat_display] = expenses_by_category.get(cat_display, 0) + t["amount"]
        
        if not expenses_by_category: # No expense data
            series.append("No expenses", 1).setBrush(QColor("#e0e0e0")) # Placeholder
        else:
            for category, total_amount in sorted(expenses_by_category.items(), key=lambda item: item[1], reverse=True):
                slice_val = series.append(f"{category}: {T['CurrencySymbol']}{total_amount:.2f}", total_amount)
                slice_val.setLabelVisible(True)
                # Basic coloring, can be improved
                # slice_val.setBrush(QColor(hash(category) % 200 + 55, hash(category[::-1]) % 200 + 55, hash(category*2) % 200 + 55))


        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(T["ExpenseBreakdownChartTitle"])
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Customize font for title and legend if needed (especially for Georgian)
        font = QFont()
        # font.setFamily("Sylfaen") # If Sylfaen is available and preferred for charts
        font.setPointSize(12)
        chart.setTitleFont(font)
        font.setPointSize(10)
        chart.legend().setFont(font)

        self.chart_view.setChart(chart)


    def load_data(self):
        try:
            cursor = self.db_conn.cursor()
            # Load only transactions for the current user
            cursor.execute("SELECT id, date, type, category, description, amount FROM transactions WHERE username = ? ORDER BY date DESC, id DESC", (self.username,))
            rows = cursor.fetchall()
            self.transactions = []
            for row in rows:
                self.transactions.append({
                    "id": row[0], "date": row[1], "type": row[2], 
                    "category": row[3], "description": row[4], "amount": row[5]
                })
        except sqlite3.Error as e:
            self.transactions = []
            QMessageBox.critical(self, T["DataLoadErrorTitle"], T["DBErrorMsg"].format(error=e))
        except Exception as e: # Catch any other unexpected error
            self.transactions = []
            QMessageBox.critical(self, T["ErrorMsg"], T["UnexpectedLoadErrorMsg"].format(error=e))
        
        self.update_all_views()


    def export_to_pdf(self):
        if not self.transactions:
            QMessageBox.information(self, T["NoDataToExportTitle"], T["NoDataToExportMsg"])
            return

        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.pdfbase import pdfmetrics
            from reportlab.lib.units import inch
            
            georgian_font_name = 'Helvetica' # Fallback
            try:
                # Ensure you have a Georgian TTF font file (e.g., Sylfaen.ttf)
                # in the same directory or provide a full path.
                # For deployment, bundling the font is best.
                font_path = "Sylfaen.ttf" # Assumes Sylfaen.ttf is in the same dir or system path
                if os.path.exists(font_path):
                     pdfmetrics.registerFont(TTFont('Sylfaen', font_path))
                     georgian_font_name = 'Sylfaen'
                else: # Try common system paths for Sylfaen if not local
                    # This is system-dependent and might not work everywhere
                    system_font_paths = [
                        "/usr/share/fonts/truetype/msttcorefonts/Sylfaen.ttf", # Linux
                        "C:/Windows/Fonts/sylfaen.ttf" # Windows
                    ]
                    for p in system_font_paths:
                        if os.path.exists(p):
                            pdfmetrics.registerFont(TTFont('Sylfaen', p))
                            georgian_font_name = 'Sylfaen'
                            break
                if georgian_font_name == 'Helvetica':
                    print("Warning: Sylfaen.ttf not found. PDF will use Helvetica, Georgian characters may not render correctly.")

            except Exception as font_e:
                print(f"Font loading error: {font_e}. Using Helvetica.")


            path, _ = QFileDialog.getSaveFileName(self, T["SavePDFDialogTitle"], f"BudgetReport_{self.username}_{datetime.now().strftime('%Y%m%d')}.pdf", T["PDFFilesFilter"])
            if not path:
                return

            doc = SimpleDocTemplate(path, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
            styles = getSampleStyleSheet()
            
            styles.add(ParagraphStyle(name='GeorgianNormal', fontName=georgian_font_name, fontSize=10, leading=12, parent=styles['Normal']))
            styles.add(ParagraphStyle(name='GeorgianH1', fontName=georgian_font_name, fontSize=18, alignment=1, spaceAfter=12, parent=styles['h1'])) # Centered
            styles.add(ParagraphStyle(name='GeorgianH2', fontName=georgian_font_name, fontSize=14, spaceBefore=10, spaceAfter=6, parent=styles['h2']))
            styles.add(ParagraphStyle(name='GeorgianH3', fontName=georgian_font_name, fontSize=12, spaceBefore=6, spaceAfter=4, parent=styles['h3']))
            styles.add(ParagraphStyle(name='GeorgianTableHeader', fontName=georgian_font_name, fontSize=10, alignment=1, parent=styles['Normal'])) # Centered
            styles.add(ParagraphStyle(name='GeorgianCell', fontName=georgian_font_name, fontSize=9, parent=styles['Normal']))
            styles.add(ParagraphStyle(name='GeorgianAmountCell', fontName=georgian_font_name, fontSize=9, alignment=2, parent=styles['Normal'])) # Right align

            story = []

            story.append(Paragraph(T["PDFReportTitle"], styles['GeorgianH1']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(T["PDFReportGeneratedBy"].format(username=self.username), styles['GeorgianNormal']))
            story.append(Paragraph(T["PDFReportGeneratedOn"].format(datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), styles['GeorgianNormal']))
            story.append(Spacer(1, 0.3*inch))

            total_income = sum(t["amount"] for t in self.transactions if t["type"] == INTERNAL_TYPE_INCOME)
            total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == INTERNAL_TYPE_EXPENSE)
            balance = total_income - total_expenses

            story.append(Paragraph(T["PDFTotalIncome"].format(currency_symbol=T["CurrencySymbol"], amount=total_income), styles['GeorgianH3']))
            story.append(Paragraph(T["PDFTotalExpenses"].format(currency_symbol=T["CurrencySymbol"], amount=total_expenses), styles['GeorgianH3']))
            story.append(Paragraph(T["PDFFinalBalance"].format(currency_symbol=T["CurrencySymbol"], amount=balance), styles['GeorgianH3']))
            story.append(Spacer(1, 0.3*inch))

            # Expenses by Category
            story.append(Paragraph(T["PDFExpensesByCategoryTitle"], styles['GeorgianH2']))
            expenses_by_category = {}
            for t in self.transactions:
                if t["type"] == INTERNAL_TYPE_EXPENSE:
                    cat_display = CATEGORIES_MAP[INTERNAL_TYPE_EXPENSE].get(t["category"], t["category"])
                    expenses_by_category[cat_display] = expenses_by_category.get(cat_display, 0) + t["amount"]
            
            if expenses_by_category:
                cat_data = [[Paragraph(T["TableHeaderCategory"], styles['GeorgianTableHeader']), Paragraph(T["TableHeaderAmount"], styles['GeorgianTableHeader'])]]
                for cat, amt in sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True):
                    cat_data.append([
                        Paragraph(cat, styles['GeorgianCell']),
                        Paragraph(f"{T['CurrencySymbol']}{amt:.2f}", styles['GeorgianAmountCell'])
                    ])
                cat_table = Table(cat_data, colWidths=[3*inch, 1.5*inch])
                cat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(cat_table)
            else:
                story.append(Paragraph("ხარჯები არ მოიძებნა.", styles['GeorgianNormal'])) # No expenses found
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(T["TransactionsTab"], styles['GeorgianH2'])) # Full Transactions List

            # Full Transactions Table
            data = [[
                Paragraph(T["TableHeaderDate"], styles['GeorgianTableHeader']),
                Paragraph(T["TableHeaderType"], styles['GeorgianTableHeader']),
                Paragraph(T["TableHeaderCategory"], styles['GeorgianTableHeader']),
                Paragraph(T["TableHeaderDescription"], styles['GeorgianTableHeader']),
                Paragraph(T["TableHeaderAmount"], styles['GeorgianTableHeader'])
            ]]
            
            for t in sorted(self.transactions, key=lambda x: (x["date"], x["id"])): # Sort by date, then id
                cat_display = CATEGORIES_MAP[t["type"]].get(t["category"], t["category"])
                data.append([
                    Paragraph(t["date"], styles['GeorgianCell']),
                    Paragraph(TYPE_INTERNAL_TO_DISPLAY[t["type"]], styles['GeorgianCell']),
                    Paragraph(cat_display, styles['GeorgianCell']),
                    Paragraph(t["description"] if t["description"] else "-", styles['GeorgianCell']),
                    Paragraph(f"{T['CurrencySymbol']}{t['amount']:.2f}", styles['GeorgianAmountCell'])
                ])

            table = Table(data, colWidths=[0.8*inch, 0.8*inch, 1.5*inch, 3*inch, 1*inch]) # Adjusted widths
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), georgian_font_name), # Ensure header font
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)

            doc.build(story)
            QMessageBox.information(self, T["ExportSuccessTitle"], T["ExportSuccessMsg"].format(path=path))
        except ImportError:
             QMessageBox.critical(self, T["ExportErrorTitle"], T["ReportLabMissingError"])
        except Exception as e:
            QMessageBox.critical(self, T["ExportErrorTitle"], T["ExportErrorMsg"].format(error=e))
            import traceback
            traceback.print_exc()


    def closeEvent(self, event):
        if self.db_conn:
            self.db_conn.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    if os.path.exists("icon.png"): # Make sure you have an icon.png or remove this
        app.setWindowIcon(QIcon("icon.png"))
    
    init_db() # Initialize database schema before login or app starts

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        main_window = BudgetApp(login_dialog.user)
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    if not PYQT_AVAILABLE:
        # If PyQt6 isn't available, main() won't be useful.
        # The initial print statement in the imports section already informed the user.
        sys.exit(1)
    main()