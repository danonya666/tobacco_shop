import sys
from PyQt5 import QtGui, uic
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QMainWindow, QAction, QDialog, QDialogButtonBox, \
    QVBoxLayout, QGroupBox, QFormLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QInputDialog, QPushButton, QTextEdit, \
    QGridLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QIcon, QActionEvent

import dal


def all_shipments(dal):
    ships = dal.all_shipments()
    return ships


class FormWidget(QMainWindow):
    def __init__(self, parent, dal):
        super().__init__(parent)
        self.dal = dal
        central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет


        central_widget.layout = QGridLayout(self)

        grid_layout = QGridLayout()  # Создаём QGridLayout
        central_widget.setLayout(grid_layout)  # Устанавливаем данное размещение в центральный виджет

        ships = all_shipments(dal)
        lenn = len(ships)

        self.table = QTableWidget(self)  # Создаём таблицу
        self.table.setColumnCount(5)  # Устанавливаем три колонки
        self.table.setRowCount(lenn)  # и одну строку в таблице



        # Устанавливаем заголовки таблицы
        self.table.setHorizontalHeaderLabels(["key", "amount", "product", "logistic company", "subject company"])

        # Устанавливаем всплывающие подсказки на заголовки
        self.table.horizontalHeaderItem(0).setToolTip("Column 1 ")
        self.table.horizontalHeaderItem(1).setToolTip("Column 2 ")
        self.table.horizontalHeaderItem(2).setToolTip("Column 3 ")

        for i in range(lenn):
            print(ships)
            subj_name = str(dal.subj_name_from_key(ships[i][4])).strip("'[','(',',',')',']', '\''")
            logistic_name = str(dal.logistic_name_from_key(ships[i][3])).strip("'[','(',',',')',']', '\''")
            print(str(subj_name), str(logistic_name))
            # заполняем первую строку
            self.table.setItem(i, 0, QTableWidgetItem(str(ships[i][0])))
            self.table.setItem(i, 1, QTableWidgetItem(str(ships[i][1])))
            self.table.setItem(i, 2, QTableWidgetItem(str(ships[i][2])))
            self.table.setItem(i, 3, QTableWidgetItem(str(logistic_name)))
            self.table.setItem(i, 4, QTableWidgetItem(str(subj_name)))

        # делаем ресайз колонок по содержимому
        self.table.resizeColumnsToContents()

        grid_layout.addWidget(self.table, 0, 0)  # Добавляем таблицу в сетку


class AuthBase:
    def __init__(self):
        self.employees = []

    def login(self, newcomer):
        for employee in self.employees:
            if employee == newcomer:
                return employee.rights
        return None


