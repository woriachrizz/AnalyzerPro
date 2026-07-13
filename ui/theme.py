DARK_THEME = """
/* ===========================
   Main Window
=========================== */

QMainWindow {
    background-color: #1E1E2E;
}

/* ===========================
   Widgets
=========================== */

QWidget {
    background-color: #1E1E2E;
    color: white;
    font-family: Segoe UI;
    font-size: 10pt;
}

/* ===========================
   Cards
=========================== */

QFrame#card {
    background-color: #2A2D3E;
    border: 1px solid #3A3D4E;
    border-radius: 10px;
}

/* ===========================
   Labels
=========================== */

QLabel#title {
    font-size: 24px;
    font-weight: bold;
}

QLabel#value {
    font-size: 30px;
    font-weight: bold;
    color: #00E676;
}

QLabel#status_connected {
    color: #00E676;
    font-weight: bold;
}

QLabel#status_disconnected {
    color: #FF5252;
    font-weight: bold;
}

/* ===========================
   Combo Boxes
=========================== */

QComboBox {
    background-color: #2A2D3E;
    border: 1px solid #555;
    border-radius: 6px;
    padding: 6px;
}

QComboBox:hover {
    border: 1px solid #00BCD4;
}

/* ===========================
   Tables
=========================== */

QTableWidget {
    background-color: #2A2D3E;
    border: 1px solid #3A3D4E;
    gridline-color: #3A3D4E;
    selection-background-color: #009688;
}

QHeaderView::section {
    background-color: #33384D;
    color: white;
    padding: 6px;
    border: none;
}

/* ===========================
   Scrollbars
=========================== */

QScrollBar:vertical {
    width: 10px;
    background: #1E1E2E;
}

QScrollBar::handle:vertical {
    background: #555;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #00BCD4;
}
"""