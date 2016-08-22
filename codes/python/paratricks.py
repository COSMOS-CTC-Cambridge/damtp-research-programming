# continue from heat.py


NumPy_data = sol_[:]
NumPy_data_shape = NumPy_data.shape
'''
import vtk
from vtk.util import numpy_support
VTK_data = numpy_support.numpy_to_vtk(num_array=NumPy_data.ravel(), deep=True,
                                      array_type=vtk.VTK_FLOAT)
# You can get it back with
NumPy_data_from_VTK = numpy_support.vtk_to_numpy(VTK_data)
NumPy_data_from_VTK = NumPy_data_from_VTK.reshape(NumPy_data_shape)

# start the VTK magic
dataImporter = vtk.vtkImageImport()
dataImporter.CopyImportVoidPointer(NumPy_data, NumPy_data.nbytes)
dataImporter.SetNumberOfScalarComponents(1)
dataImporter.SetDataExtent(0, 11, 0, 7, 0, 0)
dataImporter.SetWholeExtent(0, 11, 0, 7, 0, 0)
'''

from paraview import numpy_support
ParaView_numpy_data=numpy_support.numpy_to_vtk(NumPy_data.copy())


import paraview
import paraview.simple
import paraview.numpy_support
import paraview.servermanager
import paraview.vtk
"""renderView1=paraview.simple.GetActiveViewOrCreate("RenderView")
#cone=paraview.simple.Cone()
psrc=paraview.servermanager.sources.ProgrammableSource()
psrc.Script='''import numpy
import paraview.numpy_suppor
print "foo"
tmp=paraview.numpy_support.numpy_to_vtk(numpy.random.random(100,101))
output.PointData.append(tmp,"scalar")
'''
cont=paraview.simple.Contour(psrc)
paraview.simple.Show()
paraview.simple.Render()

"""

'''
vtkpd=vtk.vtkPointData()

'''
