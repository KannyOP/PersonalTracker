# budget_app.py
import sys
import json
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QDateEdit, QDoubleSpinBox, QMessageBox, QDialog, QGroupBox, QFileDialog,
    QHeaderView, QMenu
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QColor, QAction # Added QAction

# Import stylesheet
from styles import STYLESHEET

# --- Configuration ---
DATA_FILE = "budget_data.json"
# For a real app, use hashed passwords and a more secure store
# For this demo, hardcoded credentials
VALID_USERS = {"admin": "password123", "user": "test"}

# --- Login Dialog ---
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Budget Tracker")
        self.setModal(True)
        self.user = None

        layout = QGridLayout(self)
        self.setStyleSheet(STYLESHEET) # Apply stylesheet to dialog

        self.title_label = QLabel("Budget Tracker Login")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 0, 0, 1, 2)

        layout.addWidget(QLabel("Username:"), 1, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        layout.addWidget(self.username_input, 1, 1)

        layout.addWidget(QLabel("Password:"), 2, 0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input, 2, 1)

        self.login_button = QPushButton("Login")
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
            self.status_label.setText("Invalid username or password.")
            self.password_input.clear()


# --- Main Application Window ---
class BudgetApp(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"Personal Budget Tracker - Welcome {username}")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(STYLESHEET)

        self.transactions = []
        self.load_data()

        self.init_ui()
        self.update_table()
        self.update_summary()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel("My Personal Budget")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

        input_group = QGroupBox("Add New Transaction")
        input_layout = QGridLayout(input_group)

        input_layout.addWidget(QLabel("Type:"), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Expense", "Income"])
        input_layout.addWidget(self.type_combo, 0, 1)

        input_layout.addWidget(QLabel("Date:"), 0, 2)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        input_layout.addWidget(self.date_edit, 0, 3)

        input_layout.addWidget(QLabel("Description:"), 1, 0)
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("e.g., Groceries, Salary")
        input_layout.addWidget(self.desc_input, 1, 1, 1, 3)

        input_layout.addWidget(QLabel("Amount:"), 2, 0)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1000000.00)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$ ")
        input_layout.addWidget(self.amount_input, 2, 1)

        self.add_button = QPushButton("Add Transaction")
        self.add_button.setObjectName("successButton")
        self.add_button.clicked.connect(self.add_transaction)
        input_layout.addWidget(self.add_button, 2, 2, 1, 2)

        input_layout.setColumnStretch(1, 2)
        input_layout.setColumnStretch(3, 1)
        grid_layout.addWidget(input_group, 0, 0, 1, 2)

        table_group = QGroupBox("Transactions")
        table_layout = QVBoxLayout(table_group)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Description", "Amount", "Action"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(2, 350)
        table_layout.addWidget(self.table)
        grid_layout.addWidget(table_group, 1, 0)

        summary_actions_group = QGroupBox("Summary & Actions")
        summary_actions_layout = QVBoxLayout(summary_actions_group)
        summary_grid = QGridLayout()

        summary_grid.addWidget(QLabel("Total Income:"), 0, 0)
        self.total_income_label = QLabel("$0.00")
        self.total_income_label.setStyleSheet("color: green; font-weight: bold;")
        summary_grid.addWidget(self.total_income_label, 0, 1, Qt.AlignmentFlag.AlignRight)

        summary_grid.addWidget(QLabel("Total Expenses:"), 1, 0)
        self.total_expenses_label = QLabel("$0.00")
        self.total_expenses_label.setStyleSheet("color: red; font-weight: bold;")
        summary_grid.addWidget(self.total_expenses_label, 1, 1, Qt.AlignmentFlag.AlignRight)

        summary_grid.addWidget(QLabel("Balance:"), 2, 0)
        self.balance_label = QLabel("$0.00")
        self.balance_label.setObjectName("balanceLabelPositive")
        summary_grid.addWidget(self.balance_label, 2, 1, Qt.AlignmentFlag.AlignRight)

        summary_actions_layout.addLayout(summary_grid)
        summary_actions_layout.addStretch(1)

        self.export_pdf_button = QPushButton("Export Report (PDF)")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        summary_actions_layout.addWidget(self.export_pdf_button)
        grid_layout.addWidget(summary_actions_group, 1, 1)

        grid_layout.setColumnStretch(0, 3)
        grid_layout.setColumnStretch(1, 1)

        info_label = QLabel("Tip: Right-click on a transaction in the table to delete it.")
        info_label.setObjectName("infoLabel")
        main_layout.addWidget(info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)

    def show_table_context_menu(self, pos):
        item = self.table.itemAt(pos) # Get item at the clicked position
        if not item: # Clicked on empty space in the table
            return

        row = item.row() # Get the row of the clicked item

        menu = QMenu(self.table) # Create QMenu, parented to the table
        
        delete_action = QAction("Delete Transaction", self) # Create QAction
        # Optionally, add an icon: delete_action.setIcon(QIcon("path/to/delete_icon.png"))
        
        # Connect the action's triggered signal to delete_transaction, passing the row
        delete_action.triggered.connect(lambda: self.delete_transaction(row))
        
        menu.addAction(delete_action)
        menu.exec(self.table.mapToGlobal(pos)) # Show menu at global cursor position

    def delete_transaction(self, row_index):
        if not (0 <= row_index < len(self.transactions)):
            # This should ideally not happen if row is obtained correctly from itemAt(pos)
            QMessageBox.warning(self, "Error", "Invalid transaction selected for deletion.")
            return

        transaction_desc = self.transactions[row_index]['description']
        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete this transaction: '{transaction_desc}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self.transactions[row_index]
            self.save_data()
            self.update_table()
            self.update_summary()

    def add_transaction(self):
        ttype = self.type_combo.currentText()
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        desc = self.desc_input.text().strip()
        amount = self.amount_input.value()

        if not desc:
            QMessageBox.warning(self, "Input Error", "Description cannot be empty.")
            return
        if amount <= 0:
            QMessageBox.warning(self, "Input Error", "Amount must be greater than zero.")
            return

        transaction = {
            "date": date_str,
            "type": ttype,
            "description": desc,
            "amount": amount
        }
        self.transactions.append(transaction)
        self.transactions.sort(key=lambda x: x["date"], reverse=True)

        self.save_data()
        self.update_table()
        self.update_summary()

        self.desc_input.clear()
        self.amount_input.setValue(0.01)
        self.type_combo.setCurrentIndex(0)
        self.date_edit.setDate(QDate.currentDate())

    def update_table(self):
        self.table.setRowCount(0)
        for i, t in enumerate(self.transactions):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(t["date"]))
            
            type_item = QTableWidgetItem(t["type"])
            if t["type"] == "Income":
                type_item.setForeground(QColor("green"))
            else:
                type_item.setForeground(QColor("red"))
            self.table.setItem(i, 1, type_item)
            
            self.table.setItem(i, 2, QTableWidgetItem(t["description"]))
            
            amount_item = QTableWidgetItem(f"${t['amount']:.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 3, amount_item)

            action_item = QTableWidgetItem("Right-click to delete")
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            action_item.setToolTip("Right-click for options")
            self.table.setItem(i, 4, action_item)

    def update_summary(self):
        total_income = sum(t["amount"] for t in self.transactions if t["type"] == "Income")
        total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == "Expense")
        balance = total_income - total_expenses

        self.total_income_label.setText(f"${total_income:.2f}")
        self.total_expenses_label.setText(f"${total_expenses:.2f}")
        self.balance_label.setText(f"${balance:.2f}")

        if balance >= 0:
            self.balance_label.setObjectName("balanceLabelPositive")
        else:
            self.balance_label.setObjectName("balanceLabelNegative")
        self.balance_label.setStyleSheet(STYLESHEET) # Reapply to catch object name changes

    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r") as f:
                    self.transactions = json.load(f)
                    self.transactions.sort(key=lambda x: x["date"], reverse=True)
        except json.JSONDecodeError:
            self.transactions = []
            QMessageBox.warning(self, "Data Load Error", f"Could not load data from {DATA_FILE}. File might be corrupted. Starting fresh.")
        except Exception as e:
            self.transactions = []
            QMessageBox.critical(self, "Error", f"An unexpected error occurred while loading data: {e}")

    def save_data(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(self.transactions, f, indent=4)
        except Exception as e:
             QMessageBox.critical(self, "Error", f"Could not save data to {DATA_FILE}: {e}")

    def export_to_pdf(self):
        if not self.transactions:
            QMessageBox.information(self, "No Data", "There are no transactions to export.")
            return

        # Ensure reportlab is imported (should be at the top, but good to double-check if splitting further)
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "", "PDF Files (*.pdf)")
        if not path:
            return

        doc = SimpleDocTemplate(path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Budget Report", styles['h1']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Report Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 24))

        total_income = sum(t["amount"] for t in self.transactions if t["type"] == "Income")
        total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == "Expense")
        balance = total_income - total_expenses

        story.append(Paragraph(f"Total Income: ${total_income:.2f}", styles['h3']))
        story.append(Paragraph(f"Total Expenses: ${total_expenses:.2f}", styles['h3']))
        story.append(Paragraph(f"Final Balance: ${balance:.2f}", styles['h3']))
        story.append(Spacer(1, 24))

        data = [["Date", "Type", "Description", "Amount"]]
        for t in sorted(self.transactions, key=lambda x: x["date"]):
            data.append([
                t["date"],
                t["type"],
                t["description"],
                f"${t['amount']:.2f}"
            ])

        table = Table(data, colWidths=[70, 70, 280, 70])
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ])
        table.setStyle(table_style)
        story.append(table)

        try:
            doc.build(story)
            QMessageBox.information(self, "Export Successful", f"Report saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Could not generate PDF: {e}")

    def closeEvent(self, event):
        self.save_data()
        event.accept()


def main():
    app = QApplication(sys.argv)
    # Optional: Create an icon.png file in the same directory for the app icon
    if os.path.exists("icon.png"):
        app.setWindowIcon(QIcon("icon.png"))

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        main_window = BudgetApp(login_dialog.user)
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()