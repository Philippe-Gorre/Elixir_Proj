from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QTimer, QDateTime
import sys


# ── LOGIN WINDOW ─────────────────────────────────────────────────
class LoginWindow:
    def __init__(self):
        loader = QUiLoader()
        file = QFile("logintab.ui")
        file.open(QIODevice.OpenModeFlag.ReadOnly)
        self.ui = loader.load(file)
        file.close()

        self.ui.login_button.clicked.connect(self.login)
        self.ui.cancel_button.clicked.connect(self.cancel)
        self.ui.user_line.clear()
        self.ui.pass_line.clear()
        self.ui.user_line.setPlaceholderText("Enter username")
        self.ui.pass_line.setPlaceholderText("Enter password")

    def login(self):
        username = self.ui.user_line.text()
        password = self.ui.pass_line.text()
        if username == "admin" and password == "admin123":
            self.ui.close()
            self.main_window = ElixirApp()
            self.main_window.showMaximized()
        else:
            QMessageBox.warning(self.ui, "Login Failed", "Invalid username or password!")
            self.ui.pass_line.clear()

    def cancel(self):
        self.ui.close()
        sys.exit()

    def show(self):
        self.ui.show()


# ── MAIN ELIXIR WINDOW ───────────────────────────────────────────
class ElixirApp(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile("elixir.ui")
        file.open(QIODevice.OpenModeFlag.ReadOnly)
        self.ui = loader.load(file)
        file.close()
        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("Elixir Clinical Manager")

        # ── Live Clock ───────────────────────────────────────────
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

        # ── Top Buttons ──────────────────────────────────────────
        self.ui.payment_button.clicked.connect(self.open_payment)
        self.ui.appointment_button.clicked.connect(self.open_new_appointment)

        # ── Setup Tables ─────────────────────────────────────────
        self.setup_schedule_table()
        self.setup_appointment_table()
        self.setup_patients_table()
        self.setup_revenue_table()
        self.setup_patient_history_table()

        # ── Search Connections ───────────────────────────────────
        self.ui.patient_line.textChanged.connect(self.search_patients)
        self.ui.lineEdit.textChanged.connect(self.search_revenue)
        self.ui.pat_his_line.textChanged.connect(self.search_patient_history)

        # ── Services Buttons ─────────────────────────────────────
        self.ui.services_button1.clicked.connect(lambda: self.filter_services("Services"))
        self.ui.services_button2.clicked.connect(lambda: self.filter_services("Packages"))
        self.ui.services_button3.clicked.connect(self.new_package)

        # ── Dashboard Counts ─────────────────────────────────────
        self.update_dashboard_counts()

    # ── RESIZE EVENT — Makes all widgets adjust to window size ───
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cw = self.centralWidget().width()
        ch = self.centralWidget().height()

        # ── Top bar ──────────────────────────────────────────────
        self.ui.main_box.setGeometry(-10, -10, cw + 20, 101)
        self.ui.payment_button.setGeometry(cw - 360, 30, 171, 51)
        self.ui.appointment_button.setGeometry(cw - 180, 30, 171, 51)

        # ── Tab widget fills remaining space ─────────────────────
        self.ui.pat_email_label.setGeometry(0, 90, cw, ch - 90)

        tab_w = cw - 10
        tab_h = ch - 135

        # ── Dashboard Tab ─────────────────────────────────────────
        box_w = 211
        box_h = 121
        spacing = (cw - 4 * box_w) // 5
        self.ui.appointment_box.setGeometry(spacing, 10, box_w, box_h)
        self.ui.patient_box.setGeometry(spacing * 2 + box_w, 10, box_w, box_h)
        self.ui.wait_box.setGeometry(spacing * 3 + box_w * 2, 10, box_w, box_h)
        self.ui.check_in_box.setGeometry(spacing * 4 + box_w * 3, 10, box_w, box_h)
        self.ui.schedule_label.setGeometry(20, 145, 231, 41)
        self.ui.schedule_tablewidget.setGeometry(0, 200, tab_w, tab_h - 200)

        # ── Appointment Tab ───────────────────────────────────────
        self.ui.appointment_tablewidget.setGeometry(0, 100, tab_w, tab_h - 100)

        # ── Revenue Tab ───────────────────────────────────────────
        self.ui.tableWidget_4.setGeometry(0, 250, tab_w, tab_h - 250)
        self.ui.lineEdit.setGeometry(10, 200, 211, 41)

        # ── Patients Tab ──────────────────────────────────────────
        self.ui.tableWidget.setGeometry(10, 100, tab_w, tab_h - 100)
        self.ui.patient_line.setGeometry(cw - 320, 45, 301, 41)

        # ── Services Tab ─────────────────────────────────────────
        self.ui.services_button3.setGeometry(cw - 160, 30, 131, 51)

        # ── Patient History Tab ───────────────────────────────────
        right_w = tab_w - 310
        self.ui.pat_his_tablewidget.setGeometry(10, 110, 256, tab_h - 120)
        self.ui.pat_his_box.setGeometry(300, 20, right_w, 201)
        self.ui.pat_appt_tablewidget.setGeometry(300, 241, right_w, 201)
        self.ui.tableWidget_10.setGeometry(300, 470, right_w, tab_h - 470)

    # ── CLOCK ────────────────────────────────────────────────────
    def update_clock(self):
        self.ui.dateTimeEdit.setDateTime(QDateTime.currentDateTime())

    # ── TOP BUTTONS ──────────────────────────────────────────────
    def open_payment(self):
        QMessageBox.information(self.ui, "Payment", "Opening Payment Window...")

    def open_new_appointment(self):
        QMessageBox.information(self.ui, "New Appointment", "Opening New Appointment Window...")

    # ── DASHBOARD ────────────────────────────────────────────────
    def update_dashboard_counts(self):
        self.ui.today_count.setText("5")
        self.ui.active_count.setText("12")
        self.ui.wait_time_count.setText("15")
        self.ui.check_in_count.setText("8")

    def setup_schedule_table(self):
        table = self.ui.schedule_tablewidget
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["No.", "Patient", "Time", "Doctor", "Status"])
        table.horizontalHeader().setStretchLastSection(True)

    def setup_appointment_table(self):
        table = self.ui.appointment_tablewidget
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["No.", "Patient", "Date", "Time", "Doctor", "Status"])
        table.horizontalHeader().setStretchLastSection(True)

    def setup_patients_table(self):
        table = self.ui.tableWidget
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["No.", "Name", "Phone", "Email", "Last Visit"])
        table.horizontalHeader().setStretchLastSection(True)
        self.ui.patien_count.setText("0")

    def setup_revenue_table(self):
        table = self.ui.tableWidget
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Invoice #", "Patient", "Service", "Amount", "Status"])
        table.horizontalHeader().setStretchLastSection(True)
        self.ui.total_count.setText("₱0.00")
        self.ui.pending_count.setText("₱0.00")
        self.ui.overdue_count.setText("₱0.00")

    def setup_patient_history_table(self):
        table = self.ui.pat_his_tablewidget
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["ID", "Name"])
        table.horizontalHeader().setStretchLastSection(True)
        table.itemClicked.connect(self.show_patient_info)

        appt_table = self.ui.pat_appt_tablewidget
        appt_table.setColumnCount(4)
        appt_table.setHorizontalHeaderLabels(["Date", "Service", "Doctor", "Status"])
        appt_table.horizontalHeader().setStretchLastSection(True)

        pkg_table = self.ui.tableWidget_10
        pkg_table.setColumnCount(3)
        pkg_table.setHorizontalHeaderLabels(["Package", "Date", "Amount"])
        pkg_table.horizontalHeader().setStretchLastSection(True)

    def show_patient_info(self, item):
        row = item.row()
        table = self.ui.pat_his_tablewidget
        name = table.item(row, 1).text() if table.item(row, 1) else ""
        self.ui.pat_name.setText(name)
        self.ui.pat_phone.setText("—")
        self.ui.pat_email.setText("—")
        self.ui.pat_visit.setText("—")

    def search_patients(self, text):
        self.search_table(self.ui.tableWidget, text)

    def search_revenue(self, text):
        self.search_table(self.ui.tableWidget_4, text)

    def search_patient_history(self, text):
        self.search_table(self.ui.pat_his_tablewidget, text)

    def filter_services(self, category):
        if category == "Services":
            self.ui.services_button1.setStyleSheet("background-color: black; color: white;")
            self.ui.services_button2.setStyleSheet("")
        else:
            self.ui.services_button2.setStyleSheet("background-color: black; color: white;")
            self.ui.services_button1.setStyleSheet("")

    def new_package(self):
        QMessageBox.information(self.ui, "New Package", "Opening New Package Window...")

    # ── HELPERS ──────────────────────────────────────────────────
    def populate_table(self, table, data):
        table.setRowCount(0)
        for row_data in data:
            row = table.rowCount()
            table.insertRow(row)
            for col, value in enumerate(row_data):
                table.setItem(row, col, QTableWidgetItem(value))

    def search_table(self, table, text):
        for row in range(table.rowCount()):
            match = False
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            table.setRowHidden(row, not match)


# ── RUN ──────────────────────────────────────────────────────────
app = QApplication(sys.argv)
login = LoginWindow()
login.show()
sys.exit(app.exec())
