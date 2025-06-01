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
from PyQt6.QtGui import QIcon, QColor, QAction

from styles import STYLESHEET


DATA_FILE = "budget_data.json"
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
    "Expense": "ხარჯი",
    "Income": "შემოსავალი",
    "DateLabel": "თარიღი:",
    "DescriptionLabel": "აღწერა:",
    "DescriptionPlaceholder": "მაგ., სურსათი, ხელფასი",
    "AmountLabel": "თანხა:",
    "AddTransactionButton": "ტრანზაქციის დამატება",
    "TransactionsGroup": "ტრანზაქციები",
    "TableHeaderDate": "თარიღი",
    "TableHeaderType": "ტიპი",
    "TableHeaderDescription": "აღწერა",
    "TableHeaderAmount": "თანხა",
    "TableHeaderAction": "მოქმედება",
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
    "EmptyDescriptionError": "აღწერა არ შეიძლება იყოს ცარიელი.",
    "ZeroAmountError": "თანხა უნდა იყოს ნულზე მეტი.",
    "TableActionCellText": "წასაშლელად მარჯვენა კლიკი",
    "TableActionCellTooltip": "ოფციებისთვის მარჯვენა კლიკი",
    "DataLoadErrorTitle": "მონაცემების ჩატვირთვის შეცდომა",
    "DataLoadErrorMsg": "{file} ფაილიდან მონაცემების ჩატვირთვა ვერ მოხერხდა. ფაილი შესაძლოა დაზიანებული იყოს. ვიწყებთ თავიდან.",
    "UnexpectedLoadErrorMsg": "მონაცემების ჩატვირთვისას მოხდა მოულოდნელი შეცდომა: {error}",
    "SaveErrorMsg": "{file} ფაილში მონაცემების შენახვა ვერ მოხერხდა: {error}",
    "NoDataToExportTitle": "მონაცემები არ არის",
    "NoDataToExportMsg": "საექსპორტო ტრანზაქციები არ არსებობს.",
    "SavePDFDialogTitle": "PDF რეპორტის შენახვა",
    "PDFFilesFilter": "PDF ფაილები (*.pdf)",
    "PDFReportTitle": "ბიუჯეტის ანგარიში",
    "PDFReportGeneratedOn": "ანგარიში გენერირებულია: {datetime}",
    "PDFTotalIncome": "სულ შემოსავალი: {currency_symbol}{amount:.2f}",
    "PDFTotalExpenses": "სულ ხარჯები: {currency_symbol}{amount:.2f}",
    "PDFFinalBalance": "საბოლოო ბალანსი: {currency_symbol}{amount:.2f}",
    "ExportSuccessTitle": "ექსპორტი წარმატებულია",
    "ExportSuccessMsg": "რეპორტი შენახულია აქ: {path}",
    "ExportErrorTitle": "ექსპორტის შეცდომა",
    "ExportErrorMsg": "PDF-ის გენერირება ვერ მოხერხდა: {error}",
    "CurrencySymbol": "₾"
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
        self.setFixedSize(350, 250) # Adjusted for potentially longer Georgian text

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
        self.setWindowTitle(T["MainWindowTitle"].format(username=username))
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

        title_label = QLabel(T["MainTitleLabel"])
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

        input_group = QGroupBox(T["AddTransactionGroup"])
        input_layout = QGridLayout(input_group)

        input_layout.addWidget(QLabel(T["TypeLabel"]), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems([TYPE_INTERNAL_TO_DISPLAY[INTERNAL_TYPE_EXPENSE], TYPE_INTERNAL_TO_DISPLAY[INTERNAL_TYPE_INCOME]])
        input_layout.addWidget(self.type_combo, 0, 1)

        input_layout.addWidget(QLabel(T["DateLabel"]), 0, 2)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        input_layout.addWidget(self.date_edit, 0, 3)

        input_layout.addWidget(QLabel(T["DescriptionLabel"]), 1, 0)
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText(T["DescriptionPlaceholder"])
        input_layout.addWidget(self.desc_input, 1, 1, 1, 3)

        input_layout.addWidget(QLabel(T["AmountLabel"]), 2, 0)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1000000.00)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix(T["CurrencySymbol"] + " ")
        input_layout.addWidget(self.amount_input, 2, 1)

        self.add_button = QPushButton(T["AddTransactionButton"])
        self.add_button.setObjectName("successButton")
        self.add_button.clicked.connect(self.add_transaction)
        input_layout.addWidget(self.add_button, 2, 2, 1, 2)

        input_layout.setColumnStretch(1, 2)
        input_layout.setColumnStretch(3, 1)
        grid_layout.addWidget(input_group, 0, 0, 1, 2)

        table_group = QGroupBox(T["TransactionsGroup"])
        table_layout = QVBoxLayout(table_group)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            T["TableHeaderDate"], T["TableHeaderType"], T["TableHeaderDescription"],
            T["TableHeaderAmount"], T["TableHeaderAction"]
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(2, 350)
        table_layout.addWidget(self.table)
        grid_layout.addWidget(table_group, 1, 0)

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
        grid_layout.addWidget(summary_actions_group, 1, 1)

        grid_layout.setColumnStretch(0, 3)
        grid_layout.setColumnStretch(1, 1)

        info_label = QLabel(T["DeleteHintLabel"])
        info_label.setObjectName("infoLabel")
        main_layout.addWidget(info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)

    def show_table_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return
        row = item.row()

        menu = QMenu(self.table)
        delete_action = QAction(T["DeleteActionText"], self)
        delete_action.triggered.connect(lambda: self.delete_transaction(row))
        menu.addAction(delete_action)
        menu.exec(self.table.mapToGlobal(pos))

    def delete_transaction(self, row_index):
        if not (0 <= row_index < len(self.transactions)):
            QMessageBox.warning(self, T["ErrorMsg"], T["InvalidTransactionDelete"])
            return

        transaction_desc = self.transactions[row_index]['description']
        reply = QMessageBox.question(self, T["ConfirmDeleteTitle"],
                                     T["ConfirmDeleteMsg"].format(description=transaction_desc),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self.transactions[row_index]
            self.save_data()
            self.update_table()
            self.update_summary()

    def add_transaction(self):
        ttype_display = self.type_combo.currentText()
        ttype_internal = TYPE_DISPLAY_TO_INTERNAL[ttype_display]
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        desc = self.desc_input.text().strip()
        amount = self.amount_input.value()

        if not desc:
            QMessageBox.warning(self, T["InputErrorTitle"], T["EmptyDescriptionError"])
            return
        if amount <= 0:
            QMessageBox.warning(self, T["InputErrorTitle"], T["ZeroAmountError"])
            return

        transaction = {
            "date": date_str,
            "type": ttype_internal,
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
            
            display_type = TYPE_INTERNAL_TO_DISPLAY[t["type"]]
            type_item = QTableWidgetItem(display_type)
            if t["type"] == INTERNAL_TYPE_INCOME:
                type_item.setForeground(QColor("green"))
            else:
                type_item.setForeground(QColor("red"))
            self.table.setItem(i, 1, type_item)
            
            self.table.setItem(i, 2, QTableWidgetItem(t["description"]))
            
            amount_item = QTableWidgetItem(f"{T['CurrencySymbol']}{t['amount']:.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 3, amount_item)

            action_item = QTableWidgetItem(T["TableActionCellText"])
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            action_item.setToolTip(T["TableActionCellTooltip"])
            self.table.setItem(i, 4, action_item)

    def update_summary(self):
        total_income = sum(t["amount"] for t in self.transactions if t["type"] == INTERNAL_TYPE_INCOME)
        total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == INTERNAL_TYPE_EXPENSE)
        balance = total_income - total_expenses

        self.total_income_label.setText(f"{T['CurrencySymbol']}{total_income:.2f}")
        self.total_expenses_label.setText(f"{T['CurrencySymbol']}{total_expenses:.2f}")
        self.balance_label.setText(f"{T['CurrencySymbol']}{balance:.2f}")

        if balance >= 0:
            self.balance_label.setObjectName("balanceLabelPositive")
        else:
            self.balance_label.setObjectName("balanceLabelNegative")
        self.balance_label.setStyleSheet(STYLESHEET)

    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.transactions = json.load(f)
                    self.transactions.sort(key=lambda x: x["date"], reverse=True)
        except json.JSONDecodeError:
            self.transactions = []
            QMessageBox.warning(self, T["DataLoadErrorTitle"], T["DataLoadErrorMsg"].format(file=DATA_FILE))
        except Exception as e:
            self.transactions = []
            QMessageBox.critical(self, T["ErrorMsg"], T["UnexpectedLoadErrorMsg"].format(error=e))

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.transactions, f, indent=4, ensure_ascii=False)
        except Exception as e:
             QMessageBox.critical(self, T["ErrorMsg"], T["SaveErrorMsg"].format(file=DATA_FILE, error=e))

    def export_to_pdf(self):
        if not self.transactions:
            QMessageBox.information(self, T["NoDataToExportTitle"], T["NoDataToExportMsg"])
            return

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.pdfbase import pdfmetrics
            
            # Attempt to register a common Georgian font if available (e.g., Sylfaen)
            # This path might need adjustment based on where the font is on the system
            # For a truly portable solution, bundle the font with the app.
            try:
                pdfmetrics.registerFont(TTFont('Sylfaen', 'Sylfaen.ttf')) # Common Georgian font
                georgian_font_name = 'Sylfaen'
            except: # Fallback if Sylfaen is not found or pdfmetrics fails
                georgian_font_name = 'Helvetica' # Fallback, may not render Georgian well

            path, _ = QFileDialog.getSaveFileName(self, T["SavePDFDialogTitle"], "", T["PDFFilesFilter"])
            if not path:
                return

            doc = SimpleDocTemplate(path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create styles with Georgian font
            styles.add(ParagraphStyle(name='GeorgianNormal', fontName=georgian_font_name, fontSize=10, parent=styles['Normal']))
            styles.add(ParagraphStyle(name='GeorgianH1', fontName=georgian_font_name, fontSize=18, parent=styles['h1']))
            styles.add(ParagraphStyle(name='GeorgianH3', fontName=georgian_font_name, fontSize=12, parent=styles['h3']))


            story = []

            story.append(Paragraph(T["PDFReportTitle"], styles['GeorgianH1']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(T["PDFReportGeneratedOn"].format(datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), styles['GeorgianNormal']))
            story.append(Spacer(1, 24))

            total_income = sum(t["amount"] for t in self.transactions if t["type"] == INTERNAL_TYPE_INCOME)
            total_expenses = sum(t["amount"] for t in self.transactions if t["type"] == INTERNAL_TYPE_EXPENSE)
            balance = total_income - total_expenses

            story.append(Paragraph(T["PDFTotalIncome"].format(currency_symbol=T["CurrencySymbol"], amount=total_income), styles['GeorgianH3']))
            story.append(Paragraph(T["PDFTotalExpenses"].format(currency_symbol=T["CurrencySymbol"], amount=total_expenses), styles['GeorgianH3']))
            story.append(Paragraph(T["PDFFinalBalance"].format(currency_symbol=T["CurrencySymbol"], amount=balance), styles['GeorgianH3']))
            story.append(Spacer(1, 24))
            
            # Data for table with Georgian font for header
            header_style = ParagraphStyle(name='GeorgianTableHeader', fontName=georgian_font_name, fontSize=10, alignment=1, parent=styles['Normal'])
            
            data = [[
                Paragraph(T["TableHeaderDate"], header_style),
                Paragraph(T["TableHeaderType"], header_style),
                Paragraph(T["TableHeaderDescription"], header_style),
                Paragraph(T["TableHeaderAmount"], header_style)
            ]]
            
            # Cell style for Georgian text in table
            cell_style_georgian = ParagraphStyle(name='GeorgianCell', fontName=georgian_font_name, fontSize=9, parent=styles['Normal'])
            cell_style_amount = ParagraphStyle(name='GeorgianAmountCell', fontName=georgian_font_name, fontSize=9, alignment=2, parent=styles['Normal']) # Right align for amount

            for t in sorted(self.transactions, key=lambda x: x["date"]):
                data.append([
                    Paragraph(t["date"], cell_style_georgian),
                    Paragraph(TYPE_INTERNAL_TO_DISPLAY[t["type"]], cell_style_georgian),
                    Paragraph(t["description"], cell_style_georgian),
                    Paragraph(f"{T['CurrencySymbol']}{t['amount']:.2f}", cell_style_amount)
                ])

            table = Table(data, colWidths=[70, 70, 280, 70])
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'), # Alignment for Paragraphs inside headers
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), georgian_font_name), # Ensure header font if not handled by Paragraph style
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'), # Alignment for amount column data if not handled by Paragraph
            ])
            table.setStyle(table_style)
            story.append(table)

            doc.build(story)
            QMessageBox.information(self, T["ExportSuccessTitle"], T["ExportSuccessMsg"].format(path=path))
        except ImportError:
             QMessageBox.critical(self, T["ExportErrorTitle"], "ReportLab ბიბლიოთეკა არ არის დაყენებული. გთხოვთ დააყენოთ PDF ექსპორტისთვის.")
        except Exception as e:
            QMessageBox.critical(self, T["ExportErrorTitle"], T["ExportErrorMsg"].format(error=e))


    def closeEvent(self, event):
        self.save_data()
        event.accept()


def main():
    app = QApplication(sys.argv)
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