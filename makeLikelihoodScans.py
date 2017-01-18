import ROOT, math, datetime, os
from array import array

colorArray = [1, 2, 3, 4, 6, 7, 8, 9, 45, 38, 28, 29, 13, 41, 30, 40, ROOT.kOrange, ROOT.kPink, ROOT.kCyan+1, ROOT.kSpring, ROOT.kYellow-3, ROOT.kRed-3, ROOT.kBlue-3, ROOT.kOrange-3, ROOT.kMagenta-3, ROOT.kGreen-8]

date = datetime.date.today().isoformat()
date+='-manyPoints'

def getMW(massid):
    return 80.398 + (massid-101)*0.002

class likelihood:
    def __init__(self, infile, name, title, color, style):
        self.color = color
        self.markerstyle = style
        self.infile_name = infile
        self.infile = ROOT.TFile(self.infile_name, 'READ')
        self.tree   = self.infile.Get('limit'); 
        self.lims   = {}
        self.mwns = []
        self.mws  = []
        for evt in self.tree: 
            self.mwns.append(evt.mw)
            self.mws .append(getMW(evt.mw))
        self.name  = name
        self.title = title
        self.hist = ROOT.TH1F('hist_{name}'.format(name=self.name), 'likelihood scan', len(self.mws), min(self.mws), max(self.mws))
        self.fillHisto()
        self.getGraph()
        self.getVariationGraphs()

    def fillHisto(self):
        for evt in self.tree: 
            self.hist. SetBinContent(self.hist.FindBin(getMW(evt.mw)), 2*evt.deltaNLL)
        self.histStyle()

    def histStyle(self):
        self.hist.SetMarkerStyle(self.markerstyle)
        self.hist.SetMarkerColor(self.color)
        self.hist.SetMarkerSize(1.1)
        self.hist.GetXaxis().SetTitle('m_{W} (GeV)')
        self.hist.GetYaxis().SetTitle('-2 #Delta ln L')
        self.hist.GetYaxis().SetRangeUser(-0.01, 1.5)

    def getGraph(self):
        self.n = self.tree.Draw('2*deltaNLL:((mw-101)*2.000)', '', 'goff')
        #self.graph = ROOT.TGraph(self.n, self.tree.GetV2(), self.tree.GetV1() )
        self.vals = []
        for ev in self.tree:
            self.vals.append( [((ev.mw-101)*2.000), (2.*ev.deltaNLL)] )
        self.vals = sorted(self.vals)
        self.graph = ROOT.TGraph(len(self.vals), array('d', [x[0] for x in self.vals]), array('d', [y[1] for y in self.vals]) )
        self.graphStyle()
        self.graph_alt = ROOT.TGraph(len(self.vals), array('d', [y[1] for y in self.vals]), array('d', [x[0] for x in self.vals]) )
        self.err = self.graph_alt.Eval(1.)
        self.line = ROOT.TLine(self.err, -0.01, self.err, 1.)
        self.line.SetLineColor(self.color)
        self.line.SetLineWidth(2)
        self.line.SetLineStyle(2)

    def getVariationGraphs(self):
        self.vargraphs = []
        self.varsmg = ROOT.TMultiGraph()
        self.varsmg.SetName(self.name); self.varsmg.SetTitle(self.name)
        self.hasVars = False
        for ev in self.tree:
            if hasattr(ev, 'v1'): self.hasVars = True
            continue
        if self.hasVars:
            for var in range(1,27):
                vals = []
                for ev in self.tree:
                    vi = 'v{var}'.format(var=var)
                    vals.append( [((ev.mw-101)*2.000), (0+getattr(ev, vi) ) ] )
                vals = sorted(vals)
                vargraph = ROOT.TGraph(len(vals), array('d', [x[0] for x in vals]), array('d', [y[1] for y in vals]) )
                vargraph.SetName('v%i'%var); vargraph.SetTitle('v%i'%var)
                vargraph.SetLineColor(colorArray[var-1] )#var if var <5 else var+1)
                vargraph.SetLineWidth(2)
                self.vargraphs.append(vargraph)
                
        if self.hasVars:
            for g in self.vargraphs:
                self.varsmg.Add(g)

    def graphStyle(self):
        self.graph.SetMarkerStyle(self.markerstyle)
        self.graph.SetMarkerColor(self.color)
        self.graph.SetLineColor  (self.color)
        self.graph.SetLineWidth  (2)
        self.graph.SetMarkerSize(1.0)
        self.graph.GetXaxis().SetTitle('m_{fit} - m_{true} (MeV)')
        self.graph.GetYaxis().SetTitle('-2 #Delta ln L')
        self.graph.GetYaxis().SetRangeUser(-0.01, 1.5)

