
# Input data
##files = ["root://eosuser//eos/user/e/etejedor/inputfile.root"]
files = ['root://eoscms.cern.ch//eos/cms/store/group/phys_smp/Wmass/perrozzi/ntuples/ntuples_2014_05_23_53X/WMinusPOWHEG/InclWeights/WTreeProducer_tree_2p1.root',
         'root://eoscms.cern.ch//eos/cms/store/group/phys_smp/Wmass/perrozzi/ntuples/ntuples_2014_05_23_53X/WMinusPOWHEG/InclWeights/WTreeProducer_tree_2p4.root']

print "Processing", len(files), "files"

# ROOT imports
import ROOT
from DistROOT import DistTree

# Mapper and reducer functions
def fillCMS(reader):
  import ROOT
  ROOT.TH1.AddDirectory(False)
  ROOT.gInterpreter.Declare('#include "/afs/cern.ch/user/e/etejedor/public/wmassAnalyzer.h"')
  myAnalyzer = ROOT.wmassAnalyzer(reader)
  return myAnalyzer.GetHistosList()

def mergeCMS(l1, l2):
  for i in xrange(l1.GetSize()):
    l1.At(i).Add(l2.At(i))
  return l1

# Distributed execution
dTree = DistTree(filelist = files,
                 treename = "WTreeProducer",
                 npartitions = 4)

#print "Tree entries:", dTree.GetPartitions()

import time
start = time.time()

histList = dTree.ProcessAndMerge(fillCMS, mergeCMS)

end = time.time()

print "EXEC TIME (s): ", end - start

# Store resulting histograms in a file
f = ROOT.TFile("output.root", "RECREATE")
for h in histList:
  h.Write()
f.Close()

