# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telaPrincipal.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHeaderView,
    QMainWindow, QMenu, QMenuBar, QSizePolicy,
    QSpacerItem, QTreeView, QWidget)
import iconsPrincipal_rc

class Ui_telaPrincipal(object):
    def setupUi(self, telaPrincipal):
        if not telaPrincipal.objectName():
            telaPrincipal.setObjectName(u"telaPrincipal")
        telaPrincipal.resize(900, 550)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(telaPrincipal.sizePolicy().hasHeightForWidth())
        telaPrincipal.setSizePolicy(sizePolicy)
        telaPrincipal.setMinimumSize(QSize(900, 550))
        telaPrincipal.setMaximumSize(QSize(900, 550))
        font = QFont()
        font.setBold(True)
        telaPrincipal.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icons/icons/logoSpike.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        telaPrincipal.setWindowIcon(icon)
        telaPrincipal.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")
        self.actionUTILITARIOS = QAction(telaPrincipal)
        self.actionUTILITARIOS.setObjectName(u"actionUTILITARIOS")
        self.centralwidget = QWidget(telaPrincipal)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setFont(font)
        self.centralwidget.setStyleSheet(u"QWidget{\n"
"background-color: transparent;\n"
"}")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"QFrame{\n"
"color: rgb(255, 255, 255);\n"
"}")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 3, 3)
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(120, 0))
        self.frame_2.setMaximumSize(QSize(120, 16777215))
        self.frame_2.setStyleSheet(u"QToolButton{\n"
"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);\n"
"}")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout_4 = QGridLayout(self.frame_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_2, 1, 0, 1, 1)

        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setStyleSheet(u"QFrame{\n"
"background-color: rgb(124, 124, 124);\n"
"}")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(3, 3, 3, 3)
        self.treeView = QTreeView(self.frame_3)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setMaximumSize(QSize(16777215, 16777215))
        self.treeView.setStyleSheet(u"QTreeView{\n"
"background-color: rgb(255, 255, 255);\n"
"}")
        self.treeView.setFrameShape(QFrame.NoFrame)

        self.gridLayout_3.addWidget(self.treeView, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_3, 1, 1, 1, 1)

        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(0, 50))
        self.frame_4.setMaximumSize(QSize(16777215, 50))
        self.frame_4.setFrameShape(QFrame.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Raised)

        self.gridLayout_2.addWidget(self.frame_4, 0, 0, 1, 2)


        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        telaPrincipal.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(telaPrincipal)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 21))
        self.menubar.setFont(font)
        self.menuFERRAMENTAS = QMenu(self.menubar)
        self.menuFERRAMENTAS.setObjectName(u"menuFERRAMENTAS")
        self.menuFERRAMENTAS.setFont(font)
        telaPrincipal.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFERRAMENTAS.menuAction())
        self.menuFERRAMENTAS.addAction(self.actionUTILITARIOS)

        self.retranslateUi(telaPrincipal)

        QMetaObject.connectSlotsByName(telaPrincipal)
    # setupUi

    def retranslateUi(self, telaPrincipal):
        telaPrincipal.setWindowTitle(QCoreApplication.translate("telaPrincipal", u"Oganizer of Archives", None))
        self.actionUTILITARIOS.setText(QCoreApplication.translate("telaPrincipal", u"UTILITARIOS", None))
        self.menuFERRAMENTAS.setTitle(QCoreApplication.translate("telaPrincipal", u"FERRAMENTAS", None))
    # retranslateUi

