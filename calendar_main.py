# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui, uic
import time
import datetime
import pickle
import copy

"""This module provides main structure and function of program."""

__version__ = "0.1.0"
__author__ = 'Yunovidov Dmitriy: Dm.Yunovidov@gmail.com'

COLORS = ['#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0', '#f7f7f7', '#fddbc7', '#f4a582', '#d6604d', '#b2182b', '#67001f']
new_task = [
            '01.12.2000 12:00',
            'Опишите задачу',
            'Work',  # ['Work', 'Project', 'Home'],
            'No'  # ['No', 'Yes']
        ]
q_date_time_format = "dd.MM.yyyy HH:mm"


class MainWindow(QtWidgets.QMainWindow):
    test_tasks = None
    tasks_model = None

    def __init__(self):
        super(QtWidgets.QMainWindow, self).__init__()
        uic.loadUi("py_call.ui", self)

        self.setWindowTitle("Test calendar v.0")

        self.setCentralWidget(self.centralwidget)
        self.setMenuBar(self.menubar)

        # Configured calendar
        self.calendarWidget.setSelectedDate(QtCore.QDate.currentDate())
        self.first_date(QtCore.QDate.currentDate())

        # Configure lived progress bar
        self.pb_live.setRange(0, 100)
        self.pb_live.setFormat("time alive from 100 yo: " + str(live_and_prosper_calc()) + "%")

        # Configure tasks progress bar
        self.pb_tasks.setRange(0, 100)
        self.pb_tasks.setFormat("tasks solved: " + str(24) + "%")

        # Configured nix label with date and time
        self.l_nix.setPixmap(nix_date_time(all_width=self.calendarWidget.width()))
        # creating a timer object
        self.timer = QtCore.QTimer(self)

        # self.l_nix.setPixmap(nix_date_time(all_wight=630))
        def update_label():
            self.l_nix.setPixmap(nix_date_time(all_width=self.calendarWidget.width()))

        # adding action to timer
        self.timer.timeout.connect(update_label)
        # update the timer every 2 second
        self.timer.start(2000)

        self.calendarWidget.clicked.connect(lambda x: self.click_data(x))

        self.pb_task_add.clicked.connect(self.task_add)

        self.pb_save.clicked.connect(self.close)

        # Show program
        self.show()

    def task_add(self):
        print('Plus clicked')

        self.tasks_model.insertRow(0, 1, self.calendarWidget.selectedDate())
        # self.tasks_model.headerdata[1].append(self.calendarWidget.selectedDate())
        self.tv_tasks.update()

    def click_data(self, date):
        # Slot for clicked data. Change task list for clicked date

        # print(self.tasks_model.headerdata)

        all_data_indexes = []

        if self.tasks_model.arraydata:
            for ind_k in range(len(self.tasks_model.headerdata[1])):
                k = self.tasks_model.headerdata[1][ind_k]
                if k > date:
                    all_data_indexes.append(ind_k)
        else:
            pass

        if all_data_indexes:
            self.tasks_model.hideRow(all_data_indexes)
            self.tv_tasks.update()
        else:
            self.tasks_model.revert()
            self.tv_tasks.update()

    def first_date(self, date):
        try:
            db_tasks_temp = pickle.load(open("dimyun.pickle", "rb"))
        except (OSError, IOError) as e:
            db_tasks_temp = {
                QtCore.QDate(2020, 10, 11): new_task
            }

        self.tv_tasks.setModel(TaskTableModel(db_in=db_tasks_temp))
        # self.tv_tasks.setSortingEnabled(True)
        # self.tv_tasks.model().set_task_widgets(self.tv_tasks, 0)
        self.tv_tasks.resizeColumnsToContents()

    def closeEvent(self, event):
        self.save_exit()
        self.timer.stop()
        self.timer.deleteLater()
        self.deleteLater()
        event.accept()
        # else:
        #     event.ignore()

    def save_exit(self):
        result = QtWidgets.QMessageBox.question(
            self,
            self.tr('Close window'),
            self.tr('Save changes?'),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No
        )
        if result == QtWidgets.QMessageBox.Yes:
            self.save_data()
        else:
            pass

    def save_data(self):
        pickle.dump(self.tasks_model.db_tasks, open("dimyun.pickle", "wb"))


