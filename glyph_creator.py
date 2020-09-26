import vtk
import nibabel as nib


# in case we want to select the coordinates instead of plotting all volume
# def create_glyphs(self,img,mask1,mask2,xmin=0,xmax=0,ymin=0,ymax=0,zmin=0,zmax=0,size=0):


def create_glyphs(self,img,filename1,mask1,mask2, gtype,size=0):

    # LOAD DATA
    img = nib.load(img)
    img_data = img.get_data()
    img = img_data

    points = vtk.vtkPoints()
    dbar = vtk.vtkDoubleArray()
    dbar.SetNumberOfComponents(9)

    counter = -1

    if size == 'full':
        for i in range(50,img.shape[0]):
            for j in range(50,img.shape[1]):
                for k in range(50,img.shape[2]):
                    if str(img_data[i,j,k,0]) != 'nan' and str(img_data[i,j,k,0]) != 0 and counter<1000000:
                        counter = counter + 1
                        points.InsertPoint(counter, i,j, -k)
                        x = img_data[i,j,k,0:]
                        #print(counter)
                        dbar.InsertTuple9(counter,x[0],x[3],x[4],x[3],x[1],x[5],x[4],x[5],x[2])

    '''
    else:
        for i in range(xmin,xmax):
            for j in range(ymin,ymax):
                for k in range(zmin,zmax):
                    if str(img_data[i][j][k][0]) != 'nan' and counter<50000:
                        counter = counter + 1
                        points.InsertPoint(counter, i, j, -k)
                        x = img_data[i][j][k][0:]
                        print(counter)
                        dbar.InsertTuple9(counter,x[0],x[3],x[4],x[3],x[1],x[5],x[4],x[5],x[2])
    '''

    # GLYPHS GENERATION
    # Polydata
    indata = vtk.vtkPolyData()
    indata.SetPoints(points)
    indata.GetPointData().SetTensors(dbar)

    # different geometries
    if gtype == 'sphere':
        src = vtk.vtkSphereSource()
        src.SetRadius(0.5)

    elif gtype == 'arrow':
        src = vtk.vtkArrowSource()
        src.SetShaftRadius(0.02)
        src.SetTipLength(.6)

    # glyphs
    epp = vtk.vtkTensorGlyph()
    epp.SetInputData(indata)
    epp.SetSourceConnection(src.GetOutputPort())
    epp.SetScaleFactor(1000)
    epp.ClampScalingOn()
    # epp.SymmetricOn()
    epp.ColorGlyphsOn()
    epp.ThreeGlyphsOff()
    epp.ExtractEigenvaluesOn()
    epp.SetColorModeToEigenvalues()

    # Map the data
    map = vtk.vtkPolyDataMapper()
    map.SetInputConnection(epp.GetOutputPort())

    actorT1 = reader(self,filename1,1,1,1)
    print(filename1)

    if mask1 == 'AF_left' or mask2 == 'AF_left': actormask1 = reader(self,'AF_left.nii.gz',255,0,0)
    if mask1 == 'AF_right' or mask2 == 'AF_right': actormask1 = reader(self,'AF_right.nii.gz',0,255,0)
    if mask1 == 'CST_left' or mask2 == 'CST_left': actormask2 = reader(self,'CST_left.nii.gz',0,0,255)
    if mask1 == 'CST_right' or mask2 == 'CST_right': actormask2 = reader(self,'CST_right.nii.gz',255,255,0)


    # VISUALIZATION
    # Actors
    elactor = vtk.vtkActor()
    elactor.SetMapper(map)
    
    elactor.SetPosition(25,25,160)

    self.ren = vtk.vtkRenderer()
    self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
    self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
    
    self.ren.AddActor(actorT1)
    self.ren.AddActor(actormask1)
    self.ren.AddActor(actormask2)

    self.ren.AddActor(elactor)
    
    self.frame.setLayout(self.vl)
    
    self.show()
    self.iren.Initialize()
    self.iren.Start()

    # zooming when displaying the intersection
    for i in range(50):
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1+i*0.01)
        self.iren.Render()


def reader(self,filename,r,g,b):
    self.reader_src = vtk.vtkNIFTIImageReader()
    self.reader_src.SetFileName(filename)
    
    self.vol_map = vtk.vtkGPUVolumeRayCastMapper()
    self.vol_map.SetInputConnection(self.reader_src.GetOutputPort())
    
    # transfer functions for color and opacity
    self.funColor = vtk.vtkColorTransferFunction()
    self.funColor.AddRGBPoint(0, 0., 0., 0.)
    self.funColor.AddRGBPoint(1, r, g, b)
    
    # for the T1
    if filename == self.filename1:
        self.funAlpha = vtk.vtkPiecewiseFunction()
        self.funAlpha.AddPoint(0, 0.)
        self.funAlpha.AddPoint(256, .003)
    
    # for the masks
    else:
        self.funAlpha = vtk.vtkPiecewiseFunction()
        self.funAlpha.AddPoint(0, 0.)
        self.funAlpha.AddPoint(1, 0.00003)

    self.volProp = vtk.vtkVolumeProperty()
    self.volProp.SetColor(0, self.funColor)
    self.volProp.SetScalarOpacity(0, self.funAlpha)
    self.volProp.SetInterpolationTypeToLinear()

    self.actor = vtk.vtkVolume()
    self.actor.SetMapper(self.vol_map)
    self.actor.SetProperty(self.volProp)

    return self.actor
