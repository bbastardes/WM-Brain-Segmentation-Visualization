

import vtk
import sys
from ImageSlicing import SliceRenderer
#from GridWindow import *


def twodviews(self,i,filename1,filename2,filename3,filename4,filename5):

    self.ren2 = vtk.vtkRenderer()
    renderers = list()

    # AXIAL
    if i == 0:
        renderers.append(SliceRenderer('axial',filename1,filename2,filename3,filename4,filename5))
        self.vtkWidget2.GetRenderWindow().AddRenderer(self.ren2)
        #self.hl.addWidget(self.vtkWidget2)
        self.iren2 = self.vtkWidget2.GetRenderWindow().GetInteractor()
        self.frame2.setLayout(self.hl)
    
    # SAGITAL
    elif i == 1:
        renderers.append(SliceRenderer('sagittal',filename1,filename2,filename3,filename4,filename5))
        self.vtkWidget3.GetRenderWindow().AddRenderer(self.ren2)
        #self.hl2.addWidget(self.vtkWidget3)
        self.iren2 = self.vtkWidget3.GetRenderWindow().GetInteractor()
        self.frame3.setLayout(self.hl2)

    # CORONAL
    elif i == 2:
        renderers.append(SliceRenderer('coronal',filename1,filename2,filename3,filename4,filename5))
        self.vtkWidget4.GetRenderWindow().AddRenderer(self.ren2)
        #self.hl.addWidget(self.vtkWidget4)
        self.iren2 = self.vtkWidget4.GetRenderWindow().GetInteractor()
        self.frame4.setLayout(self.hl3)
    
    layout = (1,1)

    # set up camera
    camera = vtk.vtkCamera()
    camera.SetViewUp(0., 1., 0.)
    camera.SetPosition(-500, 100, 100)
    camera.SetFocalPoint(100, 100, 100)

    self.ren2.SetBackground(0., 0., 0.)
    self.ren2.SetActiveCamera(camera)

    # set up interactor and window
    self.inter_style = vtk.vtkInteractorStyleTrackballCamera()
    win = CombinedWindow(self,renderers, layout,i)

    #load(self,filename1,10,1,1,256,0.01)

    if i==0:
        self.frame2.setLayout(self.hl)
    elif i == 1:
        self.frame3.setLayout(self.hl2)
    elif i == 2:
        self.frame4.setLayout(self.hl3)
    
    self.show()
    self.iren2.Initialize()
    self.iren2.Start()

class StyleCallback:
    def __init__(self, rens_inters, interactor):
        self.interactor = interactor
        self.map_dict = dict()
        
        for _ren, _inter_style in rens_inters:
            self.map_dict[_ren] = _inter_style

    def __call__(self, obj, ev):
        _x, _y = obj.GetEventPosition()
        render_ref = obj.FindPokedRenderer(_x, _y)
        self.interactor.SetInteractorStyle(self.map_dict[render_ref])

'''
    def load(self,filename1,r,b,g,max,op):
    # set up the source
    src1 = vtk.vtkNIFTIImageReader()
    src1.SetFileName(filename1)
    
    vol_map1 = vtk.vtkGPUVolumeRayCastMapper()
    vol_map1.SetInputConnection(src1.GetOutputPort())
    
    # 4 transfer functions for color and opacity
    funColor = vtk.vtkColorTransferFunction()
    funColor.AddRGBPoint(0, 0., 0., 0.)
    funColor.AddRGBPoint(1, r, g, b)
    
    # 5 assign also an alpha (opacity) gradient to the values
    funAlpha = vtk.vtkPiecewiseFunction()
    funAlpha.AddPoint(0, 0.)
    funAlpha.AddPoint(max, op)
    
    # 6 set up the volume properties
    volProp = vtk.vtkVolumeProperty()
    volProp.SetColor(0, funColor)
    volProp.SetScalarOpacity(0, funAlpha)
    volProp.SetInterpolationTypeToLinear()
    
    # 7 set up the actor
    volAct = vtk.vtkVolume()
    volAct.SetMapper(vol_map1)
    volAct.SetProperty(volProp)
    
    self.ren2.AddActor(volAct)
    '''

def CombinedWindow(self, renderer_list, layout,i):
    assert len(layout) == 2
    assert layout[0] * layout[1] == len(renderer_list)

    self.renderer_list = renderer_list
    self.layout = layout

    def _get_borders(self):
        xl, yl = self.layout
        x_borders = [(_num/xl, (_num+1)/xl) for _num in range(xl)]
        y_borders = [(_num/yl, (_num+1)/yl) for _num in range(yl)]
        borders = list()

        for xb in x_borders:
            for yb in y_borders:
                borders.append((xb[0], yb[0], xb[1], yb[1]))

        return borders
    
    self.ren2 = vtk.vtkRenderer()
    
    if i == 0:
        self.vtkWidget2.GetRenderWindow().AddRenderer(self.ren2)
        self.iren2 = self.vtkWidget2.GetRenderWindow().GetInteractor()
    elif i ==1:
        self.vtkWidget3.GetRenderWindow().AddRenderer(self.ren2)
        self.iren2 = self.vtkWidget3.GetRenderWindow().GetInteractor()
    
    elif i ==2:
        self.vtkWidget4.GetRenderWindow().AddRenderer(self.ren2)
        self.iren2 = self.vtkWidget4.GetRenderWindow().GetInteractor()

    borders = _get_borders(self)

    for _ren, _bord in zip(self.renderer_list, borders):
        _ren.renderer.SetViewport(*_bord)
        if i == 0:
            self.vtkWidget2.GetRenderWindow().AddRenderer(_ren.renderer)
        elif i == 1:
            self.vtkWidget3.GetRenderWindow().AddRenderer(_ren.renderer)
        elif i == 2:
            self.vtkWidget4.GetRenderWindow().AddRenderer(_ren.renderer)

    rens_inters = [(_ren.renderer, _ren.inter_style) for _ren in
            self.renderer_list]

    self.iren2.RemoveObservers('MouseMoveEvent')

    self.iren2.AddObserver('MouseMoveEvent', StyleCallback(rens_inters, self.iren2), 1.)

    self.iren2.Start()

