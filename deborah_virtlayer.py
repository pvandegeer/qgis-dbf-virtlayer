# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CreateVirtualDebLayer

 Maak een virtuele laag aan voor de kopgegevens van Deborah
                             -------------------
        begin                : 2017-05-16
        copyright            : (C) MIT 2017 by P. van de Geer
        email                : -
 ***************************************************************************/
"""
from PyQt4.QtGui import QFileDialog
from qgis.core import QgsMessageLog
from qgis.utils import iface, QgsMessageBar
import textwrap
import os.path


def CreateVritualDebLayer(self):
    # Vraag naar map met Deborah bestanden
    folder = str(QFileDialog.getExistingDirectory(None, "Selecteer Deborah Projectmap", "D:\\Google Drive\\Dev\\QGis Probeersels\\TZD78"))
    if not folder: return

    # Controleer of bestanden bestaan
    project = folder.split('\\')[-1]
    kop_path = os.path.join(folder, project + "_kop.dbf")
    laag_path = os.path.join(folder, project + "_laag.dbf")

    if not (os.path.isfile(kop_path) and os.path.isfile(laag_path)):
        iface.messageBar().pushMessage("Fout", "Kan geen kop en/of laaggegevens vinden in de opgegeven map", level=QgsMessageBar.CRITICAL)
        return

    # Maak virtuele laag aan
    filecontent = getVRTText(self, project)
    filepath = os.path.join(folder, project + "_boringen.vrt")

    outputfile = open(filepath, "w")
    outputfile.write(filecontent)
    outputfile.close()

    # Voeg de virtuele laag toe aan de legenda
    layer = iface.addVectorLayer(filepath, project + "_boringen", "ogr")
    if not layer:
        QgsMessageLog.instance().logMessage('Kon virtuele laag niet laden!', level=QgsMessageLog.WARNING)

    # Voeg ook de laaggegevens toe aan de legenda voor evt. queries
    filepath =  os.path.join(folder, project + "_laag.dbf")
    layer = iface.addVectorLayer(filepath, project + "_lagen", "ogr")
    if not layer:
        QgsMessageLog.instance().logMessage('Kon laaggegevens niet laden!', level=QgsMessageLog.WARNING)

    iface.mapCanvas().setExtent(layer.extent())

# Hulpfunctie om de inhoud van het vrt bestand samen te stellen op basis van de Deborah projectcode
def getVRTText(self, foldername):
    layerfile = foldername + "_kop"
    filecontent = textwrap.dedent("""\
        <OGRVRTDataSource>
            <OGRVRTLayer name="boringen">
                <SrcDataSource relativeToVRT="1">{0}.dbf</SrcDataSource>
                <SrcLayer>{0}</SrcLayer>
                <GeometryType>wkbPoint</GeometryType>
                <LayerSRS>EPSG:28992</LayerSRS>
                <SrcSQL>SELECT * FROM {0} WHERE KXC > 0 AND KYC > 0</SrcSQL>
                <GeometryField encoding="PointFromColumns" x="KXC" y="KYC" z="KMV"/>
                <FID>KBN</FID>
            </OGRVRTLayer>
        </OGRVRTDataSource>
        """)
    return filecontent.replace('{0}', layerfile)
