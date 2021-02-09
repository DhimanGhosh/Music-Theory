import os, sys, platform, qdarkgraystyle
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QRadioButton, QComboBox, QLineEdit, QPushButton
from PyQt5.QtGui import QFont

utils_dir = assets_dir = ''
# ----- Access Other Directories on Particular Platform ----- #
if platform.system() == 'Linux':
    utils_dir = os.path.realpath('../Utils') + '/'
    sys.path.insert(0, utils_dir)
    from Music import Music
    from Voice_Assistant import Voice_Assistant

    assets_dir = os.path.realpath('../assets') + '/'
    sys.path.insert(0, assets_dir)
else:
    root_dir = os.path.realpath('')
    root_dir = '\\'.join(root_dir.split('\\')[:-1])
    sys.path.insert(0, root_dir)
    from Utils.Music import Music
    from Utils.Voice_Assistant import Voice_Assistant

    utils_dir = root_dir + '/Utils/'
    assets_dir = root_dir + '/assets/'

features = utils_dir + 'Features.txt'
app_logo = assets_dir + 'app_logo.png'
reset_icon = assets_dir + 'reset.png'
sharp_icon = assets_dir + 'sharp.png'
flat_icon = assets_dir + 'flat.png'
audio_file = assets_dir + 'Audio.wav'


