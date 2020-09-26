import vtk


class SliceRenderer:
    def __init__(self,orie,filename1,filename2,filename3,filename4,filename5):

        self.filename1=filename1
        self.filename2=filename2
        self.filename3=filename3
        self.filename4=filename4
        self.filename5=filename5
        
        # Set up the interaction
        self.inter_style = vtk.vtkInteractorStyleImage()
        
        # set up renderer
        self.renderer = vtk.vtkRenderer()
        
        # set up actors
        actor, self.center1, self.reslice1 = create(self,'T1w_acpc_dc_restore_brain.nii.gz', orie,maxint=2000,op=1)
        
        self.renderer.AddActor(actor)
        
        if self.filename2 == 1:
            self.colour = 'Red'
            actor2, self.center2, self.reslice2 = create(self,'AF_left.nii.gz', orie,maxint= 1,op=0.2)
            self.renderer.AddActor(actor2)
        
        if self.filename3 == 1:
            self.colour = 'Green'
            actor3, self.center3, self.reslice3 = create(self,'AF_right.nii.gz', orie,maxint=1,op=0.2)
            self.renderer.AddActor(actor3)
        
        if self.filename4 == 1:
            self.colour = 'Blue'
            actor4, self.center4, self.reslice4 = create(self,'CST_left.nii.gz', orie,maxint= 1,op=0.2)
            self.renderer.AddActor(actor4)
        
        if self.filename5 == 1:
            self.colour = 'Banana'
            actor5, self.center5, self.reslice5 = create(self,'CST_right.nii.gz', orie,maxint= 1,op=0.2)
            self.renderer.AddActor(actor5)

    
        # Create callbacks for slicing the image
        self.actions = {}
        self.actions["Slicing"] = 0
        
        # interactions
        self.inter_style.AddObserver("MouseMoveEvent", self.MouseMoveCallback)
        self.inter_style.AddObserver("LeftButtonPressEvent", self.ButtonCallback)
        self.inter_style.AddObserver("LeftButtonReleaseEvent", self.ButtonCallback)
        self.inter_style.AddObserver("double clicked", self.mousePressEvent)



    def ButtonCallback(self, obj, event):
        if event == "LeftButtonPressEvent":
            self.actions["Slicing"] = 1
            print('X:' +self.mouseX)
            print('Y:' +self.mouseY)
        
        else:
            self.actions["Slicing"] = 0

    # navigation throughout slices (and fusion)
    def MouseMoveCallback(self, obj, event):
        #center = self.center

        inter = obj.GetInteractor()
        
        (lastX, lastY) = inter.GetLastEventPosition()
        (mouseX, mouseY) = inter.GetEventPosition()
        
        self.mouseX=mouseX
        
        
        if self.actions["Slicing"] == 1:
            deltaY = mouseY - lastY
            
            self.reslice1.Update()
            
            sliceSpacing = self.reslice1.GetOutput().GetSpacing()[2]
            matrix = self.reslice1.GetResliceAxes()
            # move the center point that we are slicing through
            center = matrix.MultiplyPoint((0, 0, sliceSpacing*deltaY, 1))
            matrix.SetElement(0, 3, center[0])
            matrix.SetElement(1, 3, center[1])
            matrix.SetElement(2, 3, center[2])
            current_window = inter.GetRenderWindow()
            current_window.Render()
            
            if self.filename2 == 1:
                self.reslice2.Update()
                sliceSpacing2 = self.reslice2.GetOutput().GetSpacing()[2]
                matrix2 = self.reslice2.GetResliceAxes()
                # move the center point that we are slicing through
                center2 = matrix2.MultiplyPoint((0, 0, sliceSpacing2*deltaY, 1))
                matrix2.SetElement(0, 3, center2[0])
                matrix2.SetElement(1, 3, center2[1])
                matrix2.SetElement(2, 3, center2[2])
            
            if self.filename3 == 1:
                self.reslice3.Update()
                sliceSpacing3 = self.reslice3.GetOutput().GetSpacing()[2]
                matrix3 = self.reslice3.GetResliceAxes()
                # move the center point that we are slicing through
                center3 = matrix3.MultiplyPoint((0, 0, sliceSpacing3*deltaY, 1))
                matrix3.SetElement(0, 3, center3[0])
                matrix3.SetElement(1, 3, center3[1])
                matrix3.SetElement(2, 3, center3[2])
            
            if self.filename4 == 1:
                self.reslice4.Update()
                sliceSpacing4 = self.reslice4.GetOutput().GetSpacing()[2]
                matrix4 = self.reslice4.GetResliceAxes()
                # move the center point that we are slicing through
                center4 = matrix4.MultiplyPoint((0, 0, sliceSpacing4*deltaY, 1))
                matrix4.SetElement(0, 3, center4[0])
                matrix4.SetElement(1, 3, center4[1])
                matrix4.SetElement(2, 3, center4[2])
            
            if self.filename5 == 1:
                self.reslice5.Update()
                sliceSpacing5 = self.reslice5.GetOutput().GetSpacing()[2]
                matrix5 = self.reslice5.GetResliceAxes()
                # move the center point that we are slicing through
                center5 = matrix5.MultiplyPoint((0, 0, sliceSpacing5*deltaY, 1))
                matrix5.SetElement(0, 3, center5[0])
                matrix5.SetElement(1, 3, center5[1])
                matrix5.SetElement(2, 3, center5[2])
        
            current_window = inter.GetRenderWindow()
            current_window.Render()
        
        else:
            self.inter_style.OnMouseMove()

    def mousePressEvent(self, obj):
        if obj.type() == QEvent.MouseButtonDblClick:
            logger.debug( "double clicked" )
            #self.picker.SetTolerance(0.05)
            picker = vtkCellPicker()
            picker.SetTolerance(0.05)
            res = picker.Pick(obj.pos().x(), obj.pos().y(), 0, self.renderer)
            if res > 0:
                c = picker.GetPickPosition()
                logger.debug( " picked at coordinate = {}".format( c ) )
                self.emit(SIGNAL("objectPicked"), c[0:3])

