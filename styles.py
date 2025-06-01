# styles.py
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

/* Specific button styles */
QPushButton#dangerButton { /* Example if you wanted a specific danger button */
    background-color: #d9534f; /* Red for danger/delete */
}
QPushButton#dangerButton:hover {
    background-color: #c9302c;
}
QPushButton#dangerButton:pressed {
    background-color: #ac2925;
}

QPushButton#successButton { /* Used for the "Add Transaction" button */
    background-color: #5cb85c; /* Green for success/add */
}
QPushButton#successButton:hover {
    background-color: #4cae4c;
}
QPushButton#successButton:pressed {
    background-color: #449d44;
}


QTableWidget {
    border: 1px solid #e0e0e0;
    gridline-color: #e0e0e0; /* Lighter grid lines */
    background-color: #ffffff;
    alternate-background-color: #f9f9f9; /* Zebra striping */
    selection-background-color: #a6d8ff; /* Light blue selection */
    selection-color: #000000; /* Text color when selected */
}

QTableWidget::item {
    padding: 5px; /* Padding within each cell */
}

QHeaderView::section {
    background-color: #e9ecef; /* Light grey for headers */
    padding: 6px;
    border: 1px solid #d0d0d0;
    font-weight: bold;
}

/* --- CORRECTED QGroupBox STYLING --- */
QGroupBox {
    font-weight: bold; /* Applies to the title by default */
    border: 1px solid #d0d0d0;
    border-radius: 5px;
    margin-top: 25px;  /* This is the height of the area where the title will be drawn.
                          The content of the QGroupBox will start BELOW this margin.
                          Adjust this value if your font size or title padding changes significantly.
                          (Approx. title height + a little extra space) */
    padding-top: 8px;  /* This adds space INSIDE the groupbox, below the title area
                          and above the actual content widgets. This pushes the content down. */
    background-color: #fafafa; /* Slightly off-white groupbox background */
}

QGroupBox::title {
    subcontrol-origin: margin; /* The title is placed in the margin area of the QGroupBox. */
    subcontrol-position: top left; /* Specifically, at the top-left of this margin area. */
    left: 10px;          /* Small horizontal offset for aesthetics from the left edge. */
    /* The 'top' property for subcontrol-position is relative to the margin area itself.
       If margin-top is 25px, the title element (which is roughly 25px high due to its
       own font and padding) will fit within this. */

    padding: 5px 10px;   /* Padding *around* the text of the title itself.
                            This contributes to the overall height of the title element.
                            Approx title height = 5px (top pad) + 11pt font (~15px) + 5px (bottom pad) = ~25px.
                            This should fit within the QGroupBox's margin-top of 25px. */
    background-color: #e9ecef; /* Match header style */
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border-bottom: 1px solid #d0d0d0; /* Line below the title */
    color: #333; /* Ensure title text color, overriding general QWidget if needed */
}
/* --- END QGroupBox STYLING CORRECTION --- */

QLabel#titleLabel { /* For the main application title "My Personal Budget" */
    font-size: 18pt;
    font-weight: bold;
    color: #005a9e; /* Darker blue for titles */
    padding-bottom: 10px; /* Space below the main title */
}

QLabel#balanceLabelPositive { /* For the balance label when positive */
    font-size: 14pt;
    font-weight: bold;
    color: #28a745; /* Green for positive balance */
}

QLabel#balanceLabelNegative { /* For the balance label when negative */
    font-size: 14pt;
    font-weight: bold;
    color: #dc3545; /* Red for negative balance */
}

QLabel#infoLabel { /* For the tip label at the bottom */
    font-style: italic;
    color: #666; /* Lighter grey for less emphasis */
    padding-top: 5px; /* A bit of space above it */
}

/* Styles for QMenu (Context Menu) - Optional, but can improve consistency */
QMenu {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    padding: 5px; /* Padding around menu items */
}

QMenu::item {
    padding: 5px 20px 5px 20px; /* Top, Right, Bottom, Left padding for menu items */
    border-radius: 3px; /* Slight rounding for items */
}

QMenu::item:selected {
    background-color: #0078d7; /* Blue selection, matches button */
    color: white;
}

QMenu::separator {
    height: 1px;
    background: #e0e0e0;
    margin-left: 10px;
    margin-right: 10px;
}
"""