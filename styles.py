STYLESHEET = """
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif; /* A modern, common font */
    font-size: 11pt;
    color: #333; /* Dark grey text */
}

QMainWindow, QDialog {
    background-color: #f0f2f5; /* Light grey-blue background */
}

QLabel {
    color: #444; /* Slightly darker for labels */
}

QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
    padding: 8px;
    border: 1px solid #c0c0c0; /* Light grey border */
    border-radius: 5px;
    background-color: #ffffff; /* White background for inputs */
    min-height: 20px; /* Ensure consistent height */
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
    border: 1px solid #0078d7; /* Blue border on focus, like Office apps */
}

QPushButton {
    background-color: #0078d7; /* Primary blue */
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #005a9e; /* Darker blue on hover */
}

QPushButton:pressed {
    background-color: #004578; /* Even darker blue when pressed */
}

QPushButton#dangerButton { 
    background-color: #d9534f; 
}
QPushButton#dangerButton:hover {
    background-color: #c9302c;
}
QPushButton#dangerButton:pressed {
    background-color: #ac2925;
}

QPushButton#successButton { 
    background-color: #5cb85c; 
}
QPushButton#successButton:hover {
    background-color: #4cae4c;
}
QPushButton#successButton:pressed {
    background-color: #449d44;
}


QTableWidget {
    border: 1px solid #e0e0e0;
    gridline-color: #e0e0e0; 
    background-color: #ffffff;
    alternate-background-color: #f9f9f9; 
    selection-background-color: #a6d8ff; 
    selection-color: #000000; 
}

QTableWidget::item {
    padding: 5px; 
}

QHeaderView::section {
    background-color: #e9ecef; 
    padding: 6px;
    border: 1px solid #d0d0d0;
    font-weight: bold;
}

QGroupBox {
    font-weight: bold; 
    border: 1px solid #d0d0d0;
    border-radius: 5px;
    margin-top: 25px;  
    padding-top: 8px;  
    background-color: #fafafa; 
}

QGroupBox::title {
    subcontrol-origin: margin; 
    subcontrol-position: top left; 
    left: 10px;          
    padding: 5px 10px;   
    background-color: #e9ecef; 
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border-bottom: 1px solid #d0d0d0; 
    color: #333; 
}

QLabel#titleLabel { 
    font-size: 18pt;
    font-weight: bold;
    color: #005a9e; 
    padding-bottom: 10px; 
}

QLabel#balanceLabelPositive { 
    font-size: 14pt;
    font-weight: bold;
    color: #28a745; 
}

QLabel#balanceLabelNegative { 
    font-size: 14pt;
    font-weight: bold;
    color: #dc3545; 
}

QLabel#infoLabel { 
    font-style: italic;
    color: #666; 
    padding-top: 5px; 
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    padding: 5px; 
}

QMenu::item {
    padding: 5px 20px 5px 20px; 
    border-radius: 3px; 
}

QMenu::item:selected {
    background-color: #0078d7; 
    color: white;
}

QMenu::separator {
    height: 1px;
    background: #e0e0e0;
    margin-left: 10px;
    margin-right: 10px;
}
"""