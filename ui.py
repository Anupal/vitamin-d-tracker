import constants
from datetime import datetime, timedelta
from itertools import accumulate

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QMainWindow,
    QPushButton,
    QFrame,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsView,
    QTimeEdit,
    QLineEdit,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


def SPACING(size):
    return QSpacerItem(
        size,
        size,
        QSizePolicy.Policy.Minimum,
        QSizePolicy.Policy.Minimum,
    )


def SPACING_EX(size, direction="h"):
    return QSpacerItem(
        size,
        size,
        QSizePolicy.Policy.Expanding
        if direction == "h"
        else QSizePolicy.Policy.Minimum,
        QSizePolicy.Policy.Expanding
        if direction == "v"
        else QSizePolicy.Policy.Minimum,
    )


class ImageSelector(QWidget):
    def __init__(
        self,
        identifier,
        image_path,
        name,
        description,
        image_width=20,
        image_height=20,
        selection_callback=None,
    ):
        super().__init__()

        self.identifier = identifier
        self.selection_callback = selection_callback
        self.setFixedSize(500, 140)
        self.layout = QHBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        # Image
        self.imageWrapper = QLabel(self)
        self.imageWrapper.setObjectName("imageSelector__imageWrapper")
        imagePixmap = QtGui.QPixmap(image_path)
        imagePixmap = imagePixmap.scaled(image_width, image_height)
        self.imageWrapper.setPixmap(imagePixmap)

        # Name
        self.imageName = QLabel(name)
        self.imageName.setObjectName("imageSelector__imageName")

        # Description
        self.imageDescription = QLabel(description)
        self.imageDescription.setObjectName("imageSelector__imageDescription")

        self.layout.addItem(SPACING(20))
        self.layout.addWidget(self.imageWrapper)
        self.layout.addItem(SPACING(50))
        self.layout.addWidget(self.imageName)

        self.layout.addItem(SPACING_EX(30))
        self.layout.addWidget(self.imageDescription)
        self.layout.addItem(SPACING(20))

        wrapper_layout = QHBoxLayout(self)
        wrapper_view = QWidget()
        wrapper_view.setLayout(self.layout)
        wrapper_view.setObjectName("imageSelector")
        wrapper_layout.addWidget(wrapper_view)

    def mousePressEvent(self, _):
        self.selection_callback(self.identifier)


