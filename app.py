from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QTimer, QDateTime, QDate
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ui_path(filename):
    return os.path.join(BASE_DIR, filename)


# ── LOGIN WINDOW ─────────────────────────────────────────────────
class LoginWindow:
    def __init__(self):
        loader = QUiLoader()
        file = QFile(ui_path("logintab.ui"))
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


# ── APPOINTMENT WINDOW ───────────────────────────────────────────
# ── APPOINTMENT WINDOW (FIXED) ───────────────────────────────────
class AppointmentWindow:
    def __init__(self, on_booked_callback=None):
        self.on_booked_callback = on_booked_callback

        loader = QUiLoader()
        path = ui_path("appointment_tab.ui")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Could not find: {path}")

        file = QFile(path)
        if not file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise RuntimeError(f"Cannot open UI file: {file.errorString()}")

        # FIX: Pass the file to loader, and optionally specify None for the parent
        # Sometimes QUiLoader needs the file to be clearly readable as a device
        self.ui = loader.load(file, None)
        file.close()

        if not self.ui:
            raise RuntimeError("QUiLoader failed to load the UI object.")

        # Widget names match appointment_tab.ui exactly
        self.ui.setWindowTitle("New Appointment")
        self.ui.calendar.setMinimumDate(QDate.currentDate())

        # .ui name: services_label  (QComboBox)
        self.ui.services_label.addItems([
            "-- Select Service/Package --",
            "Basic Facial",
            "Deep Cleanse Facial",
            "Body Scrub",
            "Relaxation Massage",
            "Premium Package",
        ])

        # .ui names: pat_name, pat_email, pat_phone  (QLineEdit)
        self.ui.pat_name.setPlaceholderText("Full name")
        self.ui.pat_email.setPlaceholderText("email@example.com")
        self.ui.pat_phone.setPlaceholderText("09xxxxxxxxx")

        # .ui name: time_label  (QTimeEdit — no placeholder, uses display format)
        from PySide6.QtCore import QTime
        self.ui.time_label.setDisplayFormat("hh:mm AP")
        self.ui.time_label.setTime(QTime(9, 0))

        # .ui name: note_label  (QPlainTextEdit)
        self.ui.note_label.setPlaceholderText("Reason for visit, special instructions…")

        # .ui name: appoint_button  (QPushButton)
        self.ui.appoint_button.clicked.connect(self.book_appointment)

    def book_appointment(self):
        name    = self.ui.pat_name.text().strip()
        email   = self.ui.pat_email.text().strip()
        phone   = self.ui.pat_phone.text().strip()
        service = self.ui.services_label.currentText()
        date    = self.ui.calendar.selectedDate().toString("MMMM d, yyyy")
        time    = self.ui.time_label.time().toString("hh:mm AP")
        notes   = self.ui.note_label.toPlainText().strip()

        if not name:
            QMessageBox.warning(self.ui, "Missing Field", "Please enter the client name.")
            return
        if service == "-- Select Service/Package --":
            QMessageBox.warning(self.ui, "Missing Field", "Please select a service or package.")
            return

        appointment_data = {
            "name":    name,
            "email":   email,
            "phone":   phone,
            "service": service,
            "date":    date,
            "time":    time,
            "notes":   notes,
        }

        if self.on_booked_callback:
            self.on_booked_callback(appointment_data)

        QMessageBox.information(
            self.ui,
            "Appointment Booked",
            f"Appointment for {name}\nDate: {date} at {time}\nService: {service}"
        )
        self.ui.close()

    def show(self):
        self.ui.show()
        self.ui.raise_()
        self.ui.activateWindow()

    def isVisible(self):
        return self.ui.isVisible()

    def reset_form(self):
        self.ui.pat_name.clear()
        self.ui.pat_email.clear()
        self.ui.pat_phone.clear()
        self.ui.services_label.setCurrentIndex(0)
        self.ui.calendar.setSelectedDate(QDate.currentDate())
        from PySide6.QtCore import QTime
        self.ui.time_label.setTime(QTime(9, 0))
        self.ui.note_label.clear()