class TaskTableModel(QtCore.QAbstractTableModel):
    # class for tables model
    def __init__(self, db_in, parent=None, *args):
        """
        :param datain: a list of lists with data
        :param headerdata: a two list in list with headers data
        :param parent: parent class
        :param args: None
        """
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        # Build arraydata and headers from dict

        self.db_tasks = db_in
        headerdata = [
            ['Deadline', 'Task', 'Type', 'Is Close'],
            list(db_in.keys())
        ]
        datain = [db_in[k] for k in db_in]
        self.display_init(headerdata, datain)

    def display_init(self, headerdata, datain):
        self.arraydata = copy.deepcopy(datain)
        self.headerdata = copy.deepcopy(headerdata)
        self._arraydata = copy.deepcopy(datain)
        self._headerdata = copy.deepcopy(headerdata)

        # for ind_cccrow

        # self.db_to_save(action_type = 'init')

    def set_task_widgets(self, tv_table, row_index, row_deadline, row_work_type, row_is_closed):
        # self.tv_tasks.setItemDelegateForColumn(2, comboBoxDelegate(self.tv_tasks))

        all_add_widgets = []

        c = QtWidgets.QDateTimeEdit()
        c.setDisplayFormat(q_date_time_format)
        c.setDateTime(QtCore.QDateTime.fromString(new_task[0]))
        i = tv_table.model().index(row_index, 0)
        tv_table.setIndexWidget(i, c)
        all_add_widgets.append(c)

        for i in [2, 3]:
            c = QtWidgets.QComboBox()
            c.addItems(new_task[i])
            j = tv_table.model().index(row_index, i)
            tv_table.setIndexWidget(j, c)
            all_add_widgets.append(c)

        all_add_widgets[0].dateTimeChanged.connect(
            lambda x: tv_table.model().db_to_save(
                action='deadline_change',
                row_index=row_index,
                data=x
            )
        )
        all_add_widgets[1].currentIndexChanged.connect(
            lambda x: tv_table.model().db_to_save(
                action='work_type_change',
                row_index=row_index,
                data=new_task[2][x]
            )
        )
        all_add_widgets[2].currentIndexChanged.connect(
            lambda x: tv_table.model().db_to_save(
                action='is_closed',
                row_index=row_index,
                data=new_task[3][x]
            )
        )

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        if self.arraydata:
            return len(self.arraydata[0])
        else:
            return 0

    def flags(self, index):
        if index.column() == 3:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            return self.arraydata[row][column]

        if role == QtCore.Qt.ToolTipRole:
            # row = index.row()
            # column = index.column()
            return 'data for tasks'

        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if self.arraydata[row][3] == 'Yes':
                self.hideRow(row)
            else:
                value = self.arraydata[row][column]
                return value

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        print('Data is set', index, value, role, index.column())
        if role == QtCore.Qt.EditRole and index.column() == 3:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
            if value:
                self.hideRow([index.row()])
        elif role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            self.arraydata[row][column] = value
            self.dataChanged.emit(index, index)
            return True

        if index.column() == 3:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
            if value:
                self.hideRow([index.row()])
            #
            # if value.isValid():
            #     # May be use try, IndexError exept if None value
            #     value = value.toPyObject()
            #     self.arraydata[row][column] = value
            #     self.dataChanged.emit(index, index)
            #     return True
        # self._arraydata = copy.deepcopy(self.arraydata)
        return False

    def headerData(self, section, orientation, role):
        # self.headerdata = copy.deepcopy(self._headerdata)
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section < len(self.headerdata[0]):
                    return self.headerdata[0][section]
                else:
                    return 'not implemented'
                # return QtCore.QString(self.headerdata[0].column())
            else:
                if section < len(self.headerdata[1]):
                    return self.headerdata[1][section]
                else:
                    return 'not implemented'
                # return QtCore.QString(self.headerdata[1].column())

    def insertRow(self, position, rows, date, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            default_values = ['0'] * (len(self.headerdata[0])-1) + [False]
            self.headerdata[1].insert(position, date)
            self.arraydata.insert(position, default_values)
            print(self.headerdata)
        self._arraydata = copy.deepcopy(self.arraydata)
        self._headerdata = copy.deepcopy(self.headerdata)
        self.endInsertRows()
        return True

    def hideRow(self, positions, parent=QtCore.QModelIndex()):
        print(positions)
        self._arraydata = copy.deepcopy(self.arraydata)
        self._headerdata = copy.deepcopy(self.headerdata)
        for ind in sorted(positions, reverse=True):
            self.beginRemoveRows(parent, ind, ind)
            # self.arraydata = copy.deepcopy(self._arraydata)
            # self.headerdata = copy.deepcopy(self._headerdata)
            if len(self.arraydata) > 1:
                del self.arraydata[ind]
                del self.headerdata[1][ind]
            else:
                self.arraydata = []
                self.headerdata[1] = []
            self.endRemoveRows()
        return True

    def insertColumns(self, position, columns, parent=QtCore.QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)
        row_count = len(self.arraydata)
        for i in range(columns):
            for j in range(row_count):
                self.arraydata[j].insert(position, '0')
        self._arraydata = copy.deepcopy(self.arraydata)
        self.endInsertColumns()
        return True

    def revert(self):
        self.layoutAboutToBeChanged.emit()
        # custom_sort() is built into the data structure
        self.arraydata = copy.deepcopy(self._arraydata)
        self.headerdata = copy.deepcopy(self._headerdata)
        self.layoutChanged.emit()

    def db_to_save(self, **kwargs):
        print('db_to_save is called: ', kwargs)
        action_type = kwargs['action']
        if action_type == 'init':
            for ind_k in range(len(self.headerdata[1])):
                k = self.headerdata[1][ind_k]
                self.db_tasks[k] = self.arraydata[ind_k]

        if action_type == 'deadline_change':
            row_ind = kwargs['row_index']
            k = self.headerdata[1][row_ind]
            self.db_tasks[k][0] = kwargs['data'].toString(q_date_time_format)

        if action_type == 'task_change':
            row_ind = kwargs['row_index']
            k = self.headerdata[1][row_ind]
            self.db_tasks[k][1] = str(kwargs['data'])

        if action_type == 'work_type_change':
            row_ind = kwargs['row_index']
            k = self.headerdata[1][row_ind]
            self.db_tasks[k][2] = str(kwargs['data'])

        if action_type == 'is_closed':
            row_ind = kwargs['row_index']
            k = self.headerdata[1][row_ind]
            self.db_tasks[k][-1] = str(kwargs['data'])
            self.layoutChanged.emit()



#
# class TableView(QtWidgets.QTableView):
#     """
#     A simple table to demonstrate the QComboBox delegate.
#     """
#     def __init__(self, *args, **kwargs):
#         QtWidgets.QTableView.__init__(self, *args, **kwargs)
#         self.setItemDelegateForColumn(3, CheckBoxDelegate(self))
#
#
#
# class comboBoxDelegate(QtWidgets.QItemDelegate):
#     items = new_task[2]
#     def __init__(self, parent=None):
#         QtWidgets.QItemDelegate.__init__(self, parent)
#         # self.items = items
#         # self.chkboxSize = 19  # ?!
#
#     def createEditor(self, parent, option, index):
#         cbox = QtWidgets.QComboBox(parent)
#         cbox.addItems(self.items)
#         return cbox
#
#     def updateEditorGeometry(self, editor, option, index):
#         pass


def nix_date_time(all_width):
    # Parce current date and time
    t = time.strftime('%d.%m.%y.%H.%M').split('.')
    all_width = int(all_width)
    pixmap = QtGui.QPixmap(all_width, 120)  # "image/0.png")
    # pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.drawPixmap(45 * 0, 0, 45, 120, QtGui.QPixmap('images/{0}.png'.format(str(t[0][0]))).scaled(45, 120))
    painter.drawPixmap(45 * 1, 0, 45, 120, QtGui.QPixmap('images/{0}.png'.format(str(t[0][1]))).scaled(45, 120))
    painter.drawPixmap(45 * 2, 0, 45, 120, QtGui.QPixmap('images/dot_0.png').scaled(45, 120))
    painter.drawPixmap(45 * 3, 0, 45, 120, QtGui.QPixmap('images/{0}.png'.format(str(t[1][0]))).scaled(45, 120))
    painter.drawPixmap(45 * 4, 0, 45, 120, QtGui.QPixmap('images/{0}.png'.format(str(t[1][1]))).scaled(45, 120))
    painter.drawPixmap(45 * 5, 0, 45, 120, QtGui.QPixmap('images/dot_0.png').scaled(45, 120))
    painter.drawPixmap(45 * 6, 0, 45, 120, QtGui.QPixmap('images/{0}.png'.format(str(t[2][0]))).scaled(45, 120))
    painter.drawPixmap(45 * 7, 0, 45, 120, QtGui.QPixmap('images/{0}.png'.format(str(t[2][1]))).scaled(45, 120))
    # painter.drawPixmap(360, 0, 45, 120, QtGui.QPixmap('images/no.png').scaled(45, 120))
    painter.drawPixmap(all_width - 45 * 5, 0, 45, 120,
                       QtGui.QPixmap('images/{0}.png'.format(str(t[3][0]))).scaled(45, 120))
    painter.drawPixmap(all_width - 45 * 4, 0, 45, 120,
                       QtGui.QPixmap('images/{0}.png'.format(str(t[3][1]))).scaled(45, 120))
    painter.drawPixmap(all_width - 45 * 3, 0, 45, 120, QtGui.QPixmap('images/dot_0.png').scaled(45, 120))
    painter.drawPixmap(all_width - 45 * 2, 0, 45, 120,
                       QtGui.QPixmap('images/{0}.png'.format(str(t[4][0]))).scaled(45, 120))
    painter.drawPixmap(all_width - 45 * 1, 0, 45, 120, QtGui.QPixmap('images/{0}.png'.format(str(t[4][1]))).scaled(45,
                                                                                                                   120))  # transformMode=QtCore.Qt.SmoothTransformation
    brush = QtGui.QBrush()
    brush.setColor(QtGui.QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.SolidPattern)
    painter.setBrush(brush)
    painter.drawRect(45 * 8, 0, all_width - 45 * 6 - 45 * 7, 120)
    painter.end()
    # pixmap = pixmap.scaledToHeight(120)
    return pixmap.scaled(all_width, 120)


def live_and_prosper_calc():
    # Calculate weeks was lived
    ct = datetime.date.today()
    dob = datetime.date(1988, 11, 19)
    doe = datetime.date(2088, 11, 19)
    # dob = time.strptime("19 Nov 1988", "%d %b %Y")
    # doe = time.strptime("19 Nov 2088", "%d %b %Y")
    # ct = time.strftime("%d %b %Y")
    return round((ct - dob) / (doe - dob), 4) * 100.0


def set_task_text(text):
    text_to_paste = '<table border="1">\
<thead>\
<tr>\
<th>Date (set\line)</th>\
<th>Task</th>\
<th>Impotance (h,m,l)</th></tr>\
</thead>\
{0}\
</table>'.format(text)
    return text_to_paste


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    # app.setStyle("Fusion")
    main_window = MainWindow()
    # palette = QtGui.QPalette()
    # palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    # palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    # app.setPalette(palette)
    sys.exit(app.exec_())
