import ROOT, copy, datetime
from os import path as osp
import os

date = datetime.date.today().isoformat()+'_mass101'

ROOT.gStyle.SetOptStat(0)

def makeRatioPlot(hlist, name, opts = {}):

    norm = False; do = 'pe'; legco = [0.65,0.65,0.85,0.85]; yrange = []
    if opts.has_key('norm' ): norm = opts['norm']
    if opts.has_key('do'   ): do   = opts['do']
    if opts.has_key('legco'): legco= opts['legco']
    if opts.has_key('yrange'): yrange= opts['yrange']

    c1 = ROOT.TCanvas('foo','foo',800,800); c1.cd()
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.25, 1, 1.0)
    pad1.SetBottomMargin(0.1)
    pad1.Draw()
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.25)
    pad2.SetTopMargin(0.1);
    pad2.SetBottomMargin(0.3);
    pad2.Draw();

    leg = ROOT.TLegend(legco[0], legco[1], legco[2], legco[3])
    leg.SetTextSize(0.04)
    ymax = 0.
    for ih,h in enumerate(hlist):
        tmp_max = h.GetMaximum()
        if tmp_max > ymax: ymax = tmp_max
        h.SetMarkerColor(h.GetLineColor())
        h.SetMarkerSize(0.85)
        if 'Up'   in h.GetName(): h.SetMarkerStyle(21)
        elif 'Down' in h.GetName(): h.SetMarkerStyle(22)
        else : h.SetMarkerStyle(20)

    pad1.cd()
    for ih,h in enumerate(hlist):
        if norm: h.Scale(1./h.Integral())
        else: 
            if not yrange: h.GetYaxis().SetRangeUser(0.01, ymax*1.2)
            else: h.GetYaxis().SetRangeUser(yrange[0], yrange[1])
        h.Draw(do + ('' if not ih else ' same'))
        leg.AddEntry(h, 'up' if 'Up' in h.GetName() else 'down' if 'Down' in h.GetName() else 'nominal', 'pl')

    leg.Draw('same')

    if opts.has_key('fitratio'):
        fitratio = opts['fitratio']
        print 'found ratio fit key. fitting index %d with function %s'%(fitratio[0], fitratio[1])
    else: fitratio = [-1 , '']
    r_fiti = fitratio[0]; r_fitf = fitratio[1]
    ratios = []
    pad2.cd()
    for ih,h in enumerate(hlist):
        if not ih:
            refHisto = copy.deepcopy(h)
        else:
            divh = copy.deepcopy(h)
            divh.Divide(refHisto)
            divh.GetYaxis().SetRangeUser(0.99,1.01)
            divh.GetYaxis().SetTitle('ratio')
            divh.GetYaxis().CenterTitle()
            divh.GetYaxis().SetTitleSize(0.14)
            divh.GetYaxis().SetLabelSize(0.12)
            divh.GetYaxis().SetNdivisions(4)
            divh.GetXaxis().SetLabelSize(0.12)
            divh.GetXaxis().SetTitle('')
            divh.SetMarkerColor(divh.GetLineColor())
            if ih == r_fiti:
                divh.Fit(r_fitf,'','',50,250)
                retval = copy.deepcopy(divh.GetFunction(fitratio[1]))
            #divh.Draw('pe same')#+ '' if ih == 1 else ' same')
            ratios.append(divh)

    for ratio in ratios:
        ratio.Draw('pe0 same')
    l1 = ROOT.TLine(divh.GetXaxis().GetXmin(), 1., divh.GetXaxis().GetXmax(), 1.)
    l1.SetLineStyle(2)
    l1.Draw('same')
    c1.SaveAs(name+'.pdf')
    c1.SaveAs(name+'.png')
    return c1



infiles = {'eta4': 'inputForCombine/unmorph/2016-11-24/eta_4/eta_4.root'}

ROOT.gROOT.SetBatch()


canv = ROOT.TCanvas('foo', 'bar', 800, 800)


outpath = '/afs/cern.ch/user/m/mdunser/www/private/wmass/variation_comparisons/{date}/'.format(date=date)
if not os.path.exists(outpath):
    os.makedirs(outpath)
    os.system('cp ~/index.php {op}'.format(op=outpath))

for v in range(1,27):
    for b,inf in infiles.items():
        _file = ROOT.TFile(inf,'READ')
        for ch in ['minus', 'plus']:
            central = _file.Get('mass101_{ch}_{b}'        .format(b=b,ch=ch) )
            vup    = _file.Get('mass101_{ch}_{b}_v{v}Up'  .format(b=b,ch=ch,v=v) )
            vdn    = _file.Get('mass101_{ch}_{b}_v{v}Down'.format(b=b,ch=ch,v=v) )
            a = makeRatioPlot([central, vup, vdn], '{op}/{b}_{ch}_v{v}'.format(op=outpath,b=b,ch=ch,v=v),{'yrange': [0, 110000], 'do': 'ple'} )
    
        _file.Close()
