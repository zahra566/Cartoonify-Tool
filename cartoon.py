import sys
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import *
from gui_code import Ui_Form
import cv2
from PIL import Image as im
import numpy as np
import math

class Main(QMainWindow,Ui_Form):

    def __init__(self,*args,**kwargs):
        super(Main, self).__init__(*args,**kwargs)
        self.setupUi(self)

        self.pb1.clicked.connect(lambda: self.openFile())
        self.pb2.clicked.connect(lambda: self.cartoonify())
        self.pb3.clicked.connect(lambda: self.saveImage())
        self.pb4.clicked.connect(lambda: self.on_zoom_in(self))
        self.pb5.clicked.connect(lambda: self.on_zoom_out(self))

    def openFile(self):
        imPath, selectedFilter = QFileDialog.getOpenFileName(self, 'Browse file','E:\\Python files',
                                                             'Image (*.jpg *.png *.bmp *.tiff)')
        self.le1.setText(imPath)
        self.pixmap =QPixmap(imPath)
        if self.pixmap != '':
            self.pb4.setEnabled(True)
            self.pb5.setEnabled(True)
            self.pb2.setEnabled(True)
            self.pb3.setEnabled(True)

        w=self.pixmap.width()
        h=self.pixmap.height()
        if w>=h:
            self.scaled_pixmap = self.pixmap.scaledToWidth(880)
        elif w<h:
            self.scaled_pixmap = self.pixmap.scaledToHeight(500)
        self.lb.setPixmap(self.scaled_pixmap)
        self.scale=1

    def saveImage(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "PNG file (*.png);;JPEG file (*.jpg);;"
                                                                     "TIFF file (*.tiff);;BITMAP file (*.bmp)")

        if path:
            pixmap = self.lb.pixmap()
            pixmap.save(path)

    def on_zoom_in(self, event):
        self.scale *= 2
        self.resize_image()
    def on_zoom_out(self, event):
        self.scale /= 2
        self.resize_image()
    def resize_image(self):
        self.pixmap=self.lb.pixmap()
        size = self.pixmap.size()
        scaled_pixmap = self.pixmap.scaled(self.scale * size)
        self.lb.setPixmap(scaled_pixmap)
    def cartoonify(self):
        # read the image
        imPath=self.le1.text()
        origImage = cv2.imread(imPath)
        #origImage=QImage(self.lb.pixmap())
        h,w=origImage.shape[:2]
        newWidth=int(500/h*w)
        #origImage = cv2.cvtColor(origImage, cv2.COLOR_BGR2RGB)
        # confirm that image is chosen
        if origImage is None:
            print("Can not find any image. Choose appropriate file")
            pass

        grayScaleImage = cv2.cvtColor(origImage, cv2.COLOR_BGR2GRAY)
        smoothGrayScale = cv2.medianBlur(grayScaleImage, 5)
        blocksize=self.bsb.value()
        if math.remainder(blocksize,2)==0:
            blocksize=blocksize+1
        constant=self.ctb.value()
        getEdge = cv2.adaptiveThreshold(src=smoothGrayScale, maxValue=255,adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        thresholdType=cv2.THRESH_BINARY,blockSize=blocksize,C=constant)
        kernel = np.ones((9,9), np.uint8)
        lineTickness=self.ttb.value()
        erosion = cv2.erode(getEdge, kernel, iterations=lineTickness)
        '''cv2.imshow("img",getEdge)
        cv2.waitkey(0)'''
        colorImage = cv2.bilateralFilter(origImage, 9, 300, 300)
        cartoonImage = cv2.bitwise_and(colorImage, colorImage, mask=erosion)
        cartoonImage = cv2.cvtColor(cartoonImage, cv2.COLOR_BGR2RGB)
        #cartoonImage=cv2.resize(cartoonImage,(newWidth,500))

        img=im.fromarray(cartoonImage, mode='RGB')
        img.save('cartoonImage.jpg')
        self.lb.setPixmap(QtGui.QPixmap('cartoonImage.jpg'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setWindowIcon(QtGui.QIcon(':/icons/piecasso.ico'))
    window = Main()
    window.show()
    app.exec_()