import numpy
import tempfile
import cProfile
import pstats
data=numpy.random.random((1000,1000,100))
tempfiles = [tempfile.TemporaryFile(dir=".") for i in [0,1,2,3]]
cps = [cProfile.Profile() for i in range(len(tempfiles))]
runs = ["numpy.savez", "numpy.savez_compressed", "numpy.savez_compressed",
        "numpy.savez_compressed"]
for i,r in enumerate(runs):
    if (i==2):
        data[100:900,100:900,30:70]=0.0
    if (i==3):
        data = numpy.ones((1000,1000,100), dtype=numpy.float64)
    cps[i].runcall(eval(r), tempfiles[i], {"array_called_data":data})

print('''Time spent and file sizes:
  uncompressed random data:   {uncompt:g}\t{uncomps} 
  compressed random data:     {compt:g}\t{comps}
  compressed semirandom data: {semit:g}\t{semis}
  compressed zeros:           {zerot:g}\t{zeros}'''.format(
      uncomps=tempfiles[0].tell(),
      comps=tempfiles[1].tell(),
      semis=tempfiles[2].tell(),
      zeros=tempfiles[3].tell(),
      uncompt=pstats.Stats(cps[0]).total_tt,
      compt=pstats.Stats(cps[1]).total_tt,
      semit=pstats.Stats(cps[2]).total_tt,
      zerot=pstats.Stats(cps[3]).total_tt
  ))
