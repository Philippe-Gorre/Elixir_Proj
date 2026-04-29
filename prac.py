def add_numbers(data, data2):
    return data + data2

def full_name(first, last):
    return print(first + " " + last)

#number1 = int(input('input nubmer'))
#number2 = int(input('input nubmer'))

#print(add_numbers(number1, number2))


#first = input('First name')
#last = input('last name')

#full_name(first, last)

# numbers = [1,2,3,4,5]
# total = 0

# for num in numbers:
#     total = total + num
#     #or
#     total += num
#     total += num
#     total += num
#     total += num

# print(total)

# for i in range(10, 0, -1):   # 👈 third argument -1 = step down
#     print(i)


# for row in range(1,6):
#     for col in range(row):
#         print('*', end=" ")
#     print()    

total = 0
for i in range(4):
    for j in range(i):
        total = i * j

print(total)




numbers = [1,2,3,4,5] 
total =0

for num in numbers:
    total += num

print(total)   





#calendar Function

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCalendarWidget,
    QLabel, QPushButton
)
from PySide6.QtCore import QDate
import sys

class AppointmentForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Appointment")
        layout = QVBoxLayout(self)

        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setMinimumDate(QDate.currentDate())  # disable past dates
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)

        self.date_label = QLabel("Selected date: —")

        layout.addWidget(self.calendar)
        layout.addWidget(self.date_label)

    def on_date_selected(self, date: QDate):
        self.date_label.setText(f"Selected date: {date.toString('MMMM d, yyyy')}")

app = QApplication(sys.argv)
window = AppointmentForm()
window.show()
sys.exit(app.exec())