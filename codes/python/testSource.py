# Use vtkStructuredGrid
# has all the right things but extents and bounds and cells seem to get confused and hence
# nothing gets plotted
import numpy
from paraview import vtk
import os
pts = vtk.vtkPoints()
newArray = vtk.vtkDoubleArray()
# this is how far I've got before...
newArray.SetName("testdata")
newArray.SetNumberOfComponents(1)

# stuff our numbers into pdo.GetPointData().GetArray(0).InsertNextValue(float) one by one,
# followed by pts.InsertNextPoint(x,y,z), so need to get xyz as well
xmin,xmax,Nx,ymin,ymax,Ny,zmin,zmax,Nz = -1,1,10,-1,2,20,-1,3,30
loci = numpy.mgrid[xmin:xmax:1j*Nx,ymin:ymax:1j*Ny,zmin:zmax:1j*Nz].reshape(3,-1)
values = numpy.random.random(loci[0].shape)
exts = [0,Nx-1,0,Ny-1,0,Nz-1]
pdo.SetExtent(exts)
for ind in range(loci[0].shape[0]):
    newArray.InsertNextValue(values[ind])
    #pts.InsertNextPoint(loci[0,ind],loci[1,ind],loci[2,ind])
pdo = self.GetOutput()
pdo.GetPointData().AddArray(newArray)
#pdo.SetPoints(pts)
#pdo.SetActiveAttribute()

# try to add this
executive = self.GetExecutive()
outInfo = executive.GetOutputInformation(0)
#executive.SetExtentTranslator(outInfo, vtk.vtkExtentTranslator())
#outInfo.Set(executive.WHOLE_EXTENT(), 0, 9, 0, 9, 0, 9)
#outInfo.Set(vtk.vtkDataObject.SPACING(), 1, 1, 1)
dataType = 10 # VTK_FLOAT
numberOfComponents = 1
vtk.vtkDataObject.SetPointDataActiveScalarInfo(outInfo, dataType, numberOfComponents)

'''
# vtkTable
import numpy
data = numpy.random.random(29,4)
for ind,name in enumerate(["x","y","z","data"]):
    output.RowData.append(data[:,ind],name)
'''


# use vtkMultiblockDataSet
# gets, inside the multiblock, one vtkStructuredGrid just as wrong as above
import numpy
import paraview
import paraview.vtk
from numpy_interface import algorithms as algs
from numpy_interface import dataset_adapter as dsa
xmin,xmax,Nx,ymin,ymax,Ny,zmin,zmax,Nz = -1,1,10,-1,2,20,-1,3,30
loci = numpy.mgrid[xmin:xmax:1j*Nx,ymin:ymax:1j*Ny,zmin:zmax:1j*Nz]
values = numpy.random.random(loci.reshape(3,-1)[0].shape)
exts = [xmin,xmax,ymin,ymax,zmin,zmax]
sg0 = paraview.vtk.vtkStructuredGrid()
sg0.SetExtent(exts)
Xc,Yc,Zc = loci
coordinates = algs.make_vector(Xc.ravel(), Yc.ravel(), Zc.ravel())
pts = paraview.vtk.vtkPoints()
pts.SetData(dsa.numpyTovtkDataArray(coordinates,"Points"))
sg0.SetPoints(pts)
#output.SetExtent(exts)
#output.SetPoints(pts)
newArray = vtk.vtkDoubleArray()
# this is how far I've got before...
newArray.SetName("testdata")
newArray.SetNumberOfComponents(1)
sg0.GetPointData().AddArray(newArray)
loci = loci.reshape(3,-1)
for ind in range(loci[0].shape[0]):
    sg0.GetPointData().GetArray(0).InsertNextValue(values[ind])
output.SetBlock(0, sg0)



# use ???
# gets sigsegvs!
import numpy
import paraview
import paraview.vtk
from numpy_interface import algorithms as algs
from numpy_interface import dataset_adapter as dsa

xmin,xmax,Nx,ymin,ymax,Ny,zmin,zmax,Nz = -1,1,10,-1,2,20,-1,3,30
loci = numpy.mgrid[xmin:xmax:1j*Nx,ymin:ymax:1j*Ny,zmin:zmax:1j*Nz]
values = numpy.random.random(loci[0].shape)
exts = [xmin,xmax,ymin,ymax,zmin,zmax]
sg0 = output # paraview.vtk.vtkStructuredGrid()
sg0.SetExtent(exts)

Xc,Yc,Zc = loci
coordinates = algs.make_vector(Xc.ravel(), Yc.ravel(), Zc.ravel())
pts = paraview.vtk.vtkPoints()
pts.SetData(dsa.numpyTovtkDataArray(coordinates,"Points"))
from paraview import numpy_support
data = numpy_support.numpy_to_vtk(num_array=values.ravel(), deep=True,
                                      array_type=vtk.VTK_FLOAT)
sg0.PointData.append(data, "mydata")
#sg0.SetPoints(pts)



# use vtkImageData
# gets just 60 points and still no output
import numpy
import paraview
import paraview.vtk
from numpy_interface import algorithms as algs
from numpy_interface import dataset_adapter as dsa

xmin,xmax,Nx,ymin,ymax,Ny,zmin,zmax,Nz = -1,1,10,-1,2,20,-1,3,30
loci = numpy.mgrid[xmin:xmax:1j*Nx,ymin:ymax:1j*Ny,zmin:zmax:1j*Nz]
values = numpy.random.random(loci.reshape(3,-1)[0].shape)
exts = [xmin,xmax,ymin,ymax,zmin,zmax]

pdo = self.GetOutput()
pdo.SetExtent(exts)

#data = vtk.vtkImageData()

pdo.GetPointData().AddArray(dsa.numpyTovtkDataArray(values,"data"))
#VTK_data = numpy_support.numpy_to_vtk(num_array=NumPy_data.ravel(), deep=True, array_type=vtk.VTK_FLOAT)



# try rectilinear
# but just gets 60 points again
import numpy
from paraview import vtk
import os
newArray = vtk.vtkDoubleArray()
# this is how far I've got before...
newArray.SetName("testdata")
newArray.SetNumberOfComponents(1)
# stuff our numbers into pdo.GetPointData().GetArray(0).InsertNextValue(float) one by one,
# followed by pts.InsertNextPoint(x,y,z), so need to get xyz as well
xmin,xmax,Nx,ymin,ymax,Ny,zmin,zmax,Nz = -1,1,10,-1,2,20,-1,3,30
loci = numpy.mgrid[xmin:xmax:1j*Nx,ymin:ymax:1j*Ny,zmin:zmax:1j*Nz].reshape(3,-1)
values = numpy.random.random(loci[0].shape)
for ind in range(loci[0].shape[0]):
    newArray.InsertNextValue(values[ind])
pdo = self.GetOutput()
pdo.GetPointData().AddArray(newArray)
exts = [0,Nx-1,0,Ny-1,0,Nz-1]
pdo.SetExtent(exts)
