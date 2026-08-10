from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QHeaderView


class FrequencyTable(QTableWidget):

    def __init__(self):
        super().__init__()

        self.setColumnCount(7)

        self.setHorizontalHeaderLabels([
            "Digit",
            "Count",
            "%",
            "Gap",
            "Max Gap",
            "Avg Gap",
            "Status"
        ])

        self.setRowCount(10)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.verticalHeader().setVisible(False)

        for digit in range(10):

            self.setItem(digit, 0, QTableWidgetItem(str(digit)))
            self.setItem(digit, 1, QTableWidgetItem("0"))
            self.setItem(digit, 2, QTableWidgetItem("0.00"))
            self.setItem(digit, 3, QTableWidgetItem("0"))
            self.setItem(digit, 4, QTableWidgetItem("0"))
            self.setItem(digit, 5, QTableWidgetItem("0"))
            self.setItem(digit, 6, QTableWidgetItem("Normal"))

    def update_table(self, rows):

        for row in rows:

            digit = row["digit"]

            self.item(digit, 1).setText(str(row["count"]))
            self.item(digit, 2).setText(f'{row["percent"]:.2f}')
            self.item(digit, 3).setText(str(row["gap"]))
            self.item(digit, 4).setText(str(row["max_gap"]))
            self.item(digit, 5).setText(str(row["avg_gap"]))

            if row["gap"] > row["avg_gap"] * 2 and row["avg_gap"] > 0:
                status = "Cold"
            elif row["percent"] > 12:
                status = "Hot"
            else:
                status = "Normal"

            self.item(digit, 6).setText(status)