import vtk
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog, QSlider, QRadioButton, QGroupBox, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

import numpy as np
from random import random
from intersec import Intersection
from glyph_creator import create_glyphs
from threeviews import twodviews
import nibabel as nib
import fsl.wrappers.fslmaths as fsl
from nipype.interfaces.fsl import MultiImageMaths

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setup_ui()

        # button connection
        self.pushButton1.clicked.connect(self.on_button_cliked)
        self.pushButton2.clicked.connect(self.on_button_cliked_2)
        #self.pushButton3.clicked.connect(self.on_button_cliked_3)
        self.pushButton4.clicked.connect(self.on_button_cliked_4)
        self.slider.valueChanged[int].connect(self.changeValueOpacity)

        # setting interactors
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkWidget2 = QVTKRenderWindowInteractor(self.frame2)
        self.vtkWidget3 = QVTKRenderWindowInteractor(self.frame3)
        self.vtkWidget4 = QVTKRenderWindowInteractor(self.frame4)
        
        # layouts to organize the gui
        self.vl = QVBoxLayout()
        self.vl.addWidget(self.vtkWidget)
        self.hl = QHBoxLayout()
        self.hl.addWidget(self.vtkWidget2)
        self.hl2 = QHBoxLayout()
        self.hl2.addWidget(self.vtkWidget3)
        self.hl3 = QHBoxLayout()
        self.hl3.addWidget(self.vtkWidget4)    


    # function to read images and volume rendering t1 and masks
    def read_images(self, filename,r,g,b,t1=0):
        # 2 set up the source
        self.reader_src = vtk.vtkNIFTIImageReader()
        self.reader_src.SetFileName(filename)
        
        # 3 set up the volume mapper
        self.vol_map = vtk.vtkGPUVolumeRayCastMapper()
        self.vol_map.SetInputConnection(self.reader_src.GetOutputPort())

        # 4 transfer functions for color and opacity
        self.funColor = vtk.vtkColorTransferFunction()
        self.funColor.AddRGBPoint(0, 0., 0., 0.)
        self.funColor.AddRGBPoint(1, r, g, b)
        
        # 5 assign also an alpha (opacity) gradient to the values
        if t1 == 1:
            self.funAlpha = vtk.vtkPiecewiseFunction()
            self.funAlpha.AddPoint(0, 0.)
            self.funAlpha.AddPoint(256, 0.01)

        else:
            self.funAlpha = vtk.vtkPiecewiseFunction()
            self.funAlpha.AddPoint(0, 0.)
            self.funAlpha.AddPoint(0.01, 0.01)
            
        self.volProp = vtk.vtkVolumeProperty()
        self.volProp.SetColor(0, self.funColor)
        self.volProp.SetScalarOpacity(0, self.funAlpha)
        self.volProp.SetInterpolationTypeToLinear()

        self.volActor = vtk.vtkVolume()
        self.volActor.SetMapper(self.vol_map)
        self.volActor.SetProperty(self.volProp)
        
        return self.volActor, self.funAlpha
        

    # first renderer loading everything together
    def setup_vtk_renderer(self):
        
        self.volActorT1, self.T1_op = self.read_images(self.filename1,1,1,1,1)
        
        self.filename2 = 'AF_left.nii.gz'
        self.AF_left, _ = self.read_images(self.filename2,255,0,0,0)
        
        self.filename3 = 'AF_right.nii.gz'
        self.AF_right, _ = self.read_images(self.filename3,0,255,0,0)
        
        self.filename4 = 'CST_left.nii.gz'
        self.CST_left, _ = self.read_images(self.filename4,0,0,255,0)
        
        self.filename5 = 'CST_right.nii.gz'
        self.CST_right, _ = self.read_images(self.filename5,255,255,0,0)
        

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        
        self.camera = vtk.vtkCamera()
        self.camera.SetViewUp(0., 1., 1.)
        self.camera.SetPosition(-500, 100, 100)
        self.camera.SetFocalPoint(100, 100, 100)
        
        self.ren.SetBackground(0., 0., 0.)
        self.ren.SetActiveCamera(self.camera)
        self.inter_style = vtk.vtkInteractorStyleTrackballCamera()
        #self.iren.RemoveObservers('MouseMoveEvent')

        self.ren.AddActor(self.volActorT1)
        self.ren.AddActor(self.AF_left)
        self.AF_left.SetVisibility(False)
        self.ren.AddActor(self.AF_right)
        self.AF_right.SetVisibility(False)
        self.ren.AddActor(self.CST_left)
        self.CST_left.SetVisibility(False)
        self.ren.AddActor(self.CST_right)
        self.CST_right.SetVisibility(False)

        self.frame.setLayout(self.vl)
        
        self.show()
        self.iren.Initialize()
        self.iren.Start()


    def setup_ui(self):
        self.resize(1000, 1000)
        
        # central widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setObjectName("centralwidget")

        # big frame
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setStyleSheet("background-color: black;")
        self.frame.setObjectName("frame")
        
        # axial frame
        self.frame2 = QtWidgets.QFrame(self.centralwidget)
        self.frame2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame2.setStyleSheet("background-color: black;")
        self.frame2.setObjectName("frame2")
        
        # sagittal frame
        self.frame3 = QtWidgets.QFrame(self.centralwidget)
        self.frame3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame3.setStyleSheet("background-color: black;")
        self.frame3.setObjectName("frame3")
        
        # coronal frame
        self.frame4 = QtWidgets.QFrame(self.centralwidget)
        self.frame4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame4.setStyleSheet("background-color: black;")
        self.frame4.setObjectName("frame4")
        

        # vertical layout with buttons
        self.verticalLayout = QtWidgets.QGridLayout(self.centralwidget)

        self.verticalLayout.addWidget(self.frame,0,0,18,99)
        self.verticalLayout.addWidget(self.frame2,18,0,33,33)
        self.verticalLayout.addWidget(self.frame3,18,33,33,33)
        self.verticalLayout.addWidget(self.frame4,18,66,33,33)
        self.verticalLayout.setObjectName("horizontalLayout")
	
        # the translate mechanism
        QtCore.QMetaObject.connectSlotsByName(self)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))

        ### BASIC VISUALIZATION
        
        # button to load T1
        self.pushButton1 = QtWidgets.QPushButton(self.centralwidget)
        self.verticalLayout.addWidget(self.pushButton1,1,150)
        #self.verticalLayout.setStretchFactor(self.pushButton1,1)
        self.pushButton1.setText(_translate("MainWindow", "Load T1 image"))
        self.pushButton1.setObjectName("pushButton")
        
        labelop = QtWidgets.QLabel("T1 Opacity")
        labelop.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(labelop, 3,150)

        # slider to control opacity of T1
        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.verticalLayout.addWidget(self.slider, 4,150)
        self.slider.setFocusPolicy(Qt.StrongFocus)
        self.slider.setMinimum(0)
        self.slider.setMaximum(10)
        
        # box with names of tract masks to enable/disable them
        labelmask = QtWidgets.QLabel(self)
        self.verticalLayout.addWidget(labelmask,5,150)
        labelmask.setText("Tract masks")
        self.listWidget = QtWidgets.QListWidget()
        self.verticalLayout.addWidget(self.listWidget, 6,150)
        self.listWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.addItem(QtWidgets.QListWidgetItem("AF_left"))
        self.listWidget.addItem(QtWidgets.QListWidgetItem("AF_right"))
        self.listWidget.addItem(QtWidgets.QListWidgetItem("CST_left"))
        self.listWidget.addItem(QtWidgets.QListWidgetItem("CST_right"))
        self.listWidget.itemClicked.connect(self.masks_selected)

        label3 = QtWidgets.QLabel(self)
        self.verticalLayout.addWidget(label3,10,150)
        label3.setText("Intersection of tract masks")
        
        # button to load the dti
        self.pushButton2 = QtWidgets.QPushButton(self.centralwidget)
        self.verticalLayout.addWidget(self.pushButton2,11,150)
        self.pushButton2.setText(_translate("MainWindow", "Load DTI image"))
        
        ### INTERSECTION
        
        # box to select the mask1 to intersect
        self.cb = QtWidgets.QComboBox(self)
        self.cb.addItem("Select mask 1...")
        self.cb.addItem("AF_left")
        self.cb.addItems(["AF_right", "CST_left", "CST_right"])
        self.cb.currentIndexChanged.connect(self.selectionchange)
        self.verticalLayout.addWidget(self.cb,12,150)
        self.verticalLayout.addItem(QtWidgets.QSpacerItem(12, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.show()
    
        # box to select the mask2 to intersect
        self.cb2 = QtWidgets.QComboBox(self)
        self.cb2.addItem("Select mask 2...")
        self.cb2.addItem("AF_left")
        self.cb2.addItem("AF_right")
        self.cb2.addItems(["CST_left", "CST_right"])
        self.cb2.currentIndexChanged.connect(self.selectionchange)
        self.verticalLayout.addWidget(self.cb2,13,150)
        self.verticalLayout.addItem(QtWidgets.QSpacerItem(13, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.show()
        
        # box to chose the geometry of the glyphs
        self.cb3 = QtWidgets.QComboBox(self)
        self.cb3.addItem("Type of glyph geometry...")
        self.cb3.addItem("sphere")
        self.cb3.addItem("arrow")
        self.cb3.currentIndexChanged.connect(self.selectionchange2)
        self.verticalLayout.addWidget(self.cb3,14,150)
        self.verticalLayout.addItem(QtWidgets.QSpacerItem(14, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.show()
        
        #button to perform the glyph representation
        self.pushButton4 = QtWidgets.QPushButton()
        self.verticalLayout.addWidget(self.pushButton4,15,150)
        self.pushButton4.setText(_translate("MainWindow", "Glyph"))
    
        # button to enable stereo
        radiobutton = QRadioButton("Stereo")
        radiobutton.setChecked(False)
        radiobutton.toggled.connect(self.onClicked)
        self.verticalLayout.addWidget(radiobutton, 30, 150)

    # change opacity of T1
    def changeValueOpacity(self, value):
        self.opacity = value/1000
        self.T1_op.AddPoint(256, self.opacity)
        self.vtkWidget.Render()
    
    # open files 1
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)

        self.filename1 = fileName
    
    # open files 2
    def openFileNameDialog2(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        
        self.filenamedti = fileName
    
    # to load T1 and dti
    def on_button_cliked(self):
        self.openFileNameDialog()
        self.setup_vtk_renderer()
    def on_button_cliked_2(self):
        self.openFileNameDialog2()
    
    
        # enable/disable masks
    def masks_selected(self):
        items = self.listWidget.selectedItems()
        x = []
        for i in range(len(items)):
            x.append(str(self.listWidget.selectedItems()[i].text()))
        if 'AF_left' in x:
            self.AF_left.SetVisibility(True)
            self.filename2 = 1
        else:
            self.AF_left.SetVisibility(False)
            self.filename2 = 0
        
        if 'AF_right' in x:
            self.AF_right.SetVisibility(True)
            self.filename3 = 1
        else:
            self.AF_right.SetVisibility(False)
            self.filename3 = 0
        
        if 'CST_left' in x:
            self.CST_left.SetVisibility(True)
            self.filename4 = 1
        else:
            self.CST_left.SetVisibility(False)
            self.filename4 = 0
        
        if 'CST_right' in x:
            self.CST_right.SetVisibility(True)
            self.filename5 = 1
        else:
            self.CST_right.SetVisibility(False)
            self.filename5 = 0

        for i in range(3):
            twodviews(self,i,self.filename1,self.filename2,self.filename3,self.filename4,self.filename5)
    
    # intersection
    def selectionchange(self):
        self.mask1 = self.cb.currentText()
        self.mask2 = self.cb2.currentText()
        print("mask1 = " +self.mask1)
        print("mask2 = " +self.mask2)
    
        if self.mask1 != 'Select mask 1...' and self.mask2 != 'Select mask 2...':
            intersec = Intersection(self.mask1,self.mask2)

            dti = nib.load(self.filenamedti)
            dti_data = dti.get_data()
            
            #pre_glyph = np.full((145,174,145,6), 0)

            maths = MultiImageMaths()
            maths.run(in_file='dti.nii',op_string = ' -mul %s', operand_files= 'intersec_img.nii.gz', out_file='pre_glyph_img.nii.gz')
            
            filename1=0
            filename2=0
            filename3=0
            filename4=0
            filename5=0
            
            if self.mask1 == 'AF_left': filename2 = 1
            if self.mask2 == 'AF_left': filename2 = 1
            if self.mask1 == 'AF_right': filename3 = 1
            if self.mask2 == 'AF_right': filename3 = 1
            if self.mask1 == 'CST_left': filename4 = 1
            if self.mask2 == 'CST_left': filename4 = 1
            if self.mask1 == 'CST_right': filename5 = 1
            if self.mask2 == 'CST_right': filename5 = 1
            
            for i in range(3):
                twodviews(self,i,self.filename1,filename2,filename3,filename4,filename5)

    # to select glyph geoemtry
    def selectionchange2(self):
        self.type = self.cb3.currentText()

    # glyph representation
    def on_button_cliked_4(self):
        create_glyphs(self,'pre_glyph_img.nii.gz',self.filename1, self.mask1, self.mask2,self.type,size='full')

    # STEREO
    def onClicked(self):
        radioButton = self.sender()
        win = self.vtkWidget.GetRenderWindow()
        win.GetStereoCapableWindow()
        if radioButton.isChecked():
            win = self.vtkWidget.GetRenderWindow()
            win.GetStereoCapableWindow()
            win.StereoCapableWindowOn()
            win.SetStereoRender(1)
            win.SetStereoTypeToAnaglyph()
        else:
            win.SetStereoRender(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
