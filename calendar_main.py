# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui, uic
import time
import datetime
import pickle
import copy

"""This module provides main structure and function of program."""

__version__ = "0.1.0"
__author__ = 'Yunovidov Dmitriy: Dm.Yunovidov@gmail.com'

COLORS = [
    '#053061',
    '#2166ac',
    '#4393c3',
    '#92c5de',
    '#d1e5f0',
    '#f7f7f7',
    '#fddbc7',
    '#f4a582',
    '#d6604d',
    '#b2182b',
    '#67001f'
]


class MainWindow(QtWidgets.QMainWindow):
    db_tasks = None
    db_down_tasks = None
    daetime_format = 'dd-MM-yy HH:mm:ss'

    def __init__(self):
        super(QtWidgets.QMainWindow, self).__init__()
        uic.loadUi("py_call.ui", self)

        self.setWindowTitle("Test calendar v.0.1.0")

        self.setCentralWidget(self.centralwidget)
        self.setMenuBar(self.menubar)

        # Init QSystemTrayIcon
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon("icon_1.png"))

        # Tray menu
        show_action = QtWidgets.QAction("Show", self)
        hide_action = QtWidgets.QAction("Hide", self)
        quit_action = QtWidgets.QAction("Exit", self)

        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.close)

        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Configured calendar
        self.calendarWidget.setSelectedDate(QtCore.QDate.currentDate())
        self.first_date(QtCore.QDateTime.currentDateTime())

        # Configure lived progress bar
        self.prb_live.setRange(0, 100)
        v = live_and_prosper_calc()
        self.prb_live.setValue(int(v))
        self.prb_live.setFormat("time alive from 100 yo: " + str(v) + "%")

        # Configure tasks progress bar
        self.prb_tasks.setRange(0, 100)
        self.prb_tasks.setFormat("tasks solved: " + str(0) + "%")
        self.prb_tasks.setValue(0)

        # Configured nix label with date and time
        self.l_nix.setPixmap(nix_date_time(all_width=self.calendarWidget.width()))
        # creating a timer object
        self.timer = QtCore.QTimer(self)

        # adding action to timer
        self.timer.timeout.connect(self.update_label_tasks)
        # update the timer every 2 second
        self.timer.start(2000)

        # self.calendarWidget.clicked.connect(lambda x: self.click_data(x))

        self.pb_task_add.clicked.connect(self.task_add)
        self.pb_task_undo.clicked.connect(self.task_undo)

        self.pb_exit.clicked.connect(self.hide_it)
        self.pb_save.clicked.connect(self.save_data)

        # Show program
        # self.show()
        # tray.setContextMenu(menu)

    def hide_it(self):
        """
        Hide program to tray
        :return: None
        """
        self.hide()
        self.tray_icon.showMessage(
            "Tray Program",
            "Application was minimized to Tray",
            QtWidgets.QSystemTrayIcon.Information,
            2000
        )

    def update_label_tasks(self):
        """
        Update nix time and % of solved tasks
        :return: None
        """
        if self.db_tasks and self.db_down_tasks:
            solve = round(len(self.db_down_tasks) / (len(self.db_tasks) + len(self.db_down_tasks)) * 100, 2)
            self.prb_tasks.setFormat("tasks solved: " + str(solve) + "%")
            self.prb_tasks.setValue(int(solve))
        self.l_nix.setPixmap(nix_date_time(all_width=self.calendarWidget.width()))

    def task_undo(self):
        """
        Remoove last task from QTextEdit
        :return: None
        """
        print('Undo clicked')
        self.update_tasks(is_undo=True)
        self.display_task(self.db_tasks)

    def task_add(self):
        """
        Add row in md table in QTextEdit with default data
        :return: None
        """
        print('Plus clicked')
        self.update_tasks()
        deadline_date = self.calendarWidget.selectedDate()
        add_date = QtCore.QDateTime.currentDateTime()
        self.db_tasks[add_date] = [
            QtCore.QDateTime(deadline_date.addDays(1)),
            'Describe the task',
            'Work/Project/Home',  # ['Work', 'Project', 'Home'],  type of task
            '0, ..., 10',  # importance from 0 to 10, 0 - most important
            'No'  # ['No', 'Yes'] is completed
        ]
        print('Len of db: ', len(list(self.db_tasks.keys())))
        self.display_task(self.db_tasks)

    def update_tasks(self, is_undo=False):
        """
        Update db with tasks
        :return: None
        """
        self.db_tasks = {}
        unformat_data = self.te_tasks.toMarkdown().split('\n')
        print(unformat_data)
        lend_data = len(unformat_data)
        if is_undo:
            lend_data -= 3
        for l_i in range(lend_data):
            line = unformat_data[l_i]
            l_data = line.split('|')
            print(l_data)
            if len(l_data) > 7 and l_i > 2:
                l_data = l_data[1:-1]
                try:
                    task_date = QtCore.QDateTime.fromString(l_data[0], self.daetime_format)
                    deadline = QtCore.QDateTime.fromString(l_data[1], self.daetime_format)
                    describe = l_data[2]
                    task_type = l_data[3]
                    task_importance = l_data[4]
                    is_done = l_data[5]
                    self.db_tasks[task_date] = [
                        deadline,
                        describe,
                        task_type,
                        task_importance,
                        is_done
                    ]
                except TypeError as e:
                    print('Handled Error: ', e)

    def first_date(self, date):
        """
        Initiate or load db with tasks
        :param date:
        :return:
        """
        # print(date)
        # print(QtCore.QDate(2020, 10, 11))
        # print(QtCore.QDate(date.date()))
        # Try to load db from files
        try:
            self.db_tasks = pickle.load(open("dimyun_up.pickle", "rb"))
            print('Loaded up data: ', self.db_tasks)
        except (OSError, IOError) as e:
            print('Handled Error: ', e)
            init_task = [
                date.addDays(1),
                'Describe the task',
                'Work/Project/Home',  # ['Work', 'Project', 'Home'],  type of task
                '0, ..., 10',  # importance from 0 to 10, 0 - most important
                'No'  # ['No', 'Yes'] is completed
            ]
            self.db_tasks = {
                date: init_task
            }

        # Try to load all db form file
        try:
            self.db_down_tasks = pickle.load(open("dimyun_down.pickle", "rb"))
            print('Loaded down data: ', self.db_down_tasks)
        except (OSError, IOError) as e:
            print('Handled Error: ', e)
            self.db_down_tasks = {}
        self.display_task(self.db_tasks)

    def display_task(self, db_in):
        """
        Display all task in text edit window with html syntax
        :param db_it: dictionary with data
        :return: None
        """
        text_all = [
            '|  Set Data  |  Deadline  |  Describe the Task  |  Type of Task  |  Importance  |  Is Completed  |\n',
            '|------------|------------|---------------------|----------------|--------------|----------------|\n'
        ]
        # print('Display db: ', db_in)
        for ind_date in list(db_in.keys()):
            if 'No' in db_in[ind_date][-1]:
                task_data = db_in[ind_date]
                text_in = '|  ' + ind_date.toString(self.daetime_format) + '  '
                text_in += '|  ' + task_data[0].toString(self.daetime_format) + '  '
                for i in range(1, len(task_data)):
                    text_in += '|  ' + task_data[i] + '  '
                text_in += '|\n'
                text_all.append(text_in)

                # Draw in calendar
                t_format = QtGui.QTextCharFormat()
                t_font = QtGui.QFont()
                t_font.setPixelSize(15)
                t_font.setBold(True)

                t_format.setFont(t_font)

                # t_format.setForeground(QtCore.Qt.red)

                # setting date text format
                self.calendarWidget.setDateTextFormat(task_data[0].date(), t_format)

        else:
                # Drop items from up task and save it in down task
                self.db_down_tasks[ind_date] = db_in.pop(ind_date)
                self.db_down_tasks[ind_date].append(QtCore.QDate.currentDate())  # append down date
        # print(text_all)
        self.te_tasks.setMarkdown(''.join(text_all))

    def closeEvent(self, event):
        self.save_dialog()
        self.timer.stop()
        self.timer.deleteLater()
        self.deleteLater()
        event.accept()
        # else:
        #     event.ignore()

    def save_dialog(self):
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
        self.update_tasks()
        self.display_task(self.db_tasks)
        pickle.dump(self.db_tasks, open("dimyun_up.pickle", "wb"))
        pickle.dump(self.db_down_tasks, open("dimyun_down.pickle", "wb"))