class SettingsView(QWidget):
    def __init__(self, user_data, tracker, button_callbacks={}):
        super().__init__()
        self.user_data = user_data
        self.tracker = tracker
        self.button_callbacks = button_callbacks

        self.layout = QVBoxLayout(self)
        self.upper_layout = QHBoxLayout()
        self.leftlayout = QVBoxLayout()
        self.leftlayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.headingSkin = QLabel("Select your skin color")
        self.headingSkin.setObjectName("skinSelectorView__heading")

        skinType1Selector = ImageSelector(*constants.skin_list[0], self.on_selection)
        skinType2Selector = ImageSelector(*constants.skin_list[1], self.on_selection)
        skinType3Selector = ImageSelector(*constants.skin_list[2], self.on_selection)
        skinType4Selector = ImageSelector(*constants.skin_list[3], self.on_selection)
        skinType5Selector = ImageSelector(*constants.skin_list[4], self.on_selection)
        skinType6Selector = ImageSelector(*constants.skin_list[5], self.on_selection)

        self.skintypeItems = {
            constants.skin_list[0][0]: skinType1Selector,
            constants.skin_list[1][0]: skinType2Selector,
            constants.skin_list[2][0]: skinType3Selector,
            constants.skin_list[3][0]: skinType4Selector,
            constants.skin_list[4][0]: skinType5Selector,
            constants.skin_list[5][0]: skinType6Selector,
        }

        print("skintypeItems:", self.skintypeItems)

        if self.user_data.data:
            self.currentSkinType = self.user_data.data["skin_type"]

            self.skintypeItems[self.currentSkinType].setStyleSheet(
                """
                #imageSelector {
                    border: 2px solid #909090;
                    border-radius: 10px;
                    background-color: #909090;
                    color: white;
                }
                """
            )
        else:
            self.currentSkinType = None

        self.leftlayout.addItem(SPACING(5))
        self.leftlayout.addWidget(
            self.headingSkin, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.leftlayout.addItem(SPACING(5))
        self.leftlayout.addWidget(skinType1Selector)
        self.leftlayout.addWidget(skinType2Selector)
        self.leftlayout.addWidget(skinType3Selector)
        self.leftlayout.addWidget(skinType4Selector)
        self.leftlayout.addWidget(skinType5Selector)
        self.leftlayout.addWidget(skinType6Selector)

        self.upper_layout.addLayout(self.leftlayout)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.upper_layout.addWidget(self.line)

        self.rightlayout = QVBoxLayout()
        self.rightlayout.setContentsMargins(20, 20, 20, 20)
        self.rightlayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.headingAge = QLabel("Enter your Age")
        self.headingAge.setObjectName("skinSelectorView__heading")

        self.rightlayout.addItem(SPACING(50))
        self.rightlayout.addWidget(
            self.headingAge, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.rightlayout.addItem(SPACING(50))

        self.inputAge = QLineEdit()
        self.inputAge.setObjectName("inputAge")
        if self.user_data.data:
            self.inputAge.setText(str(user_data.data["age"]))
        self.rightlayout.addWidget(self.inputAge)

        self.headingLocation = QLabel("Enter your default location")
        self.headingLocation.setObjectName("skinSelectorView__heading")

        self.rightlayout.addItem(SPACING(50))
        self.rightlayout.addWidget(
            self.headingLocation, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.rightlayout.addItem(SPACING(50))

        self.inputLocation = QLineEdit()
        self.inputLocation.setObjectName("inputLocation")
        if self.user_data.data:
            self.inputLocation.setText(user_data.data["location"][0])
        self.rightlayout.addWidget(self.inputLocation)

        self.headingTarget = QLabel("Enter your daily target")
        self.headingTarget.setObjectName("skinSelectorView__heading")

        self.rightlayout.addItem(SPACING(50))
        self.rightlayout.addWidget(
            self.headingTarget, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
        )

        self.inputDailyTarget = QLineEdit()
        self.inputDailyTarget.setObjectName("inputDailyTarget")
        if self.user_data.data:
            str(self.inputDailyTarget.setText(str(user_data.data["target"])))
        self.rightlayout.addWidget(self.inputDailyTarget)

        self.upper_layout.addLayout(self.rightlayout)

        self.layout.addLayout(self.upper_layout)

        self.lower_layout = QHBoxLayout()
        self.submitButton = QPushButton("SUBMIT")
        self.submitButton.setFixedSize(200, 40)
        self.submitButton.clicked.connect(self.submit_callback)
        self.cancelButton = QPushButton("CANCEL")
        self.cancelButton.setFixedSize(200, 40)
        if "back" in self.button_callbacks:
            self.cancelButton.clicked.connect(self.button_callbacks["back"])
        self.lower_layout.addWidget(self.submitButton)
        self.lower_layout.addWidget(self.cancelButton)
        self.layout.addItem(SPACING(5))

        self.hline = QFrame()
        self.hline.setFrameShape(QFrame.Shape.HLine)
        self.hline.setFrameShadow(QFrame.Shadow.Sunken)
        self.hline.setObjectName("hline")
        self.layout.addWidget(self.hline)

        self.layout.addLayout(self.lower_layout)

    def on_selection(self, identifier):
        if self.currentSkinType:
            self.skintypeItems[self.currentSkinType].setStyleSheet(
                """
                #imageSelector {
                    border-right: 1px solid #909090;
                    border-bottom: 1px solid #909090;
                    border-radius: 10px;
                    background-color: #f3f3f4;
                }
                """
            )

        self.currentSkinType = identifier

        self.skintypeItems[self.currentSkinType].setStyleSheet(
            """
                #imageSelector {
                    border: 2px solid #909090;
                    border-radius: 10px;
                    background-color: #909090;
                    color: white;
                }
                """
        )

    def submit_callback(self):
        self.user_data.data = {
            "age": int(self.inputAge.text()),
            "target": int(self.inputDailyTarget.text()),
            "location": (
                self.inputLocation.text(),
                self.tracker.convert_text_to_gps(self.inputLocation.text()),
            ),
            "skin_type": self.currentSkinType,
        }
        self.user_data.save_user_data()
        self.button_callbacks["back"]()


class LogItem(QWidget):
    def __init__(self, vitamin_d, time, time_duration, location, selection_callback):
        super(LogItem, self).__init__()
        self.vitamin_d = vitamin_d
        self.time = time
        self.time_duration = time_duration
        self.location = location
        self.selection_callback = selection_callback
        self.init_ui()

    def init_ui(self):
        self.mainLayout = QHBoxLayout()

        self.labelTime = QLabel(self.time)
        self.labelTime.setObjectName("logItem__labelTime")

        self.labelTimeDuration = QLabel(str(self.time_duration) + " secs")
        self.labelTimeDuration.setObjectName("logItem__labelTimeDuration")

        self.labelVitaminD = QLabel(str(self.vitamin_d))
        self.labelVitaminD.setObjectName("logItem__labelVitaminD")

        layoutContainerFrame = QFrame()
        layoutContainerFrame.setObjectName("logItem")
        layoutContainer = QVBoxLayout()

        readingsContainer = QHBoxLayout()

        readingsContainer.addWidget(self.labelTime)
        readingsContainer.addItem(SPACING(20))
        readingsContainer.addWidget(self.labelTimeDuration)
        readingsContainer.addItem(SPACING_EX(20))
        readingsContainer.addWidget(self.labelVitaminD)

        layoutContainer.addLayout(readingsContainer)

        readingsLocation = QLabel(f"LOCATION: {self.location}")
        readingsLocation.setObjectName("readingsLocation")

        layoutContainer.addWidget(
            readingsLocation, 0, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )

        layoutContainerFrame.setLayout(layoutContainer)
        layoutContainerFrame.setFixedSize(415, 80)

        self.mainLayout.addWidget(layoutContainerFrame)

        self.setLayout(self.mainLayout)

    def mousePressEvent(self, _):
        self.selection_callback(self.time)


class BodyImageView(QWidget):
    def __init__(self, show_only=True, markers=None):
        super().__init__()

        self.show_only = show_only
        if markers:
            self.markers = markers
        else:
            self.markers = {
                "head": False,
                "neck": False,
                "left_arm_upper": False,
                "left_arm_lower": False,
                "left_palm": False,
                "right_arm_upper": False,
                "right_arm_lower": False,
                "right_palm": False,
                "torso": False,
                "left_leg_upper": False,
                "left_leg_lower": False,
                "left_feet": False,
                "right_leg_upper": False,
                "right_leg_lower": False,
                "right_feet": False,
            }

        self.init_ui()

    def init_ui(self):
        QtGui.QImageReader.setAllocationLimit(0)

        # Create a QGraphicsView and QGraphicsScene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        # Load an image using QPixmap
        pixmap = QtGui.QPixmap("img/human_body.jpg")

        pixmap = pixmap.scaled(300, 700)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        self.btn_dict = {
            "head": (QPushButton(), (135, 20), self.markers["head"]),
            "neck": (QPushButton(), (135, 75), self.markers["neck"]),
            "left_arm_upper": (
                QPushButton(),
                (50, 150),
                self.markers["left_arm_upper"],
            ),
            "left_arm_lower": (
                QPushButton(),
                (35, 250),
                self.markers["left_arm_lower"],
            ),
            "left_palm": (QPushButton(), (25, 350), self.markers["left_palm"]),
            "right_arm_upper": (
                QPushButton(),
                (225, 150),
                self.markers["right_arm_upper"],
            ),
            "right_arm_lower": (
                QPushButton(),
                (240, 250),
                self.markers["right_arm_lower"],
            ),
            "right_palm": (QPushButton(), (250, 350), self.markers["right_palm"]),
            "torso": (QPushButton(), (135, 200), self.markers["torso"]),
            "left_leg_upper": (
                QPushButton(),
                (95, 400),
                self.markers["left_leg_upper"],
            ),
            "left_leg_lower": (
                QPushButton(),
                (80, 550),
                self.markers["left_leg_lower"],
            ),
            "left_feet": (QPushButton(), (45, 650), self.markers["left_feet"]),
            "right_leg_upper": (
                QPushButton(),
                (185, 400),
                self.markers["right_leg_upper"],
            ),
            "right_leg_lower": (
                QPushButton(),
                (200, 550),
                self.markers["right_leg_lower"],
            ),
            "right_feet": (QPushButton(), (235, 650), self.markers["right_feet"]),
        }

        for btn_id, btn in self.btn_dict.items():
            btn[0].setFixedSize(30, 30)
            if self.btn_dict[btn_id][2]:
                self.btn_dict[btn_id][0].setStyleSheet(
                    "border : 2px solid #00008B; background-color: darkorange;"
                )
            else:
                self.btn_dict[btn_id][0].setStyleSheet(
                    "border : 2px solid #00008B; background-color: #00008B;"
                )

            if not self.show_only:
                btn[0].clicked.connect(lambda _, bid=btn_id: self.button_clicked(bid))
            btn_item = self.scene.addWidget(btn[0])
            btn[0].setObjectName("btnBody")
            btn_item.setPos(btn[1][0], btn[1][1])

        # Create a QVBoxLayout for the main widget
        layout = QVBoxLayout()
        layout.addWidget(self.view)

        # Set the layout for the main widget
        self.setLayout(layout)

    def button_clicked(self, btn_id):
        self.mark_button(btn_id)

    def mark_button(self, btn_id):
        if not self.markers[btn_id]:
            self.btn_dict[btn_id][0].setStyleSheet(
                "border : 2px solid #00008B; background-color: darkorange;"
            )
            self.markers[btn_id] = True
        else:
            self.btn_dict[btn_id][0].setStyleSheet(
                "border : 2px solid #00008B; background-color: #00008B;"
            )
            self.markers[btn_id] = False


class LogView(QWidget):
    def __init__(self, user_data, tracker, button_callbacks={}):
        super(LogView, self).__init__()
        self.button_callbacks = button_callbacks
        self.init_ui()
        self.user_data = user_data
        self.current_date = tracker.today
        self.current_log_items = {}
        self.tracker = tracker

        self.setup_callbacks()

        self.load_day_logs()

    def setup_callbacks(self):
        if "back" in self.button_callbacks:
            self.btnBack.clicked.connect(self.button_callbacks["back"])

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setObjectName("layout")

        # --- left layout --- #
        self.layoutLeft = QVBoxLayout()
        self.layoutLeft.setObjectName("layoutLeft")
        self.layoutLeft.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        # Back button
        self.btnBack = QPushButton("BACK")
        self.btnBack.setObjectName("btnBack")
        self.btnBack.setFixedSize(100, 40)
        # self.btnBack.setMaximumSize(QtCore.QSize(100, 16777215))
        self.layoutLeft.addWidget(self.btnBack)

        # ----- Day switcher ----- #
        self.layoutDayBar = QHBoxLayout()
        self.layoutDayBar.setObjectName("layoutDayBar")
        self.btnDayPrev = QPushButton("<")
        self.btnDayPrev.setObjectName("btnDay")
        self.btnDayPrev.setFixedSize(30, 30)
        self.btnDayPrev.clicked.connect(self.previous_date)
        self.layoutDayBar.addWidget(self.btnDayPrev)
        self.labelDay = QLabel("TODAY")
        self.labelDay.setObjectName("labelDay")
        self.layoutDayBar.addWidget(
            self.labelDay, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.btnDayNext = QPushButton(">")
        self.btnDayNext.setObjectName("btnDay")
        self.btnDayNext.setFixedSize(30, 30)
        self.btnDayNext.clicked.connect(self.next_date)
        self.layoutDayBar.addWidget(self.btnDayNext)
        layoutDayBarWidget = QWidget()
        layoutDayBarWidget.setLayout(self.layoutDayBar)
        layoutDayBarWidget.setFixedHeight(50)
        self.layoutLeft.addWidget(layoutDayBarWidget)
        # ------------------------ #

        self.txtDayValue = QLabel("0000 IU")
        self.txtDayValue.setObjectName("txtDayValue")
        self.txtDayValue.setMaximumSize(QtCore.QSize(16777215, 100))
        self.layoutLeft.addWidget(
            self.txtDayValue, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )

        # headings for log entries ...
        self.labelTimeHeading = QLabel("TIME")
        self.labelTimeHeading.setObjectName("logItem__labelTimeHeading")
        self.labelTimeDurationHeading = QLabel("DURATION")
        self.labelTimeDurationHeading.setObjectName("logItem__labelTimeDurationHeading")
        self.labelVitaminDHeading = QLabel("READING")
        self.labelVitaminDHeading.setObjectName("logItem__labelVitaminDHeading")
        headingsContainer = QHBoxLayout()
        headingsContainer.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        headingsContainer.addItem(SPACING(25))
        headingsContainer.addWidget(self.labelTimeHeading)
        headingsContainer.addItem(SPACING(50))
        headingsContainer.addWidget(self.labelTimeDurationHeading)
        headingsContainer.addItem(SPACING(90))
        headingsContainer.addWidget(self.labelVitaminDHeading)
        headingsContainerFrame = QWidget()
        headingsContainerFrame.setLayout(headingsContainer)
        headingsContainerFrame.setFixedSize(415, 40)
        self.layoutLeft.addWidget(
            headingsContainerFrame, QtCore.Qt.AlignmentFlag.AlignHCenter
        )

        # Placeholder for log list
        self.layoutLog = QVBoxLayout()
        self.layoutLog.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layoutLog.setObjectName("layoutLog")
        layoutLogWidget = QWidget()
        layoutLogWidget.setLayout(self.layoutLog)
        # layoutLogWidget.setFixedHeight(420)
        self.layoutLeft.addWidget(layoutLogWidget)

        # Contain layout within widget and set max width
        layoutLeftWidget = QWidget()
        layoutLeftWidget.setLayout(self.layoutLeft)
        layoutLeftWidget.setMaximumSize(QtCore.QSize(480, 16777215))
        self.layout.addWidget(layoutLeftWidget)

        self.btnAddLog = QPushButton("+")
        self.btnAddLog.setObjectName("btnAddLog")
        self.btnAddLog.setFixedSize(50, 50)
        self.btnAddLog.clicked.connect(self.launchAddLogPopup)
        self.layoutLeft.addWidget(
            self.btnAddLog, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
        )

        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.layout.addWidget(self.line)

        # --- right layout --- #
        self.layoutRight = QVBoxLayout()
        self.layoutRight.setObjectName("layoutRight")
        self.labelSkinExposure = QLabel("SKIN EXPOSURE")
        self.labelSkinExposure.setObjectName("labelSkinExposure")
        self.layoutRight.addWidget(
            self.labelSkinExposure, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.bodyImageView = BodyImageView()
        self.layoutRight.addWidget(self.bodyImageView)

        # Contain layout within widget and set max width
        layoutRightWidget = QWidget()
        layoutRightWidget.setLayout(self.layoutRight)
        layoutRightWidget.setMaximumSize(QtCore.QSize(480, 16777215))
        self.layout.addWidget(layoutRightWidget)

        self.setLayout(self.layout)

    def launchAddLogPopup(self):
        pop = LogSunlight("hey", self)
        pop.show()
        ...

    def previous_date(self):
        sorted_dates = self.tracker.sorted_days()
        current_index = sorted_dates.index(self.current_date)
        if current_index > 0:
            self.current_date = sorted_dates[current_index - 1]
            self.load_day_logs()

    def next_date(self):
        sorted_dates = self.tracker.sorted_days()
        current_index = sorted_dates.index(self.current_date)
        if current_index < len(sorted_dates) - 1:
            self.current_date = sorted_dates[current_index + 1]
            self.load_day_logs()

    def load_day_logs(self):
        # make label show TODAY if today
        # hide add logs button if not today
        if self.current_date == self.tracker.today:
            self.labelDay.setText("TODAY")
            self.btnAddLog.show()
        else:
            self.labelDay.setText(self.current_date)
            self.btnAddLog.hide()

        # remove previous entries
        self.current_log_items = {}
        while self.layoutLog.count():
            log_item = self.layoutLog.takeAt(0)
            log_item_widget = log_item.widget()

            if log_item_widget:
                log_item_widget.deleteLater()

        # Set Daily total value on top
        self.txtDayValue.setText(
            str(self.tracker.daily_total(self.current_date)) + " IU"
        )

        for timestamp in self.tracker.sorted_times(self.current_date):
            self.add_log(
                timestamp,
                self.tracker.entries[self.current_date][timestamp]["duration"],
                self.tracker.entries[self.current_date][timestamp]["reading"],
                self.tracker.entries[self.current_date][timestamp]["location"],
            )

        if self.tracker.entries[self.current_date]:
            self.current_time = self.tracker.sorted_times(self.current_date)[0]
            self.display_body_markers()
            # add special indicators to new current time
            self.current_log_items[self.current_time].setStyleSheet(
                """
                #logItem {
                    border: 2px solid #00008B;
                    background-color: #f8f8f8;
                
                }
                """
            )
        else:
            self.current_time = None

    def display_body_markers(self):
        newBodyImageView = BodyImageView(
            markers=self.tracker.entries[self.current_date][self.current_time]["body"]
        )
        self.layoutRight.replaceWidget(self.bodyImageView, newBodyImageView)
        self.bodyImageView.deleteLater()
        self.bodyImageView = newBodyImageView

    def log_selection_callback(self, timestamp):
        # remove special indicators from current time
        self.current_log_items[self.current_time].setStyleSheet(
            """
            #logItem {
                border: none;
                border-bottom: 1px solid #c5c5c5;
                background-color: transparent;
            }
            #logItem:hover {
                border-bottom: 2px solid #00008B;
                background-color: #f8f8f8;
            }
            """
        )

        self.current_time = timestamp

        # add special indicators to new current time
        self.current_log_items[self.current_time].setStyleSheet(
            """
            #logItem {
                border: 2px solid #00008B;
                background-color: #f8f8f8;
            
            }
            """
        )

        self.display_body_markers()

    def add_log(self, timestamp, time_duration, reading, location):
        item = LogItem(
            reading + " IU",
            timestamp,
            time_duration,
            location,
            self.log_selection_callback,
        )
        self.current_log_items[timestamp] = item
        self.layoutLog.addWidget(item)

    def launchAddLogPopup(self):
        pop = LogSunlight("hey", self)
        pop.show()


class UVGraph(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.view = QWidget()
        self.view.setObjectName("graphWidget")

        self.layout = QHBoxLayout()
        self.view.setLayout(self.layout)

        self.figure = Figure()
        self.title = title
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.layout.addWidget(self.canvas)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

    def create_symmetric_distribution(self, peak):
        fractions = [0.2, 0.5, 0.7, 0.9, 1, 0.9, 0.7, 0.5, 0.2]
        return [fraction * peak for fraction in fractions]

    def plot(self, peak):
        hours = [str(i) + ":00" for i in range(8, 12)] + [
            str(i) + ":00" for i in range(12, 17)
        ]
        uv_levels = self.create_symmetric_distribution(float(peak))

        print("HRS", hours)
        print("UV", uv_levels)
        self.ax.clear()
        self.ax.spines["bottom"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.tick_params(axis="both", which="both", length=0)
        self.ax.set_xticklabels(hours, rotation="vertical", fontsize="x-small")
        self.ax.plot(
            hours,
            uv_levels,
            color="darkorange",
            marker="o",
            linestyle="-",
            linewidth=2,
        )
        self.ax.fill_between(hours, uv_levels, color="#e3e3e3", alpha=0.4)
        self.ax.set_title(self.title)

        self.canvas.draw()


class UserLogGraph(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.view = QWidget()
        self.view.setObjectName("graphWidget")

        self.layout = QHBoxLayout()
        self.view.setLayout(self.layout)

        self.figure = Figure()
        self.title = title
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.layout.addWidget(self.canvas)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

    def plot(self, log_labels, log_readings, target=None, cumulative=True):
        categories = log_labels
        readings_bar = log_readings
        cumulative_readings_line = list(accumulate(readings_bar))
        if target:
            target_line = [target] * len(readings_bar)

        self.ax.clear()
        self.ax.bar(categories, readings_bar, color="#00008B")
        self.ax.spines["bottom"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.tick_params(axis="both", which="both", length=0)
        self.ax.set_xticklabels(categories, rotation="vertical", fontsize="x-small")
        if cumulative:
            self.ax.plot(
                categories,
                cumulative_readings_line,
                color="darkorange",
                marker="o",
                linestyle="--",
                linewidth=2,
            )
        if target:
            self.ax.plot(categories, target_line, color="black")
        self.ax.set_title(self.title)

        self.canvas.draw()


class SensorGraph(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.view = QWidget()
        self.view.setObjectName("graphWidget")

        self.layout = QHBoxLayout()
        self.view.setLayout(self.layout)

        self.figure = Figure()
        self.title = title
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.layout.addWidget(self.canvas)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

    def plot(self, x, y):
        self.ax.clear()
        self.ax.spines["bottom"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.tick_params(axis="both", which="both", length=0)
        self.ax.set_xticklabels(x, rotation="vertical", fontsize="x-small")
        self.ax.plot(
            x,
            y,
            color="darkorange",
            linestyle="-",
            linewidth=1,
        )
        self.ax.set_title(self.title)

        self.canvas.draw()


class SensorView(QWidget):
    def __init__(self, button_callbacks={}):
        super().__init__()

        self.button_callbacks = button_callbacks

        self.init_ui()
        self.setup_callbacks()

    def init_ui(self):
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        self.sensor_graph = SensorGraph("BH1750 Light sensor (Lux)")
        self.mainLayout.addWidget(self.sensor_graph)

        self.btnBack = QPushButton("BACK")
        self.btnBack.setFixedHeight(40)

        self.sensor_message = QLabel()
        self.sensor_message.setObjectName("sensorMessage")

        self.mainLayout.addWidget(self.sensor_graph)
        self.mainLayout.addWidget(self.sensor_message)
        self.mainLayout.addItem(SPACING_EX(20, "v"))
        self.mainLayout.addWidget(self.btnBack)

    def setup_callbacks(self):
        if "back" in self.button_callbacks:
            self.btnBack.clicked.connect(self.button_callbacks["back"])


class MainView(QWidget):
    def __init__(self, user_data, tracker, button_callbacks={}):
        super(MainView, self).__init__()
        self.user_data = user_data
        self.button_callbacks = button_callbacks
        self.tracker = tracker
        self.init_ui()

        self.setup_callbacks()

    def setup_callbacks(self):
        if "settings" in self.button_callbacks:
            self.btnSettings.clicked.connect(self.button_callbacks["settings"])
        if "log" in self.button_callbacks:
            self.btnLog.clicked.connect(self.button_callbacks["log"])
        if "sensor" in self.button_callbacks:
            self.btnSensor.clicked.connect(self.button_callbacks["sensor"])

    def init_ui(self):
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # Todays' metrics
        self.txtToday = QLabel("TODAY")
        self.txtToday.setObjectName("mainView__txtToday")
        self.mainLayout.addWidget(
            self.txtToday, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )

        self.todayContainer = QHBoxLayout()

        uvi_max = self.tracker.get_uvi_from_openmeteo(
            self.user_data.data["location"][1]
        )[1]

        self.todayValueTarget = QHBoxLayout()
        self.todayValueTarget.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.txtTodayValueLabel = QLabel("CURRENT:")
        self.txtTodayValueLabel.setObjectName("mainView__txtTodayValueLabel")
        self.txtTodayValue = QLabel(
            str(self.tracker.daily_total(self.tracker.today)) + " IU"
        )
        self.txtTodayValue.setObjectName("mainView__txtTodayValue")

        self.txtTodayTargetValueLabel = QLabel("TARGET:")
        self.txtTodayTargetValueLabel.setObjectName(
            "mainView__txtTodayTargetValueLabel"
        )
        self.txtTodayTargetValue = QLabel(str(self.user_data.data["target"]) + " IU")
        self.txtTodayTargetValue.setObjectName("mainView__txtTodayTargetValue")

        self.todayValueTarget.addWidget(
            self.txtTodayValueLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.todayValueTarget.addItem(SPACING(5))
        self.todayValueTarget.addWidget(
            self.txtTodayValue, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.todayValueTarget.addItem(SPACING(20))
        self.todayValueTarget.addWidget(
            self.txtTodayTargetValueLabel, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.todayValueTarget.addItem(SPACING(5))
        self.todayValueTarget.addWidget(
            self.txtTodayTargetValue, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )

        self.todaySunlightPlot = UVGraph("UVI Today")
        self.todaySunlightPlot.plot(uvi_max[0])
        self.todayLogPlot = UserLogGraph("Exposure Today")
        self.todayLogPlot.plot(
            self.tracker.entries[self.tracker.today].keys(),
            [
                int(val["reading"])
                for val in self.tracker.entries[self.tracker.today].values()
            ],
            self.user_data.data["target"],
        )

        self.todayContainer.addWidget(self.todaySunlightPlot)
        self.todayContainer.addWidget(self.todayLogPlot)

        self.mainLayout.addLayout(self.todayContainer)
        self.mainLayout.addLayout(self.todayValueTarget)

        # Weekly metrics
        self.txtWeekly = QLabel("WEEKLY")
        self.txtWeekly.setObjectName("mainView__txtWeekly")
        self.mainLayout.addWidget(
            self.txtWeekly, 0, QtCore.Qt.AlignmentFlag.AlignHCenter
        )

        self.weeklyContainer = QHBoxLayout()

        self.last_7_day_labels = self.tracker.get_last_7()
        self.last_7_day_values = [
            self.tracker.daily_total(day) for day in self.last_7_day_labels
        ]

        self.txtWeeklyValue = QLabel("0000")
        self.txtWeeklyValue.setObjectName("mainView__txtWeeklyValue")

        self.weeklySunlightPlot = UserLogGraph("UVI Next 7 days")
        next_7_days = [datetime.now() + timedelta(days=i) for i in range(7)]
        next_7_days = [date.strftime("%d/%m") for date in next_7_days]
        self.weeklySunlightPlot.plot(
            next_7_days, uvi_max, target=None, cumulative=False
        )
        self.weeklyLogPlot = UserLogGraph("Exposure Last 7 days")
        self.weeklyLogPlot.plot(
            [
                label.replace("-2023", "").replace("-", "/")
                for label in self.last_7_day_labels
            ],
            self.last_7_day_values,
            self.user_data.data["target"],
            cumulative=False,
        )

        self.weeklyContainer.addWidget(self.weeklySunlightPlot)
        self.weeklyContainer.addWidget(self.weeklyLogPlot)

        self.weeklyContainer.addWidget(self.txtWeeklyValue)
        self.mainLayout.addLayout(self.weeklyContainer)

        self.bottomButtonsLayout = QHBoxLayout()
        self.bottomButtonsLayout.setObjectName("mainView__bottomButtonsLayout")
        self.btnLog = QPushButton("LOG")
        self.btnLog.setObjectName("mainView__btnLog")
        self.btnLog.setFixedSize(100, 40)
        self.bottomButtonsLayout.addWidget(self.btnLog)
        self.bottomButtonsLayout.addItem(SPACING_EX(40))

        self.btnSensor = QPushButton("SENSOR")
        self.btnSensor.setObjectName("mainView__btnSensor")
        self.btnSensor.setFixedSize(100, 40)
        self.bottomButtonsLayout.addWidget(self.btnSensor)
        self.bottomButtonsLayout.addItem(SPACING_EX(40))

        self.btnSettings = QPushButton("SETTINGS")
        self.btnSettings.setObjectName("mainView__btnSettings")
        self.btnSettings.setFixedSize(100, 40)
        self.bottomButtonsLayout.addWidget(self.btnSettings)
        self.mainLayout.addLayout(self.bottomButtonsLayout)

        self.setLayout(self.mainLayout)


class MainWindow(QMainWindow):
    def __init__(self, user_data, tracker, button_callbacks):
        super().__init__()
        self.setWindowTitle("Dsure - Track Vitamin D")
        self.setFixedSize(1000, 950)
        self.user_data = user_data
        self.tracker = tracker
        self.button_callbacks = button_callbacks

        with open("styles.css", "r") as file:
            style_sheet = file.read()
            self.setStyleSheet(style_sheet)

        if self.user_data.data:
            self.change_view("main")
        else:
            self.change_view("settings")

    def change_view(self, key):
        self.sensor_view = None
        if key == "settings":
            settings_view = SettingsView(
                self.user_data, self.tracker, self.button_callbacks
            )
            self.setCentralWidget(settings_view)
        elif key == "main":
            main_view = MainView(self.user_data, self.tracker, self.button_callbacks)
            self.setCentralWidget(main_view)
        elif key == "log":
            log_view = LogView(self.user_data, self.tracker, self.button_callbacks)
            self.setCentralWidget(log_view)
        elif key == "sensor":
            self.sensor_view = SensorView(self.button_callbacks)
            self.setCentralWidget(self.sensor_view)


class LogSunlight(QMainWindow):
    def __init__(self, name, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedSize(600, 1000)
        self.setWindowTitle("Log Sunlight time")

        with open("styles.css", "r") as file:
            style_sheet = file.read()
            self.setStyleSheet(style_sheet)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 20, 40, 20)

        labelStartTime = QLabel("START TIME")
        labelStartTime.setObjectName("labelStartTime")
        self.layout.addWidget(labelStartTime, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.inputStartTime = QTimeEdit()
        self.inputStartTime.setFixedHeight(30)
        self.inputStartTime.setTime(QtCore.QTime.currentTime())
        self.layout.addWidget(self.inputStartTime)

        labelEndTime = QLabel("END TIME")
        labelEndTime.setObjectName("labelEndTime")
        self.layout.addWidget(labelEndTime, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.inputEndTime = QTimeEdit()
        self.inputEndTime.setFixedHeight(30)
        self.inputEndTime.setTime(QtCore.QTime.currentTime())
        self.layout.addWidget(self.inputEndTime)

        labelLocation = QLabel("LOCATION")
        labelLocation.setObjectName("labelLocation")
        self.layout.addWidget(labelLocation, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.inputLocation = QLineEdit()
        self.inputLocation.setFixedHeight(30)
        self.layout.addWidget(self.inputLocation)

        self.bodyImageView = BodyImageView(show_only=False)
        self.layout.addWidget(self.bodyImageView)

        self.buttonLayouts = QHBoxLayout()
        self.buttonCancelLogEntry = QPushButton("CANCEL")
        self.buttonCancelLogEntry.setObjectName("buttonCancelLogEntry")
        self.buttonCancelLogEntry.setFixedHeight(40)
        self.buttonCancelLogEntry.clicked.connect(self.cancelLogEntry)

        self.buttonSubmitLogEntry = QPushButton("SUBMIT")
        self.buttonSubmitLogEntry.setObjectName("buttonSubmitLogEntry")
        self.buttonSubmitLogEntry.setFixedHeight(40)
        self.buttonSubmitLogEntry.clicked.connect(self.submitLogEntry)

        self.buttonLayouts.addWidget(self.buttonCancelLogEntry)
        self.buttonLayouts.addWidget(self.buttonSubmitLogEntry)

        self.layout.addLayout(self.buttonLayouts)

        layout_widget = QWidget()
        layout_widget.setLayout(self.layout)
        self.setCentralWidget(layout_widget)

    def cancelLogEntry(self):
        self.close()

    def submitLogEntry(self):
        # fetch body markers
        # add and fetch location
        gps_location = self.inputLocation.text()
        gps_coordinates = (
            self.parent.tracker.convert_text_to_gps(gps_location)
            if gps_location
            else ""
        )
        if not gps_coordinates:
            gps_coordinates = (
                self.parent.user_data.data["location"][0],
                self.parent.user_data.data["location"][1],
            )
        else:
            gps_coordinates = (gps_location, gps_coordinates)

        log_data = {
            "start_time": f"{self.inputStartTime.time().hour():02d}:{self.inputStartTime.time().minute():02d}",
            "end_time": f"{self.inputEndTime.time().hour():02d}:{self.inputEndTime.time().minute():02d}",
            "location": gps_coordinates,
            "body": self.bodyImageView.markers,
        }
        self.parent.tracker.process_entry(log_data, self.parent.user_data)
        self.parent.load_day_logs()
        self.close()
