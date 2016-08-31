
import numpy
import tempfile
import h5py
file=tempfile.NamedTemporaryFile(dir="../codes/python/", prefix="hdf5_visualisation_example", suffix=".h5",
                                 delete=False)
file.close()
xmin, xmax, ymin, ymax, zmin, zmax = -5,+5,-5,+5,-5,+5
xpts, ypts, zpts = 101, 101, 101
cutoff1, cutoff2, cutoff3 = 1.0, 3.0, 4.0
dsname="mydataset"
m = numpy.mgrid[xmin:xmax:xpts*1j,ymin:ymax:ypts*1j,zmin:zmax:xpts*1j]
r = (m**2).sum(axis=0)**0.5
mydata = cutoff2/(cutoff2-cutoff3)**2*(r-cutoff3)**2
mydata[r<cutoff2] = r[r<cutoff2]
mydata[r<cutoff1] = 0.0
mydata[r>cutoff3] = 0.0
h5file = h5py.File(file.name,"w")
try:
    h5file.create_dataset(dsname, data=mydata) #, compression="szip")
except ValueError as ve:
    if (ve.args[0] == 'Compression filter "szip" is unavailable'):
        try:
            h5file.create_dataset(dsname, data=mydata, compression="lzf")
        except ValueError as ve:
            if (ve.args[0] == 'Compression filter "lzf" is unavailable'):
                try:
                    h5file.create_dataset(dsname, data=mydata, compression="gzip")
                except ValueError as ve:
                    if (ve.args[0] == 'Compression filter "gzip" is unavailable'):
                        h5file.create_dataset(dsname, data=mydata)
                    else:
                        raise
            else:
                raise
    else:
        raise
print("Wrote data to file {f} using compression type {comp}.".format(f=file.name, comp=h5file[dsname].compression))

str="""<?xml version="1.0" ?>
<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>
<Xdmf Version="2.0">
  <Domain>
    <Grid Name="{meshname}" GridType="Uniform">
      <Topology TopologyType="3DCoRectMesh" NumberOfElements="{Nx} {Ny} {Nz}"/>
       <Geometry GeometryType="ORIGIN_DXDYDZ">
        <DataItem DataType="Float" Dimensions="3" Format="XML">
          {xmin} {ymin} {zmin}
        </DataItem>
        <DataItem DataType="Float" Dimensions="3" Format="XML">
          {dx} {dy} {dz}
        </DataItem>
      </Geometry>
      <Attribute Name="mydata" AttributeType="Scalar" Center="Node">
        <DataItem Dimensions="{Nx} {Ny} {Nz}" NumberType="Float" Precision="{precision}" Format="HDF">
          {filename}:/{datasetname}
        </DataItem>
      </Attribute>
    </Grid>
  </Domain>
</Xdmf>
""".format(meshname="mymesh",
           Nx=h5file[dsname].shape[0], Ny=h5file[dsname].shape[1], Nz=h5file[dsname].shape[2],
           xmin=xmin, ymin=ymin, zmin=zmin,
           dx=(xmax-xmin)*1.0/(xpts-1), dy=(ymax-ymin)*1.0/(ypts-1), dz=(zmax-zmin)*1.0/(zpts-1),
           precision=h5file[dsname].dtype.itemsize,
           filename=h5file.filename,
           datasetname=dsname)
xdmffilen=h5file.filename.replace(".h5",".xdmf")
xdmffile=open(xdmffilen,"w")
xdmffile.write(str)
xdmffile.close()
h5file.close()