## lh_3d             = likelihood('higgsCombine2016-10-27_full_binning.POINTSFULL.MultiDimFit.mH120.root'                    , '3d_withPDF'       , 'full binned w/ PDF'        , 2 , 20)
## lh_3d_noPDF       = likelihood('higgsCombine2016-10-27_full_binning_noPDFUncertainty.POINTSFULL.MultiDimFit.mH120.root'   , '3d_noPDF'         , 'full binned no PDF'        , 2 , 24)
## lh_incPt          = likelihood('higgsCombine2016-10-28_inclusive_pt.POINTSFULL.MultiDimFit.mH120.root'                    , 'incPt_withPDF'    , 'binned #eta w/ PDF'        , 3 , 21)
## lh_incPt_noPDF    = likelihood('higgsCombine2016-10-28_inclusive_pt_noPDFUncertainty.POINTSFULL.MultiDimFit.mH120.root'   , 'incPt_noPDF'      , 'binned #eta no PDF'        , 3 , 25)
## lh_incEta         = likelihood('higgsCombine2016-10-28_inclusive_eta.POINTSFULL.MultiDimFit.mH120.root'                   , 'incEta_withPDF'   , 'binned p_{T} w/ PDF'       , 4 , 22)
## lh_incEta_noPDF   = likelihood('higgsCombine2016-10-28_inclusive_eta_noPDFUncertainty.POINTSFULL.MultiDimFit.mH120.root'  , 'incEta_noPDF'     , 'binned p_{T} no PDF'       , 4 , 26)
## lh_incPtEta       = likelihood('higgsCombine2016-10-28_inclusive_both.POINTSFULL.MultiDimFit.mH120.root'                  , 'incPtEta_withPDF' , 'inclusive w/ PDF'          , 6 , 23)
## lh_incPtEta_noPDF = likelihood('higgsCombine2016-10-28_inclusive_both_noPDFUncertainty.POINTSFULL.MultiDimFit.mH120.root' , 'incPtEta_noPDF'   , 'inclusive no PDF'          , 6 , 32)

lh_eta_5           = likelihood('higgsCombine2016-11-25_charges_eta_5.MultiDimFit.mH120.root'                       , 'eta_5_withPDF'    , 'W^{#pm} central w/ PDF'    ,  1 , 20)
lh_eta_5_noPDF     = likelihood('higgsCombine2016-11-25_charges_eta_5_noPDFUncertainty.MultiDimFit.mH120.root'      , 'eta_5_noPDF'      , 'W^{#pm} central no PDF'    ,  1 , 24)
lh_sum_eta_5       = likelihood('higgsCombine2016-11-25_charges_sum_eta_5.MultiDimFit.mH120.root'                   , 'sum_eta_5_withPDF', 'W^{+}+W^{-} central w/ PDF',  2 , 23)
lh_sum_eta_5_noPDF = likelihood('higgsCombine2016-11-25_charges_sum_eta_5_noPDFUncertainty.MultiDimFit.mH120.root'  , 'sum_eta_5_noPDF'  , 'W^{+}+W^{-} central no PDF',  2 , 32)
lh_dif_eta_5       = likelihood('higgsCombine2016-11-25_charges_dif_eta_5.MultiDimFit.mH120.root'                   , 'dif_eta_5_withPDF', 'W^{+}-W^{-} central w/ PDF',  3 , 21)
lh_dif_eta_5_noPDF = likelihood('higgsCombine2016-11-25_charges_dif_eta_5_noPDFUncertainty.MultiDimFit.mH120.root'  , 'dif_eta_5_noPDF'  , 'W^{+}-W^{-} central no PDF',  3 , 25)
lh_neg_eta_5       = likelihood('higgsCombine2016-11-25_charges_minus_eta_5.MultiDimFit.mH120.root'                 , 'neg_eta_5_withPDF', 'W^{-} central w/ PDF'      ,  4 , 22)
lh_neg_eta_5_noPDF = likelihood('higgsCombine2016-11-25_charges_minus_eta_5_noPDFUncertainty.MultiDimFit.mH120.root', 'neg_eta_5_noPDF'  , 'W^{-} central no PDF'      ,  4 , 26)
lh_pos_eta_5       = likelihood('higgsCombine2016-11-25_charges_plus_eta_5.MultiDimFit.mH120.root'                  , 'pos_eta_5_withPDF', 'W^{+} central w/ PDF'      ,  5 , 21)
lh_pos_eta_5_noPDF = likelihood('higgsCombine2016-11-25_charges_plus_eta_5_noPDFUncertainty.MultiDimFit.mH120.root' , 'pos_eta_5_noPDF'  , 'W^{+} central no PDF'      ,  5 , 25)

