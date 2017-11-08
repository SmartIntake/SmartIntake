# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 19:47:10 2017

@author: LEaps & dev.Fallingstar
"""

import sys
import os
import zipfile
import requests as req
from PyQt4 import QtGui, QtCore

base_url = 'http://api.cloudike.hyunhoo.xyz'

links = []

class DragListView(QtGui.QListWidget):
    def __init__(self, type, parent=None):
        super(DragListView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(72, 72))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.emit(QtCore.SIGNAL("dropped"), links)
        else:
            event.ignore()

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.takeItem(self.currentRow())


class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 200, 100)
        self.setWindowTitle("TEST APPLICATION")

        extractAction = QtGui.QAction("&GEt", self)
        extractAction.setShortcut("Ctrl+Q");
        extractAction.setStatusTip('EXIT')

        self.widg_listView = QtGui.QWidget()
        self.widg_login = QtGui.QWidget()

        self.statusBar()
        self.setGUI()

    def setGUI(self):
        self.setDDListGUI()
        self.setLoginGUI()

        self.setCentralWidget(self.widg_login)

    def setDDListGUI(self):
        self.list = DragListView(self)
        self.connect(self.list, QtCore.SIGNAL("dropped"), self.pictureDropped)

        self.layout_main = QtGui.QVBoxLayout()
        self.layout_btns = QtGui.QHBoxLayout()
        self.btn_trash = QtGui.QPushButton("Move all files to trash")
        self.btn_trash.clicked.connect(self.sendToTrash)
        self.btn_clear = QtGui.QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clearList)
        self.layout_btns.addWidget(self.btn_trash)
        self.layout_btns.addWidget(self.btn_clear)

        self.layout_main.addWidget(self.list)
        self.layout_main.addLayout(self.layout_btns)

        self.widg_listView.setLayout(self.layout_main)

    def setLoginGUI(self):
        self.idField = QtGui.QLineEdit(self)

        self.pwField = QtGui.QLineEdit(self)
        self.pwField.setEchoMode(QtGui.QLineEdit.Password)

        self.sendBtn = QtGui.QPushButton("Login", self)
        self.sendBtn.clicked.connect(self.loginAction)
        self.sendBtn.resize(self.sendBtn.minimumSizeHint())

        self.label1 = QtGui.QLabel(self)
        self.label1.setText(' ID: ')
        self.label1.resize(self.label1.minimumSizeHint())

        self.label2 = QtGui.QLabel(self)
        self.label2.setText('PW: ')
        self.label2.resize(self.label1.minimumSizeHint())

        self.layout_main1 = QtGui.QVBoxLayout()
        self.layout_idpw = QtGui.QVBoxLayout()
        self.layout_id = QtGui.QHBoxLayout()
        self.layout_pw = QtGui.QHBoxLayout()

        self.layout_id.addWidget(self.label1)
        self.layout_id.addWidget(self.idField)

        self.layout_pw.addWidget(self.label2)
        self.layout_pw.addWidget(self.pwField)

        self.layout_idpw.addLayout(self.layout_id)
        self.layout_idpw.addLayout(self.layout_pw)

        self.layout_main1.addLayout(self.layout_idpw)
        self.layout_main1.addWidget(self.sendBtn)

        self.widg_login.setLayout(self.layout_main1)

    def loginAction(self):
        api_url = '/api/1/accounts/login/'
        userId = self.idField.text()
        userPassword = self.pwField.text()

        params = {'login': 'email:' + userId, 'password': userPassword}
        res = req.post(base_url + api_url, params=params)
        res.raise_for_status()
        response_data = res.json()
        self.token = response_data['token']

        if len(self.token) == 32:
            print(self.token)
            self.setCentralWidget(self.widg_listView)
            self.fileList = self.getFilesList()['content']

    def sendToTrash(self, evt):
        listItems = self.getItemsFromList()
        for file_name in listItems:
            print("uploading : " + file_name)
            self.send_file(file_name)

    def clearList(self, evt):
        for index in range(0, self.list.count()):
            self.list.takeItem(index)
        for index in range(0, self.list.count()):
            self.list.takeItem(index)

    def pictureDropped(self, l):
        for url in l:
            if os.path.exists(url):
                icon = QtGui.QIcon(url)
                pixmap = icon.pixmap(72, 72)
                icon = QtGui.QIcon(pixmap)
                item = QtGui.QListWidgetItem(url, self.list)
                item.setIcon(icon)
                item.setStatusTip(url)

    def getItemsFromList(self):
        items = []
        for index in range(self.list.count()):
            items.append(self.list.item(index).text())
        return items

    def send_file(self, file_name):
        originPath = file_name
        url = "http://api.cloudike.hyunhoo.xyz/api/1/files/create/"
        headers = {"Mountbit-Auth": self.token}

        if str(file_name).endswith("/"):
            isDirectory = True
        else:
            isDirectory = False

        if isDirectory:
            file_name_split = file_name.split("/")
            file_name = "/".join(file_name_split[0:len(file_name_split)-1])
            file_name = file_name+".zip"
            self.zipFile(dirPath=originPath, zipPath=file_name)
        else:
            file_name = file_name

        short_file_name = str(file_name).split("/")[-1]

        if short_file_name.endswith(".jpg") or short_file_name.endswith(".png") or short_file_name.endswith(".bmp") or short_file_name.endswith(".jpeg"):
            path = "/img/" + short_file_name
        elif short_file_name.endswith(".mp4") or short_file_name.endswith(".avi") or short_file_name.endswith(".mp3") or short_file_name.endswith(".mkv") or short_file_name.endswith(".wmv"):
            path = "/playable/" + short_file_name
        else:
            path = "/etc/" + short_file_name

        data = {"path": path,
                "overwrite": 1,
                "multipart": False}

        res = req.post(url=url, data=data, headers=headers)

        if res.status_code == 200:
            self.upload_file(response=res, file_name=file_name)
        else:
            print("Error while sending file!")

    def upload_file(self, response, file_name):
        json_data = response.json()
        confirm_url = json_data["confirm_url"]
        upload_url = json_data["url"]

        keys = dict(json_data["headers"]).keys()

        data = list()

        for key in keys:
            tmp_tuple = (key, dict(json_data["headers"])[key])
            data.append(tmp_tuple)
        tmp_tuple = ('file', open(file_name, 'rb'))
        data.append(tmp_tuple)
        res = req.post(url=upload_url, files=data)

        if res.status_code == 200 or res.status_code == 201:
            self.file_confirm(confirm_url=confirm_url)
        else:
            print("Error while uploading file!")

    def getFilesList(self):
        url = "http://api.cloudike.hyunhoo.xyz/api/1/metadata/?limit=500&offset=0&order_by=name"
        headers = {"Mountbit-Auth": self.token}
        print(headers)
        res = req.get(url=url, headers=headers)
        print(res)
        if res.status_code == 200:
            print(res.json())
            return res.json()['content']
        else:
            print(res.json())
        

    def file_confirm(self, confirm_url):
        headers = {"Mountbit-Auth": self.token}

        res = req.post(url=confirm_url, headers=headers)
        if res.status_code == 200:
            print("File upload success!")
        else:
            print("Error while confirming file!")

    def zipFile(self, dirPath, zipPath):
        zipf = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(dirPath):
            for file in files:
                zipf.write(os.path.join(root, file))
        zipf.close()

def run():
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    GUI.show()
    app.exec_()


run()