def create(self,filename, orie='coronal', maxint=1000,op=0.99):
    # set up the source
    source = vtk.vtkNIFTIImageReader()
    source.SetFileName(filename)
    self.source = source
    
    # Calculate the center of the volume
    source.Update()
    
    (xMin, xMax, yMin, yMax, zMin, zMax) = source.GetExecutive().GetWholeExtent(
                                                source.GetOutputInformation(0))
    (xSpacing, ySpacing, zSpacing) = source.GetOutput().GetSpacing()
    (x0, y0, z0) = source.GetOutput().GetOrigin()

    self.center = [x0 + xSpacing * 0.5 * (xMin + xMax),
                   y0 + ySpacing * 0.5 * (yMin + yMax),
                   z0 + zSpacing * 0.5 * (zMin + zMax)]
                   
    # Matrices for axial, coronal, sagittal, oblique view orientations
    orie_mat = _get_orie_mat(self,orie=orie)

    # Extract a slice in the desired orientation
    self.reslice = vtk.vtkImageReslice()
    self.reslice.SetInputConnection(source.GetOutputPort())
    self.reslice.SetOutputDimensionality(2)
    self.reslice.SetResliceAxes(orie_mat)
    self.reslice.SetInterpolationModeToLinear()

    # Create a greyscale lookup table
    if filename == 'T1w_acpc_dc_restore_brain.nii.gz':
        table = vtk.vtkLookupTable()
        table.SetRange(0, maxint) # image intensity range
        table.SetValueRange(0.0, 1.0) # from black to white
        table.SetSaturationRange(0.0, 0.0) # no color saturation
        table.SetRampToLinear()
        table.Build()
    
        # Map the image through the lookup table
        color = vtk.vtkImageMapToColors()
        color.SetLookupTable(table)
        color.SetInputConnection(self.reslice.GetOutputPort())

        # Display the image
        actor = vtk.vtkImageActor()
        actor.GetMapper().SetInputConnection(color.GetOutputPort())
        actor.GetProperty().SetOpacity(op)
    else:
        
        table = vtk.vtkLookupTable()
        table.SetNumberOfTableValues(2)

        table.Build()
        nc = vtk.vtkNamedColors()

        table.SetTableValue(0,nc.GetColor4d("Black"))
        table.SetTableValue(1,nc.GetColor4d(self.colour))
        
        color = vtk.vtkImageMapToColors()
        color.SetLookupTable(table)
        color.SetInputConnection(self.reslice.GetOutputPort())

        actor = vtk.vtkImageActor()
        actor.GetMapper().SetInputConnection(color.GetOutputPort())
        actor.GetProperty().SetOpacity(op)

    return actor, self.center, self.reslice

# orientation definition
def _get_orie_mat(self, orie):
    trans_mat = vtk.vtkMatrix4x4()
    center = self.center
    
    if orie == 'axial':
        trans_mat.DeepCopy((1, 0, 0, center[0],
                            0, 1, 0, center[1],
                            0, 0, 1, center[2],
                            0, 0, 0, 1))
    elif orie == 'coronal':
        trans_mat.DeepCopy((1, 0, 0, center[0],
                            0, 0, 1, center[1],
                            0,-1, 0, center[2],
                            0, 0, 0, 1))
    elif orie == 'sagittal':
        trans_mat.DeepCopy((0, 0,-1, center[0],
                            1, 0, 0, center[1],
                            0,-1, 0, center[2],
                            0, 0, 0, 1))
    elif orie == 'oblique':
        trans_mat.DeepCopy((1, 0, 0, center[0],
                            0, 0.866025, -0.5, center[1],
                            0, 0.5, 0.866025, center[2],
                            0, 0, 0, 1))
    else:
        raise ValueError

    return trans_mat