class Employee:
    def __init__(self, nick, password, rights=None):
        """
        :param nick:
        :param password:
        :param rights: 1 = admin, 0 = manager, None - not authorized
        """
        self.nick = nick or None
        self.password = password or None
        self.rights = rights

    def __eq__(self, other):
        if self.nick == other.nick and self.password == other.password:
            return True
        else:
            return False

    def login(self, base):
        self.rights = base.login(self)


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.emp = Employee(None, None)
        self.children_windows = []
        self.dal = dal.PgDal()
        self.init_ui()

    def check_db(self, emp):
        logins = self.dal.select_logins()
        for man in logins:
            if man[1] == emp.nick and man[2] == emp.password:
                return 1 if man[3] else 0
        return None

    def showDialog(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog',
                                        'Enter your nickname:')

        text2, ok2 = QInputDialog.getText(self, 'Input Dialog',
                                          'Enter your password:')

        if ok and ok2:
            emp = Employee(text, text2)
            rights = self.check_db(emp)
            emp.rights = rights
            if rights is not None:
                role = 'manager' if not rights else 'administrator'
                formatted = f'Successful login! You are logged in as {role}'
                reply = QMessageBox.question(self, 'PyQt5 message', formatted, QMessageBox.Close)
                if reply == QMessageBox.Close:
                    print('Close')
            else:
                reply = QMessageBox.question(self, 'PyQt5 message', "Wrong login or password!", QMessageBox.Close)
            return emp
        return None

    def add_shipment_dialog(self):
        print(self.emp.rights)
        if not self.emp.rights:
            reply = QMessageBox.question(self, 'Bad', 'You are not logged in or do not have rights!',
                                         QMessageBox.Close)
        else:
            text, ok = QInputDialog.getText(self, 'Input Dialog',
                                            'Enter ammount:')

            text2, ok2 = QInputDialog.getText(self, 'Input Dialog',
                                              'Enter product name:')

            text3, ok3 = QInputDialog.getText(self, 'Input Dialog',
                                              'Enter logistics company name:')

            text4, ok4 = QInputDialog.getText(self, 'Input Dialog',
                                              'Enter subject company name:')

            print(str(text2), str(text3), str(text4))
            product_key = self.dal.product_key_from_name(str(text2))
            logistics_key = self.dal.logistics_key_from_name(str(text3))
            subj_key = self.dal.subject_key_from_name(str(text4))
            result = self.dal.add_shipment(text, product_key, logistics_key, subj_key)
            if result == 1:
                reply = QMessageBox.question(self, 'Successful adding', 'Shipment added!', QMessageBox.Close)
            # return [str(text), product_key, logistics_key, subj_key]
            else:
                reply = QMessageBox.question(self, 'Successful adding', 'Something went wrong! Check the data please', QMessageBox.Close)

    def init_ui(self):
        self.setGeometry(200, 300, 1000, 500)
        self.setWindowTitle('Tobacco Shop - Manager Panel')
        self.setWindowIcon(QIcon('icon.png'))
        self.init_menu()

        self.form_widget = FormWidget(self, self.dal)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.form_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)

        self.show()

    def init_menu(self):
        # self.statusBar() # I don't know, what is that
        # Creating top menu
        menu_bar = self.menuBar()

        # Everything that is inside Create menu button
        create_menu = menu_bar.addMenu('&Create')

        add_product_action = QAction('&Product', self)
        add_product_action.triggered.connect(self.add_product)
        create_menu.addAction(add_product_action)

        add_order_action = QAction('&Order', self)
        add_order_action.triggered.connect(self.add_order)
        create_menu.addAction(add_order_action)

        add_logistics_action = QAction('&Logistics Company', self)
        add_logistics_action.triggered.connect(self.add_logistics)
        create_menu.addAction(add_logistics_action)

        add_subject_action = QAction('&Subject Company', self)
        add_subject_action.triggered.connect(self.add_subject)
        create_menu.addAction(add_subject_action)

        # Everything that is inside Delete menu button
        delete_menu = menu_bar.addMenu('&Delete')

        delete_product_action = QAction('&Product', self)
        delete_product_action.triggered.connect(self.delete_product)
        delete_menu.addAction(delete_product_action)

        delete_order_action = QAction('&Order', self)
        delete_order_action.triggered.connect(self.delete_order)
        delete_menu.addAction(delete_order_action)

        delete_logistics_action = QAction('&Logistics Company', self)
        delete_logistics_action.triggered.connect(self.delete_logistics)
        delete_menu.addAction(delete_logistics_action)

        delete_subject_action = QAction('&Subject Company', self)
        delete_subject_action.triggered.connect(self.delete_subject)
        delete_menu.addAction(delete_subject_action)

        # Login button
        login_menu = menu_bar.addMenu('&Login')

        login_action = QAction('&Login', self)
        login_action.triggered.connect(self.login)
        login_menu.addAction(login_action)

    def add_product(self):
        print("Adding a product")

    def add_order(self):
        print("Adding an order")
        self.add_shipment_dialog()

    def add_logistics(self):
        print("Adding logistics")

    def add_subject(self):
        print("Adding subject")

    def delete_product(self):
        print("Deleting a product")

    def delete_order(self):
        print("Deleting an order")

    def delete_logistics(self):
        print("Deleting logistics")

    def delete_subject(self):
        print("Deleting subject")

    def login(self):
        print("Logging in")
        emp = self.showDialog()
        self.emp = emp
        return


"""
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure you want to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