#
# class TaskTableModel(QtCore.QAbstractTableModel):
#     # class for tables model
#     q_date_time_format = "dd.MM.yyyy HH:mm"
#     new_task = None
#
#     def __init__(self, db_in, parent=None, *args):
#         """
#         :param datain: a list of lists with data
#         :param headerdata: a two list in list with headers data
#         :param parent: parent class
#         :param args: None
#         """
#         QtCore.QAbstractTableModel.__init__(self, parent, *args)
#         # Build arraydata and headers from dict
#
#         self.db_tasks = db_in
#         headerdata = [
#             ['Deadline', 'Task', 'Type', 'Is Close'],
#             list(db_in.keys())
#         ]
#         datain = [db_in[k] for k in db_in]
#         self.new_task = datain[0]
#
#         self.display_init(headerdata, datain)
#
#     def display_init(self, headerdata, datain):
#         self.arraydata = copy.deepcopy(datain)
#         self.headerdata = copy.deepcopy(headerdata)
#         self._arraydata = copy.deepcopy(datain)
#         self._headerdata = copy.deepcopy(headerdata)
#
#         # for ind_cccrow
#
#         # self.db_to_save(action_type = 'init')
#
#     def set_task_widgets(self, tv_table, row_index, row_deadline, row_work_type, row_is_closed):
#         # self.tv_tasks.setItemDelegateForColumn(2, comboBoxDelegate(self.tv_tasks))
#
#         all_add_widgets = []
#
#         c = QtWidgets.QDateTimeEdit()
#         c.setDisplayFormat(self.q_date_time_format)
#         c.setDateTime(QtCore.QDateTime.fromString(self.new_task[0]))
#         i = tv_table.model().index(row_index, 0)
#         tv_table.setIndexWidget(i, c)
#         all_add_widgets.append(c)
#
#         for i in [2, 3]:
#             c = QtWidgets.QComboBox()
#             c.addItems(self.new_task[i])
#             j = tv_table.model().index(row_index, i)
#             tv_table.setIndexWidget(j, c)
#             all_add_widgets.append(c)
#
#         all_add_widgets[0].dateTimeChanged.connect(
#             lambda x: tv_table.model().db_to_save(
#                 action='deadline_change',
#                 row_index=row_index,
#                 data=x
#             )
#         )
#         all_add_widgets[1].currentIndexChanged.connect(
#             lambda x: tv_table.model().db_to_save(
#                 action='work_type_change',
#                 row_index=row_index,
#                 data=self.new_task[2][x]
#             )
#         )
#         all_add_widgets[2].currentIndexChanged.connect(
#             lambda x: tv_table.model().db_to_save(
#                 action='is_closed',
#                 row_index=row_index,
#                 data=self.new_task[3][x]
#             )
#         )
#
#     def rowCount(self, parent):
#         return len(self.arraydata)
#
#     def columnCount(self, parent):
#         if self.arraydata:
#             return len(self.arraydata[0])
#         else:
#             return 0
#
#     def flags(self, index):
#         if index.column() == 3:
#             return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
#         else:
#             return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
#
#     def data(self, index, role):
#         if role == QtCore.Qt.EditRole:
#             row = index.row()
#             column = index.column()
#             return self.arraydata[row][column]
#
#         if role == QtCore.Qt.ToolTipRole:
#             # row = index.row()
#             # column = index.column()
#             return 'data for tasks'
#
#         if role == QtCore.Qt.DisplayRole:
#             row = index.row()
#             column = index.column()
#             if self.arraydata[row][3] == 'Yes':
#                 self.hideRow(row)
#             else:
#                 value = self.arraydata[row][column]
#                 return value
#
#     def setData(self, index, value, role=QtCore.Qt.EditRole):
#         print('Data is set', index, value, role, index.column())
#         if role == QtCore.Qt.EditRole and index.column() == 3:
#             print(">>> setData() role = ", role)
#             print(">>> setData() index.column() = ", index.column())
#             if value:
#                 self.hideRow([index.row()])
#         elif role == QtCore.Qt.EditRole:
#             row = index.row()
#             column = index.column()
#             self.arraydata[row][column] = value
#             self.dataChanged.emit(index, index)
#             return True
#
#         if index.column() == 3:
#             print(">>> setData() role = ", role)
#             print(">>> setData() index.column() = ", index.column())
#             if value:
#                 self.hideRow([index.row()])
#             #
#             # if value.isValid():
#             #     # May be use try, IndexError exept if None value
#             #     value = value.toPyObject()
#             #     self.arraydata[row][column] = value
#             #     self.dataChanged.emit(index, index)
#             #     return True
#         # self._arraydata = copy.deepcopy(self.arraydata)
#         return False
#
#     def headerData(self, section, orientation, role):
#         # self.headerdata = copy.deepcopy(self._headerdata)
#         if role == QtCore.Qt.DisplayRole:
#             if orientation == QtCore.Qt.Horizontal:
#                 if section < len(self.headerdata[0]):
#                     return self.headerdata[0][section]
#                 else:
#                     return 'not implemented'
#                 # return QtCore.QString(self.headerdata[0].column())
#             else:
#                 if section < len(self.headerdata[1]):
#                     return self.headerdata[1][section]
#                 else:
#                     return 'not implemented'
#                 # return QtCore.QString(self.headerdata[1].column())
#
#     def insertRow(self, position, rows, date, parent=QtCore.QModelIndex()):
#         self.beginInsertRows(parent, position, position + rows - 1)
#         for i in range(rows):
#             default_values = ['0'] * (len(self.headerdata[0])-1) + [False]
#             self.headerdata[1].insert(position, date)
#             self.arraydata.insert(position, default_values)
#             print(self.headerdata)
#         self._arraydata = copy.deepcopy(self.arraydata)
#         self._headerdata = copy.deepcopy(self.headerdata)
#         self.endInsertRows()
#         return True
#
#     def hideRow(self, positions, parent=QtCore.QModelIndex()):
#         print(positions)
#         self._arraydata = copy.deepcopy(self.arraydata)
#         self._headerdata = copy.deepcopy(self.headerdata)
#         for ind in sorted(positions, reverse=True):
#             self.beginRemoveRows(parent, ind, ind)
#             # self.arraydata = copy.deepcopy(self._arraydata)
#             # self.headerdata = copy.deepcopy(self._headerdata)
#             if len(self.arraydata) > 1:
#                 del self.arraydata[ind]
#                 del self.headerdata[1][ind]
#             else:
#                 self.arraydata = []
#                 self.headerdata[1] = []
#             self.endRemoveRows()
#         return True
#
#     def insertColumns(self, position, columns, parent=QtCore.QModelIndex()):
#         self.beginInsertColumns(parent, position, position + columns - 1)
#         row_count = len(self.arraydata)
#         for i in range(columns):
#             for j in range(row_count):
#                 self.arraydata[j].insert(position, '0')
#         self._arraydata = copy.deepcopy(self.arraydata)
#         self.endInsertColumns()
#         return True
#
#     def revert(self):
#         self.layoutAboutToBeChanged.emit()
#         # custom_sort() is built into the data structure
#         self.arraydata = copy.deepcopy(self._arraydata)
#         self.headerdata = copy.deepcopy(self._headerdata)
#         self.layoutChanged.emit()
#
#     def db_to_save(self, **kwargs):
#         print('db_to_save is called: ', kwargs)
#         action_type = kwargs['action']
#         if action_type == 'init':
#             for ind_k in range(len(self.headerdata[1])):
#                 k = self.headerdata[1][ind_k]
#                 self.db_tasks[k] = self.arraydata[ind_k]
#
#         if action_type == 'deadline_change':
#             row_ind = kwargs['row_index']
#             k = self.headerdata[1][row_ind]
#             self.db_tasks[k][0] = kwargs['data'].toString(q_date_time_format)
#
#         if action_type == 'task_change':
#             row_ind = kwargs['row_index']
#             k = self.headerdata[1][row_ind]
#             self.db_tasks[k][1] = str(kwargs['data'])
#
#         if action_type == 'work_type_change':
#             row_ind = kwargs['row_index']
#             k = self.headerdata[1][row_ind]
#             self.db_tasks[k][2] = str(kwargs['data'])
#
#         if action_type == 'is_closed':
#             row_ind = kwargs['row_index']
#             k = self.headerdata[1][row_ind]
#             self.db_tasks[k][-1] = str(kwargs['data'])
#             self.layoutChanged.emit()


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


# class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
#
#     def __init__(self, icon, parent=None):
#         QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
#         menu = QtWidgets.QMenu(parent)
#         showAction = menu.addAction('Show')
#         # showAction = menu.addAction('Show')
#         exitAction = menu.addAction("Exit")
#         self.setContextMenu(menu)
#
#         # Adding item on the menu bar
#         tray = QtWidgets.QSystemTrayIcon()
#         tray.setIcon(icon)
#         tray.setVisible(True)
#
#         showAction.triggered.connect(parent.show)
#         exitAction.triggered.connect(parent.close)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    # app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    # trayIcon = SystemTrayIcon(QtGui.QIcon("icon_1.png"), main_window)
    # trayIcon.show()
    # palette = QtGui.QPalette()
    # palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    # palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    # app.setPalette(palette)
    sys.exit(app.exec_())
