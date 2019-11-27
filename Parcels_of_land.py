"""
/***************************************************************************
  Parcels_of_land.py

  QGIS plugin that adds a parcel to polygon layer using uldk.gugik.gov.pl service.
  --------------------------------------
  Date : 26.11.2019
  Copyright: (C) 2019 by Piotr Michałowski
  Email: piotrm35@hotmail.com
/***************************************************************************
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as published
 * by the Free Software Foundation.
 *
 ***************************************************************************/
"""


SCRIPT_TITLE = 'Parcels of land'
SCRIPT_NAME = 'Parcels_of_land'
SCRIPT_VERSION = '0.1.1'
GENERAL_INFO = """
author: Piotr Michałowski, Olsztyn, woj. W-M, Poland
piotrm35@hotmail.com
license: GPL v. 2
work begin: 26.11.2019
"""


import os
import urllib.request
from PyQt5 import QtGui, QtWidgets, uic
from qgis.core import *
from qgis.utils import iface
from .Setup import Setup


BASE_ID_URL = 'https://uldk.gugik.gov.pl/?request=GetParcelById&id='
URL_SUFFIX = '&result=geom_wkt&srid='
PARCEL_FIELD_NAME = 'parcel'


class Parcels_of_land(QtWidgets.QMainWindow):


    def __init__(self, iface):
        super(Parcels_of_land, self).__init__()
        self.iface = iface
        self.base_path = os.sep.join(os.path.realpath(__file__).split(os.sep)[0:-1])
        self.icon = QtGui.QIcon(os.path.join(self.base_path, 'img', 'Parcels_of_land_ICON.png'))
        self.output_layer = None


    #----------------------------------------------------------------------------------------------------------------
    # plugin methods:
    

    def initGui(self):
        self.action = QtWidgets.QAction(self.icon, SCRIPT_TITLE, self.iface.mainWindow())
        self.action.setObjectName(SCRIPT_NAME + '_action')
        self.iface.addToolBarIcon(self.action)
        self.action.triggered.connect(self.run)
        uic.loadUi(os.path.join(self.base_path, 'ui', 'Parcels_of_land.ui'), self)
        self.setWindowTitle(SCRIPT_TITLE + ' v. ' + SCRIPT_VERSION)
        self.Refresh_map_pushButton.clicked.connect(self.Refresh_map_pushButton_clicked)
        self.Refresh_map_pushButton.setEnabled(False)
        self.Refresh_list_pushButton.clicked.connect(self.Refresh_list_pushButton_clicked)
        self.About_pushButton.clicked.connect(self.about_pushButton_clicked)
        self.Input_parcel_list_textEdit.textChanged.connect(self.Input_parcel_list_textEdit_textChanged)
        
        
    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.action.triggered.disconnect(self.run)
        self.Refresh_map_pushButton.clicked.disconnect(self.Refresh_map_pushButton_clicked)
        self.Refresh_list_pushButton.clicked.disconnect(self.Refresh_list_pushButton_clicked)
        self.About_pushButton.clicked.disconnect(self.about_pushButton_clicked)
        self.Input_parcel_list_textEdit.textChanged.disconnect(self.Input_parcel_list_textEdit_textChanged)


    def run(self):
        self.set_output_layer()
        if self.output_layer is not None:
            self.show()
        

    #----------------------------------------------------------------------------------------------------------------
    # input widget methods
    

    def Refresh_map_pushButton_clicked(self):
        self.Refresh_map_pushButton.setEnabled(False)
        self.output_layer.startEditing()
        parcel_list = self.get_parcel_list()
        if parcel_list:
            map_list = self.gat_map_list()
            for row in parcel_list:
                if row not in map_list:
                    self.add_parcel_by_id(row)
                else:
                    map_list.remove(row)
            if map_list:
                to_delete_fid_list = self.get_features_id_list(map_list)
                res = self.output_layer.dataProvider().deleteFeatures(to_delete_fid_list)
        else:
            print('Refresh_map_pushButton_clicked: there are no input data.')
        self.output_layer.commitChanges()


    def Refresh_list_pushButton_clicked(self):
        self.Refresh_list_pushButton.setEnabled(False)
        map_list = self.gat_map_list()
        if map_list:
            self.Input_parcel_list_textEdit.setPlainText('\n'.join(map_list))
        else:
            print('Refresh_list_pushButton_clicked: there are no input data.')
        self.Refresh_list_pushButton.setEnabled(True)
                

    def about_pushButton_clicked(self):
        QtWidgets.QMessageBox.information(self, SCRIPT_TITLE, SCRIPT_TITLE + ' v. ' + SCRIPT_VERSION + '\n' + GENERAL_INFO)


    def Input_parcel_list_textEdit_textChanged(self):
        self.Refresh_map_pushButton.setEnabled(True)


    #----------------------------------------------------------------------------------------------------------------
    # work methods:


    def set_output_layer(self):
        try:
            self.output_layer = QgsProject.instance().mapLayersByName(Setup.OUTPUT_POLYGON_LAYER_NAME)[0]
        except:
            self.output_layer = None
            QtWidgets.QMessageBox.critical(self, SCRIPT_TITLE, "There is no '" + str(Setup.OUTPUT_POLYGON_LAYER_NAME) + "' layer.")
    

    def add_parcel_by_id(self, parcel_id):
        parcel_id_list = parcel_id.split('-')
        if len(parcel_id_list) == 2:
            geodetic_region = parcel_id_list[0]
            parcel_suffix = parcel_id_list[1]
            n = 4 - len(geodetic_region)
            url = BASE_ID_URL + Setup.PLACE_ID + '.' + '0' * n + geodetic_region + '.' + parcel_suffix + URL_SUFFIX + Setup.EPSG_ID
            try:
                with urllib.request.urlopen(url) as response:
                   result = response.read()
            except:
                print('ERROR(' + parcel_id + '):')
                print('url = ' + url + '\n')
                return
            try:
                result = result.decode()
            except:
                print('ERROR(' + parcel_id + '):')
                print('result = ' + str(result) + '\n')
                return
            result_list = result.split('\n')
            if result_list[0].strip() == '0' and len(result_list) >= 2:
                result_list = result_list[1].split(';')
                if len(result_list) >= 2:
                    parcel_wkt = result_list[1].strip()
                    output_geom = QgsGeometry.fromWkt(parcel_wkt)
                    output_feat = QgsFeature(self.output_layer.fields())
                    output_feat.setGeometry(output_geom)
                    self.set_attribute_if_exist(output_feat, PARCEL_FIELD_NAME, parcel_id)
                    (res, outFeats) = self.output_layer.dataProvider().addFeatures([output_feat])
                    print('SUCCESS(' + parcel_id + ')')
                    return
                else:
                    print('ERROR(' + parcel_id + '):')
                    print('len(result_list)(2) = ' + str(len(result_list)) + '\n')
                    return
            else:
                print('ERROR(' + parcel_id + '):')
                print('result_list[0] = ' + str(result_list[0]))
                print('len(result_list) = ' + str(len(result_list)) + '\n')
                return
        else:
            print('ERROR(' + parcel_id + '):')
            print('len(parcel_id_list) = ' + str(len(parcel_id_list)) + '\n')
            

    def set_attribute_if_exist(self, qgs_feature, attribute_name, attribute_value):
        try:
            qgs_feature.setAttribute(attribute_name, attribute_value)
        except:
            print("Can't set attribute: " + attribute_name)


    def get_parcel_list(self):
        data = self.Input_parcel_list_textEdit.toPlainText()
        output_list = data.split('\n')
        for i in range(len(output_list)):
            output_list[i] = output_list[i].strip()
        return output_list


    def gat_map_list(self):
        output_list = []
        features = self.output_layer.getFeatures()
        for feature in features:
            output_list.append(feature[PARCEL_FIELD_NAME])
        return output_list
    

    def get_features_id_list(self, input_list):
        output_list = []
        for row in input_list:
            exp = QgsExpression(PARCEL_FIELD_NAME + " = '" + row + "'")
            request = QgsFeatureRequest(exp)
            for feature in self.output_layer.getFeatures(request):
                output_list.append(feature.id())
        return output_list
            

    #----------------------------------------------------------------------------------------------------------------






    