class Ui_Dialog(object):
    def __init__(self, Dialog):
        super(Ui_Dialog, self).__init__()
        # ----- App Design ----- #
        # To make this to work in Fullscreen; set 'self.window_width' and 'self.window_height' to 'size.width()' and 'size.height()'
        # To make this to work in Fullscreen-Windowed; set 'self.window_width' and 'self.window_height' to 'rect.width()' and 'rect.height()'
        self.window_width = 500
        self.window_height = 800
        # self.window_width = size.width()    # Fullscreen
        # self.window_height = size.height()  # Fullscreen
        self.drop_down_width = self.window_width // 2 + 50
        self.notation_width = self.drop_down_width // 2
        self.widget_height = self.window_height // 20
        self.label_width = self.window_width // 4
        self.label_padding_left = self.window_width // 20
        self.content_padding_left = self.label_padding_left + self.label_width
        self.padding_top = self.window_height // 10
        self.v_space_between_widgets = self.window_height // 5

        self.app_font = QFont()
        self.output_text_font = QFont()
        self.app_font.setPointSize((self.window_width + self.window_height) // 100)
        self.output_text_font.setPointSize((self.window_width + self.window_height) // 120)

        self.label_style = 'color: rgb(176, 85, 87);'
        self.option_menu_style = 'color: rgb(158, 212, 124);'
        self.input_menu_style = 'color: rgb(15, 99, 189);'
        self.output_text_style = 'color: rgba(255, 255, 255, 150);'
        self.reset_button_style = '\
            background-color: red;\
            border-radius: 15px;\
            color: rgb(0, 0, 0);'

        # ----- App Window Settings ----- #
        Dialog.setObjectName("Dialog")
        self.set_window_resizable(window_obj=Dialog, width=self.window_width, height=self.window_height, flag=False)

        # ----- Widgets ----- #
        self.notation_label = QLabel(Dialog)
        self.notation_S = QRadioButton(Dialog)
        self.notation_b = QRadioButton(Dialog)
        self.option_label = QLabel(Dialog)
        self.option_menu = QComboBox(Dialog)
        self.input_label = QLabel(Dialog)
        self.input_menu = QComboBox(Dialog)
        self.output_label = QLabel(Dialog)
        self.output_text = QLineEdit(Dialog)
        self.reset_button = QPushButton(Dialog)
        self.va_button = QPushButton(Dialog)

        # ----- Music Logic ----- #
        music = Music()
        self.notesS = music.notesS
        self.notesb = music.notesb
        self.notes = self.notesS
        self.options_menu_vals = tuple()
        with open(features, 'r') as f:
            self.options_menu_vals = tuple([x.strip() for x in f.readlines()])
        self.input_menu_vals = tuple()
        self.rel_maj_min_options = ('Relative Major', 'Relative Minor')
        self.major_minor_options = ('Major', 'Minor')
        self.guitar_frets_options = tuple([str(i) for i in range(1, 23)])  # For Capo position entry
        self.sub_menu_selected = dict()  # To Keep track of options selected
        self.select_data = '--Select--'
        self.option_change_detect = ''
        self.input_change_detect = ''

        # ----- Voice Assistant ----- #
        self.va = Voice_Assistant()

    def setupUi(self, Dialog):
        # Notations
        self.notation_label.setFont(self.app_font)
        self.notation_label.setGeometry(
            QtCore.QRect(self.label_padding_left, self.padding_top, self.label_width, self.widget_height))
        self.notation_label.setObjectName("notation_label")
        self.notation_label.setStyleSheet(self.label_style)
        self.notation_S.setFont(self.app_font)
        self.notation_S.setGeometry(
            QtCore.QRect(self.content_padding_left, self.padding_top, self.notation_width, self.widget_height))
        self.notation_S.setObjectName("notation_S")
        self.notation_S.setChecked(True)
        self.notation_b.setFont(self.app_font)
        self.notation_b.setGeometry(
            QtCore.QRect(self.content_padding_left + self.notation_width, self.padding_top, self.notation_width,
                         self.widget_height))
        self.notation_b.setObjectName("notation_b")

        self.padding_top += self.v_space_between_widgets
        # Option Menu
        self.option_label.setFont(self.app_font)
        self.option_label.setGeometry(
            QtCore.QRect(self.label_padding_left, self.padding_top, self.label_width, self.widget_height))
        self.option_label.setObjectName("options_label")
        self.option_label.setStyleSheet(self.label_style)
        self.option_menu.setFont(self.app_font)
        self.option_menu.setGeometry(
            QtCore.QRect(self.content_padding_left, self.padding_top - 2, self.drop_down_width, self.widget_height))
        self.option_menu.setObjectName("option_menu")

        self.option_menu.addItem(self.select_data)
        self.option_menu.addItems(self.options_menu_vals)
        self.option_menu.currentIndexChanged.connect(self.option_selection_change)
        # self.option_menu.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.option_menu.setStyleSheet(self.option_menu_style)

        self.padding_top += self.v_space_between_widgets
        # Input Menu
        self.input_label.setFont(self.app_font)
        self.input_label.setGeometry(
            QtCore.QRect(self.label_padding_left, self.padding_top, self.label_width, self.widget_height))
        self.input_label.setObjectName("input_label")
        self.input_label.setStyleSheet(self.label_style)
        self.input_menu.setFont(self.app_font)
        self.input_menu.setGeometry(
            QtCore.QRect(self.content_padding_left, self.padding_top - 2, self.drop_down_width, self.widget_height))
        self.input_menu.setObjectName("input_menu")
        self.input_menu.setDisabled(True)
        self.input_menu.setStyleSheet(self.input_menu_style)

        self.padding_top += self.v_space_between_widgets
        # Output
        self.output_label.setFont(self.app_font)
        self.output_label.setGeometry(
            QtCore.QRect(self.label_padding_left, self.padding_top, self.label_width, self.widget_height))
        self.output_label.setObjectName("output_label")
        self.output_label.setStyleSheet(self.label_style)
        self.output_text.setFont(self.output_text_font)
        self.output_text.setGeometry(
            QtCore.QRect(self.content_padding_left, self.padding_top - 2, self.drop_down_width, self.widget_height))
        self.output_text.setObjectName("output_text")
        self.output_text.setDisabled(True)
        self.output_text.setStyleSheet(self.output_text_style)

        self.padding_top += self.v_space_between_widgets // 2
        # App RESET
        self.reset_button.setFont(self.app_font)
        self.reset_button.setGeometry(
            QtCore.QRect(self.label_padding_left, self.padding_top, self.label_width + self.drop_down_width,
                         self.widget_height))
        self.reset_button.setObjectName("reset_button")
        self.reset_button.clicked.connect(self.reset)
        self.reset_button.setIcon(QtGui.QIcon(reset_icon))
        self.reset_button.setIconSize(QtCore.QSize(self.widget_height, self.widget_height))
        self.reset_button.setStyleSheet(self.reset_button_style)

        self.padding_top += self.v_space_between_widgets // 2
        # Voice Assitant
        self.va_button.setFont(self.app_font)
        self.va_button.setGeometry(
            QtCore.QRect(self.label_padding_left, self.padding_top, self.label_width + self.drop_down_width,
                         self.widget_height))
        self.va_button.setObjectName("va_button")
        self.va_button.clicked.connect(self.Voice_Assistant_Call)
        self.va_button.setIcon(QtGui.QIcon(app_logo))
        self.va_button.setIconSize(QtCore.QSize(self.widget_height, self.widget_height))
        self.va_button.setStyleSheet(self.reset_button_style)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def option_selection_change(self):
        selected_text = self.option_menu.currentText()

        # ----- Detect change in menu selection ----- #
        if self.option_change_detect != selected_text:
            print(self.sub_menu_selected)
            print('Option Menu Change Detected')
            # self.input_menu.clear()
            self.output_text.clear()  # This is working; "input_menu.clear()" getting hanged
            self.input_menu.addItem(self.select_data)
            print('Input Menu cleared')
            self.option_change_detect = selected_text
            print('New opt change detect set')

        # ----- Change Input Menu Values ----- #
        if selected_text != self.select_data:
            print('Option Item Selected:', selected_text)
            self.input_menu.setDisabled(False)
            if selected_text == self.options_menu_vals[0]:  # Major Scale
                print('maj scale')
                if self.notation_S.isChecked():
                    self.notes = self.notesS
                elif self.notation_b.isChecked():
                    self.notes = self.notesb
                self.input_menu_vals = self.notes
            elif selected_text == self.options_menu_vals[1]:  # Major Chord
                print('maj chord')
                if self.notation_S.isChecked():
                    self.notes = self.notesS
                elif self.notation_b.isChecked():
                    self.notes = self.notesb
                self.input_menu_vals = self.notes
            elif selected_text == self.options_menu_vals[2]:  # Chords in Major Scale
                print('chords in maj scale')
                if self.notation_S.isChecked():
                    self.notes = self.notesS
                elif self.notation_b.isChecked():
                    self.notes = self.notesb
                self.input_menu_vals = self.notes
            print('rcvd inp menu vals')
            self.input_menu.addItems(self.input_menu_vals)
            self.input_menu.currentIndexChanged.connect(self.input_selection_change)
            print('set inp menu vals')
        else:
            self.input_menu.clear()
            self.input_menu.setDisabled(True)

        # ----- To Keep track of Selections ----- #
        if self.option_menu.currentText() not in self.sub_menu_selected and self.option_menu.currentText() != self.select_data:
            self.sub_menu_selected[self.option_menu.currentText()] = []

    def input_selection_change(self):
        selected_text = self.input_menu.currentText()

        # ----- Detect change in menu selection ----- #
        if self.input_change_detect != selected_text:
            self.input_change_detect = selected_text

        # ----- Action performed on Input Menu Values ----- #
        if selected_text != self.select_data:
            option_menu_selected_text = self.option_menu.currentText()
            if option_menu_selected_text == self.options_menu_vals[0]:  # Major Scale
                note = selected_text
                music = Music(note)
                result = music.major_scale()
                self.output_text.setText('     '.join(result))
            elif option_menu_selected_text == self.options_menu_vals[1]:  # Major Chord
                note = selected_text
                music = Music(note)
                result = music.major_chord()
                self.output_text.setText('     '.join(result))
            elif option_menu_selected_text == self.options_menu_vals[2]:  # Chords in Major Scale
                note = selected_text
                music = Music(note)
                result = music.chords_in_major_scale()
                self.output_text.setText('     '.join(result))

        # ----- To Keep track of Selections ----- #
        if self.option_menu.currentText() != self.select_data:
            if self.option_menu.currentText() in self.sub_menu_selected:
                self.sub_menu_selected[self.option_menu.currentText()].append(selected_text)
                self.sub_menu_selected[self.option_menu.currentText()] = list(
                    set(self.sub_menu_selected[self.option_menu.currentText()]))
            else:
                self.sub_menu_selected[self.option_menu.currentText()] = list(set([selected_text]))

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Music Theory Guide"))
        self.notation_label.setText(_translate("Dialog", "Notation"))
        self.notation_S.setIcon(QtGui.QIcon(sharp_icon))
        self.notation_b.setIcon(QtGui.QIcon(flat_icon))
        self.option_label.setText(_translate("Dialog", "Options"))
        self.input_label.setText(_translate("Dialog", "Input"))
        self.output_label.setText(_translate("Dialog", "Output"))
        self.output_text.setText(_translate("Dialog", ""))
        self.reset_button.setText(_translate("Dialog", "Reset Application"))
        self.va_button.setText(_translate("Dialog", "Voice Assistant"))

    def set_window_resizable(self, window_obj, width, height, flag=False):
        if not flag:
            window_obj.setGeometry(rect.width() // 2 - width // 2, rect.height() // 2 - height // 2, width, height)
            window_obj.setMaximumHeight(height)
            window_obj.setMinimumHeight(height)
            window_obj.setMaximumWidth(width)
            window_obj.setMinimumWidth(width)
        else:
            window_obj.resize(width, height)

    def reset(self):
        self.notation_S.setChecked(True)
        self.option_menu.setCurrentIndex(0)
        self.input_menu.clear()
        self.output_text.setText('')

    def Voice_Assistant_Call(self):
        self.va.start_AI_engine()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkgraystyle.load_stylesheet())
    screen = app.primaryScreen()
    # print('Screen: %s' % screen.name())
    size = screen.size()
    # print('Size: %d x %d' % (size.width(), size.height()))
    rect = screen.availableGeometry()
    # print('Available: %d x %d' % (rect.width(), rect.height()))

    MainWindow = QMainWindow()
    MainWindow.setWindowIcon(QtGui.QIcon(app_logo))
    ui = Ui_Dialog(MainWindow)

    ui.setupUi(MainWindow)
    ui.retranslateUi(MainWindow)
    QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # MainWindow.showFullScreen()    # Fullscreen
    MainWindow.show()
    sys.exit(app.exec_())