lhs = [
 lh_eta_5           ,
 lh_eta_5_noPDF     ,
 lh_sum_eta_5       ,
 lh_sum_eta_5_noPDF ,
 lh_dif_eta_5       ,
 lh_dif_eta_5_noPDF ,
 lh_neg_eta_5       ,
 lh_neg_eta_5_noPDF ,
 lh_pos_eta_5       ,
 lh_pos_eta_5_noPDF ,
]

canv = ROOT.TCanvas('canv', 'canv', 800,600)
canv.cd()
ROOT.gStyle.SetOptStat(0)

leg = ROOT.TLegend(0.68, 0.12, 0.88, 0.35)
leg.SetLineColor(ROOT.kWhite)
leg.SetFillColorAlpha(ROOT.kWhite, 0.)
leg.SetTextSize(0.03)

for i,l in enumerate(lhs):
    leg.AddEntry(l.graph, l.title, 'pl')

mg = ROOT.TMultiGraph()
for i,l in enumerate(lhs):
    #l.graph.Draw('alp %s'%('same' if i else '') )
    mg.Add(l.graph)
mg.Draw('apl')
mg.GetYaxis().SetRangeUser(-0.01, 1.5)
mg.GetXaxis().SetTitle(lhs[0].graph.GetXaxis().GetTitle())
mg.GetYaxis().SetTitle(lhs[0].graph.GetYaxis().GetTitle())
mg.GetXaxis().SetRangeUser(-20., 20.)

leg.Draw('same')
line = ROOT.TLine(mg.GetXaxis().GetXmin(), 1., mg.GetXaxis().GetXmax(), 1.)
line.SetLineStyle(2)
line.SetLineWidth(2)
line.SetLineColor(ROOT.kGray+1)
line.Draw('same')

#for i,l in enumerate(lhs):
#    l.line.Draw()

outpath = '/afs/cern.ch/user/m/mdunser/www/private/wmass/pdf_uncertainties/{date}/'.format(date=date)
if not os.path.exists(outpath):
    os.makedirs(outpath)
    os.system('cp ~/index.php {op}'.format(op=outpath))
    
canv.SaveAs('{op}/pdf_effects.pdf'.format(op=outpath))
canv.SaveAs('{op}/pdf_effects.png'.format(op=outpath))

for i,l in enumerate(lhs):
    if l.hasVars:
        leg2 = ROOT.TLegend(0.12, 0.12, 0.45, 0.25)
        leg2.SetNColumns(4)
        for g in l.vargraphs:
            leg2.AddEntry(g, g.GetName(), 'pl')
        c2 = ROOT.TCanvas('c2', 'c2', 800,800)
        c2.cd()
        ROOT.gStyle.SetPadRightMargin(0.05)
        ROOT.gStyle.SetPadLeftMargin(0.12)
        l.varsmg.Draw('apl')
        l.varsmg.GetYaxis().SetRangeUser(-0.2,0.2)
        leg2.Draw('same')
        #l.varsmg.GetYaxis().SetRangeUser(-0.1, 26.1)
        l.varsmg.GetXaxis().SetRangeUser(-20., 20.)
        l.varsmg.GetXaxis().SetTitle(l.graph.GetXaxis().GetTitle())
        l.varsmg.GetYaxis().SetTitle('values of #theta_{i}')
        l.varsmg.GetYaxis().SetTitleOffset(1.60)
        c2.SaveAs('{op}/variations_effects_{name}.pdf'.format(op=outpath, name=l.name))
        c2.SaveAs('{op}/variations_effects_{name}.png'.format(op=outpath, name=l.name))
        del c2



for l in lhs:
    os.system('cp {filename} {target}'.format(filename=l.infile_name, target=outpath))
