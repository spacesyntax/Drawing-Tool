# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DrawingToolDockWidget
                                 A QGIS plugin
 Drawing tool for axial lines, segment lines and unlinks.
                             -------------------
        begin                : 2019-06-16
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Space Syntax Limited
        email                : i.kolovou@spaceyntax.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4.QtCore import QThread, QSettings, pyqtSignal
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from PyQt4 import QtGui, uic
from utility_functions import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'DrawingTool_dockwidget_base.ui'))


class DrawingToolDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(DrawingToolDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        axial_icon = QtGui.QPixmap("/custom_icons/settings.png")
        segment_icon = QtGui.QPixmap("/custom_icons/settings.png")
        unlink_icon = QtGui.QPixmap("/custom_icons/settings.png")
        #self.settingsButton.setIcon(QtGui.QIcon(settings_icon))

        # get settings

        # if axial button checked - update snapping
        self.axialButton.clicked.connect(self.setAxialSnapping)

        # if segment button checked - update snapping
        self.segmentButton.clicked.connect(self.setSegmentSnapping)

        # if unlinks button checked - update snapping
        self.unlinksButton.clicked.connect(self.setUnlinkSnapping)

        self.toleranceSpin.setRange(1, 30)
        self.toleranceSpin.setSingleStep(1)
        self.toleranceSpin.setValue(10)

        self.settings = None

        self.iface = iface

    def update_settings(self):
        if self.settings:
            self.resetSnapping()
        self.settings = [self.networkCombo.currentText(),
                         self.unlinksCombo.currentText(),
                         self.toleranceSpin.value()]
        print 'settings upd', self.settings
        return

    def setAxialSnapping(self):
        # keep button pressed

        # un press other buttons

        # disable previous snapping setting
        self.resetSnapping()

        # snap to nothing
        if self.settings[0] != '':
            proj = QgsProject.instance()
            proj.writeEntry('Digitizing', 'SnappingMode', 'advanced')
            layer = getLayerByName(self.settings[0])
            proj.setSnapSettingsForLayer(layer.id(), False, 0, 0, self.settings[2], True)
        else:
            self.iface.messageBar().pushMessage("Network layer not specified!", QgsMessageBar.CRITICAL, duration=5)
        return

    def setSegmentSnapping(self):
        # disable previous snapping setting
        self.resetSnapping()

        # snap to vertex
        if self.settings[0] != '':
            proj = QgsProject.instance()
            proj.writeEntry('Digitizing', 'SnappingMode', 'advanced')
            layer = getLayerByName(self.settings[0])
            proj.setSnapSettingsForLayer(layer.id(), True, 0, 0, self.settings[2], True)
        else:
            self.iface.messageBar().pushMessage("Network layer not specified!", QgsMessageBar.CRITICAL, duration=5)
        return

    def setUnlinkSnapping(self):
        # disable previous snapping setting if segment
        self.resetSnapping()

        # snap to vertex
        if self.settings[1] != 'no unlinks':
            proj = QgsProject.instance()
            proj.writeEntry('Digitizing', 'SnappingMode', 'advanced')
            layer = getLayerByName(self.settings[1])
            proj.setSnapSettingsForLayer(layer.id(), True, 0, 0, self.settings[2], False)
        else:
            self.iface.messageBar().pushMessage("Unlinks layer not specified!", QgsMessageBar.CRITICAL, duration=5)
        return

    def resetSnapping(self):
        # disable previous snapping setting
        if self.settings[0] != '':
            proj = QgsProject.instance()
            proj.writeEntry('Digitizing', 'SnappingMode', 'advanced')
            layer = getLayerByName(self.settings[0])
            proj.setSnapSettingsForLayer(layer.id(), False, 0, 0, self.settings[2], True)
        if self.settings[1] != 'no unlinks':
            proj = QgsProject.instance()
            proj.writeEntry('Digitizing', 'SnappingMode', 'advanced')
            layer = getLayerByName(self.settings[1])
            proj.setSnapSettingsForLayer(layer.id(), False, 0, 0, self.settings[2], False)
        return

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


