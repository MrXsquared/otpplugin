# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OpenTripPlannerPlugin
                                 A QGIS plugin
 This plugin makes OpenTripPlanner functionalities accessible in QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-10-21
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Mario Königbauer
        email                : mkoenigb@hm.edu
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
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from PyQt5.QtNetwork import  QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QCoreApplication, QUrl
from qgis.core import *
from qgis.utils import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .otp_plugin_dialog import OpenTripPlannerPluginDialog
import os.path
import requests
from requests.exceptions import HTTPError


class OpenTripPlannerPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'OpenTripPlannerPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&OpenTripPlanner Plugin')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('OpenTripPlannerPlugin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/otp_plugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'OpenTripPlanner Plugin'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&OpenTripPlanner Plugin'),
                action)
            self.iface.removeToolBarIcon(action)
 
    # https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/settings.html 
    def store_variables(self):
        s = QgsSettings()
        s.setValue("otp_plugin/GeneralSettings_ServerURL", "http://localhost:8080/otp/routers/test/")
        #s.setValue("otp_plugin/myint",  10)
        #s.setValue("otp_plugin/myreal", 3.14)
        #Just testing stuff below...
        #print(s)
        self.iface.messageBar().pushMessage(
        "Success", "Function store_variables! Var: ",
        level=Qgis.Success, duration=3)   
    def read_variables(self):
        s = QgsSettings()
        ServerURL = s.value("myplugin/mytext", "http://localhost:8080/otp/routers/test/")
        #myint  = s.value("myplugin/myint", 123)
        #myreal = s.value("myplugin/myreal", 2.71)
        #nonexistent = s.value("myplugin/nonexistent", None)
        print(mytext)
        print(myint)
        print(myreal)
        print(nonexistent)
  
    # Open File Dialog when
    def select_output_folder(self):
        #foldername, _filter = QFileDialog.getExistingDirectory(self.dlg, "Open Directory","",ShowDirsOnly)
        filename, _filter = QFileDialog.getSaveFileName(self.dlg, "Select output file ","", '*.*')
        self.dlg.GeneralSettings_SavePath.setText(filename)

    def Isochrones_RequestIsochrones(self):
        layers = QgsProject.instance().layerTreeRoot().children() # Fetch the currently loaded layers
        selectedLayerIndex = self.dlg.Isochrones_SelectInputLayer.currentIndex() # Fetch the selected layer in combobox
        selectedLayer = layers[selectedLayerIndex].layer() # Use the in combobox selected layer
        fieldnames = [field.name() for field in selectedLayer.fields()] # Receive fieldnames from selected layer
        #selectedLayer = iface.activeLayer() #Uses the currently selected layer in layerslist from qgis browser
        features = selectedLayer.getFeatures()
        ServerURL = self.dlg.GeneralSettings_ServerURL
        self.dlg.Isochrones_WalkSpeed_Override.setVectorLayer(selectedLayer)
        self.dlg.Isochrones_WalkSpeed_Override.updateFieldLists()        
        
        for feature in features:
            # retrieve every feature with its geometry and attributes
            print("Feature ID: ", feature.id())
            # fetch geometry
            # show some information about the feature geometry
            geom = feature.geometry()
            pointgeom = geom.asPoint() #Read Point geometry
            x = pointgeom.x() #Read X-Value
            y = pointgeom.y() #Read Y-Value
            print("PointX: ", x, " | PointY: ", y)
            
            # fetch attributes
            attrs = feature.attributes()
            # attrs is a list. It contains all the attribute values of this feature
            print(attrs)
            
            #Check where to gather attributes from: GUI or Layer?
            #WalkSpeed
            if self.dlg.Isochrones_WalkSpeed_Override.isActive() == True:
                Isochrones_WalkSpeed, IrrelevantSuccessStorage = self.dlg.Isochrones_WalkSpeed_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_WalkSpeed = self.dlg.Isochrones_WalkSpeed.value() #Receiving Value from GUI: SpinBox
            
            #Date
            if self.dlg.Isochrones_Date_Override.isActive() == True:
                Isochrones_Date, IrrelevantSuccessStorage = self.dlg.Isochrones_Date_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_Date = self.dlg.Isochrones_Date.date().toString("yyyy-MM-dd") #Receiving Value from GUI: SpinBox
            
            #Time
            if self.dlg.Isochrones_Time_Override.isActive() == True:
                Isochrones_Time, IrrelevantSuccessStorage = self.dlg.Isochrones_Time_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_Time = self.dlg.Isochrones_Time.time().toString("HH:mm:ss")  #Receiving Value from GUI: SpinBox
            
            #ArriveBy
            if self.dlg.Isochrones_ArriveBy_Override.isActive() == True:
                Isochrones_ArriveBy, IrrelevantSuccessStorage = self.dlg.Isochrones_ArriveBy_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_ArriveBy = self.dlg.Isochrones_ArriveBy.checkState() #Receiving Value from GUI: SpinBox
            
            #MaxWaitingTime
            if self.dlg.Isochrones_MaxWaitingTime_Override.isActive() == True:
                Isochrones_MaxWaitingTime, IrrelevantSuccessStorage = self.dlg.Isochrones_MaxWaitingTime_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_MaxWaitingTime = self.dlg.Isochrones_MaxWaitingTime.value() #Receiving Value from GUI: SpinBox
            
            #MaxTransfers
            if self.dlg.Isochrones_MaxTransfers_Override.isActive() == True:
                Isochrones_MaxTransfers, IrrelevantSuccessStorage = self.dlg.Isochrones_MaxTransfers_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_MaxTransfers = self.dlg.Isochrones_MaxTransfers.value() #Receiving Value from GUI: SpinBox
            
            #MaxWalkDistance
            if self.dlg.Isochrones_MaxWalkDistance_Override.isActive() == True:
                Isochrones_MaxWalkDistance, IrrelevantSuccessStorage = self.dlg.Isochrones_MaxWalkDistance_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_MaxWalkDistance = self.dlg.Isochrones_MaxWalkDistance.value() #Receiving Value from GUI: SpinBox
            
            #MaxOffroadDistance
            if self.dlg.Isochrones_MaxOffroadDistance_Override.isActive() == True:
                Isochrones_MaxOffroadDistance, IrrelevantSuccessStorage = self.dlg.Isochrones_MaxOffroadDistance_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_MaxOffroadDistance = self.dlg.Isochrones_MaxOffroadDistance.value() #Receiving Value from GUI: SpinBox
            
            #Isochrones Interval
            if self.dlg.Isochrones_Interval_Override.isActive() == True:
                Isochrones_Interval, IrrelevantSuccessStorage = self.dlg.Isochrones_Interval_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_Interval = self.dlg.Isochrones_Interval.toPlainText() #Receiving Value from GUI: SpinBox
            
            #Transportation Mode
            if self.dlg.Isochrones_TransportationMode_Override.isActive() == True:
                Isochrones_TransportationMode, IrrelevantSuccessStorage = self.dlg.Isochrones_TransportationMode_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_TransportationMode = self.dlg.Isochrones_TransportationMode.toPlainText() #Receiving Value from GUI: SpinBox
            
            #Additional Parameters
            if self.dlg.Isochrones_AdditionalParameters_Override.isActive() == True:
                Isochrones_AdditionalParameters, IrrelevantSuccessStorage = self.dlg.Isochrones_AdditionalParameters_Override.toProperty().value(QgsExpressionContext()) #Receiving Value from GUI: DataDefinedOverride
            else:
                Isochrones_AdditionalParameters = self.dlg.Isochrones_AdditionalParameters.toPlainText() #Receiving Value from GUI: SpinBox
                
            #Example URL: http://localhost:8080/otp/routers/ttc/isochrone?fromPlace=43.637,-79.434&mode=WALK,TRANSIT&date=11-14-2017&time=8:00am&maxWalkDistance=500&cutoffSec=1800&cutoffSec=3600
            #Concat URL and convert to string
            isochrone_url = (str(ServerURL) + "isochrone?" + #
                            "fromPlace=" + str(y) + "," + str(x) + #
                            "&mode=" + str(Isochrones_TransportationMode) + #
                            "&date=" + str(Isochrones_Date) + #
                            "&time=" + str(Isochrones_Time) + #
                            "&walkSpeed=" + str(Isochrones_WalkSpeed) + #
                            "&maxWalkDistance=" + str(Isochrones_MaxWalkDistance) + #
                            "&maxWaitingTime=" + str(Isochrones_MaxWaitingTime) + #
                            "&maxTransfers=" + str(Isochrones_MaxTransfers) + #
                            "&maxOffroadDistance=" + str(Isochrones_MaxOffroadDistance) + #
                            "&cutoffsec=" + #Isochrones_Interval.strip()
                            "&cutoffsec=" + #
                            Isochrones_AdditionalParameters # Additional Parameters entered as OTP-Readable string -> User responsibility
                            )
                            
            #Just testing stuff below...
            print(self.dlg.Isochrones_WalkSpeed_Override.vectorLayer())
            print(isochrone_url)
            self.iface.messageBar().pushMessage(
            "Success", "Function Isochrones_RequestIsochrones run! URL: " + isochrone_url + " - " + str(fieldnames) + str(selectedLayer) + str(self.dlg.Isochrones_WalkSpeed_Override.vectorLayer()),
            level=Qgis.Success, duration=3)   

            #Testing Requests
            url = 'https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql'
            r = requests.get(url, headers={"content-type":"application/json"})
            with open('D:/Users/Mario/Desktop/cat3.jpg', 'wb') as f:
                f.write(r.content)
            # Retrieve HTTP meta-data
            print(r.status_code)
            print(r.headers['content-type'])
            print(r.encoding)
            requeststatuscode = str(r.status_code)
            requestheader = str(r.headers['content-type'])
            requestencoding = str(r.encoding)
            responseheader = str('response is not defined - does not work')       
            self.iface.messageBar().pushMessage(
            "Success", "HTTP GET Request via Python requests: " + "requeststatus: " + requeststatuscode + " requestheader: " + requestheader + " requestencoding: " + requestencoding + " responseheader: " + responseheader + " url: " + url,
            level=Qgis.Success, duration=3)             
    
    def run(self):
        """Run method that performs all the real work"""

        
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = OpenTripPlannerPluginDialog()
            self.dlg.GeneralSettings_SelectSavePath.clicked.connect(self.select_output_folder) #Open file dialog when hitting button
            self.dlg.Isochrones_RequestIsochrones.clicked.connect(self.Isochrones_RequestIsochrones) #Call Isochrones_RequestIsochrones function when clicking on RequestIsochrones button
            self.dlg.GeneralSettings_Save.clicked.connect(self.store_variables) #Call store_Variables function when clicking on save button
            
            
        # Fetch the currently loaded layers
        layers = QgsProject.instance().layerTreeRoot().children()
        # Clear the contents of the comboBox from previous runs
        self.dlg.Isochrones_SelectInputLayer.clear()
        # Populate the comboBox with names of all the loaded layers
        self.dlg.Isochrones_SelectInputLayer.addItems([layer.name() for layer in layers])
        
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            Isochrones_RequestIsochrones()
            print("test!")
