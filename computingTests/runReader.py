##########################
# Map & reduce functions #
##########################

def fill(reader):
  from ROOT import TH1F

  h = TH1F("h", "test histogram", 64, -4, 4)
  while reader.Next():
    h.Fill(entry.px, entry.py)

  return h

def merge(h1, h2):
  h1.Add(h2)
  return h1


################
# Main program #
################

if __name__ == "__main__":
  import ROOT
  from DistROOT import DistTree

  ROOT.gInterpreter.Declare("""
TH1F* fillCpp(TTreeReader& reader) {
  TH1F *h = new TH1F("h", "test histogram", 64, -4, 4);
  TTreeReaderValue<float> pxval(reader, "px");
  TTreeReaderValue<float> pyval(reader, "py");
  while (reader.Next()) {
    h->Fill(*pxval, *pyval);
  }
  return h;
}
""")

  ROOT.gInterpreter.Declare("""
TH1F* mergeCpp(TH1F *h1, const TH1F *h2) {
  h1->Add(h2);
  return h1;
}
""")

  dTree = DistTree(filelist = ["/data/test.root", "/data/test.root"],
                   treename = "test",
                   npartitions = 2)

  print "Tree entries:", dTree.GetPartitions()

  res = dTree.ProcessAndMerge(ROOT.fillCpp, ROOT.mergeCpp)
  #res = dTree.ProcessAndMerge(fillPy, mergePy)

  print res.GetEntries()