# ── MAIN ELIXIR WINDOW ───────────────────────────────────────────
class ElixirApp(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile(ui_path("elixir.ui"))
        file.open(QIODevice.OpenModeFlag.ReadOnly)
        self.ui = loader.load(file)
        file.close()
        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("Elixir Clinical Manager")
        self.resize(self.ui.size())
        self.setFixedSize(1105, 800)
        self.setMinimumSize(1105, 800)
        self.setMaximumSize(1105, 800)

        self.appointment_window = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

        self.ui.payment_button.clicked.connect(self.open_payment)
        self.ui.appointment_button.clicked.connect(self.open_new_appointment)

        self.setup_schedule_table()
        self.setup_appointment_table()
        self.setup_patients_table()
        self.setup_revenue_table()
        self.setup_patient_history_table()

        self.ui.patient_line.textChanged.connect(self.search_patients)
        self.ui.lineEdit.textChanged.connect(self.search_revenue)
        self.ui.pat_his_line.textChanged.connect(self.search_patient_history)

        self.ui.services_button1.clicked.connect(lambda: self.filter_services("Services"))
        self.ui.services_button2.clicked.connect(lambda: self.filter_services("Packages"))
        self.ui.services_button3.clicked.connect(self.new_package)

        self.update_dashboard_counts()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cw = self.centralWidget().width()
        ch = self.centralWidget().height()

        self.ui.main_box.setGeometry(-10, -10, cw + 20, 101)
        self.ui.payment_button.setGeometry(cw - 360, 30, 171, 51)
        self.ui.appointment_button.setGeometry(cw - 180, 30, 171, 51)

        self.ui.pat_email_label.setGeometry(0, 90, cw, ch - 90)

        tab_w = cw - 10
        tab_h = ch - 135

        box_w = 211
        box_h = 121
        spacing = (cw - 4 * box_w) // 5
        self.ui.appointment_box.setGeometry(spacing, 10, box_w, box_h)
        self.ui.patient_box.setGeometry(spacing * 2 + box_w, 10, box_w, box_h)
        self.ui.wait_box.setGeometry(spacing * 3 + box_w * 2, 10, box_w, box_h)
        self.ui.check_in_box.setGeometry(spacing * 4 + box_w * 3, 10, box_w, box_h)
        self.ui.schedule_label.setGeometry(20, 145, 231, 41)
        self.ui.schedule_tablewidget.setGeometry(0, 200, tab_w, tab_h - 200)

        self.ui.appointment_tablewidget.setGeometry(0, 100, tab_w, tab_h - 100)

        # ── FIX: was tableWidget_4, correct name is appointment_tablewidget_2 ──
        self.ui.appointment_tablewidget_2.setGeometry(0, 250, tab_w, tab_h - 250)
        self.ui.lineEdit.setGeometry(10, 200, 211, 41)

        self.ui.tableWidget.setGeometry(10, 100, tab_w, tab_h - 100)
        self.ui.patient_line.setGeometry(cw - 320, 45, 301, 41)

        self.ui.services_button3.setGeometry(cw - 160, 30, 131, 51)

        right_w = tab_w - 310
        self.ui.pat_his_tablewidget.setGeometry(10, 110, 256, tab_h - 120)
        self.ui.pat_his_box.setGeometry(300, 20, right_w, 201)
        self.ui.pat_appt_tablewidget.setGeometry(300, 241, right_w, 201)
        self.ui.tableWidget_10.setGeometry(300, 470, right_w, tab_h - 470)

    def update_clock(self):
        self.ui.dateTimeEdit.setDateTime(QDateTime.currentDateTime())

    def open_payment(self):
        QMessageBox.information(self.ui, "Payment", "Opening Payment Window...")

    def open_new_appointment(self):
        if self.appointment_window is None or not self.appointment_window.isVisible():
            self.appointment_window = AppointmentWindow(
                on_booked_callback=self.on_appointment_booked
            )
            self.appointment_window.reset_form()
        self.appointment_window.show()

    def on_appointment_booked(self, data: dict):
        # ── Appointments tab table ───────────────────────────────
        appt_table = self.ui.appointment_tablewidget
        row = appt_table.rowCount()
        appt_table.insertRow(row)
        appt_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        appt_table.setItem(row, 1, QTableWidgetItem(data["name"]))
        appt_table.setItem(row, 2, QTableWidgetItem(data["date"]))
        appt_table.setItem(row, 3, QTableWidgetItem(data["time"]))
        appt_table.setItem(row, 4, QTableWidgetItem(data["service"]))
        appt_table.setItem(row, 5, QTableWidgetItem("Scheduled"))
        appt_table.setItem(row, 6, QTableWidgetItem(data["notes"]))

        # ── Schedule tab table ───────────────────────────────────
        sched_table = self.ui.schedule_tablewidget
        s_row = sched_table.rowCount()
        sched_table.insertRow(s_row)
        sched_table.setItem(s_row, 0, QTableWidgetItem(str(s_row + 1)))
        sched_table.setItem(s_row, 1, QTableWidgetItem(data["name"]))
        sched_table.setItem(s_row, 2, QTableWidgetItem(data["time"]))
        sched_table.setItem(s_row, 3, QTableWidgetItem(data["service"]))
        sched_table.setItem(s_row, 4, QTableWidgetItem("Scheduled"))

        # ── Update dashboard count ───────────────────────────────
        self.ui.today_count.setText(str(appt_table.rowCount()))

    def update_dashboard_counts(self):
        self.ui.today_count.setText("5")
        self.ui.active_count.setText("12")
        self.ui.wait_time_count.setText("15")
        self.ui.check_in_count.setText("8")

    def setup_schedule_table(self):
        table = self.ui.schedule_tablewidget
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["No.", "Patient", "Time", "Service", "Status"])
        table.horizontalHeader().setStretchLastSection(True)

    def setup_appointment_table(self):
        table = self.ui.appointment_tablewidget
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["No.", "Patient", "Date", "Time", "Service", "Status", "Notes"])
        table.horizontalHeader().setStretchLastSection(True)

    def setup_patients_table(self):
        table = self.ui.tableWidget
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["No.", "Name", "Phone", "Email", "Last Visit"])
        table.horizontalHeader().setStretchLastSection(True)
        self.ui.patien_count.setText("0")

    def setup_revenue_table(self):
        # ── FIX: was self.ui.tableWidget (patients table), correct is appointment_tablewidget_2 ──
        table = self.ui.appointment_tablewidget_2
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
        # ── FIX: was tableWidget_4, correct name is appointment_tablewidget_2 ──
        self.search_table(self.ui.appointment_tablewidget_2, text)

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