import os, math, copy, datetime, re
import ROOT
import numpy     as np
import itertools as it
from sys import stdout

date = datetime.date.today().isoformat()
date+=''

class histoset:
    def __init__(self, name):
        self.name = name
        self.h_list = []
        self.nom_integrals = {}
        self.systVarSet = set()
        self.processes  = set()

    def extendHistos(self, e_list):
        for h in e_list:
            h_name = h.GetName()
            updownsysts = [p for p in h_name.split('_') if 'Up' in p or 'Down' in p  ]
            for syst in updownsysts:
                self.systVarSet.add(syst.replace('Up','').replace('Down',''))
            if not 'Up' in h_name and not 'Down' in h_name:
                self.processes.add((h_name.replace('mt_',''), h.Integral()) )
                self.nom_integrals[h_name.replace('mt_','')] = h.Integral()
                h.SetLineColor(ROOT.kBlack)
            if 'Up' in h_name:
                h.SetLineColor(ROOT.kRed)
            if 'Down' in h_name:
                h.SetLineColor(ROOT.kGreen)
        self.h_list.extend(e_list)

    def normalizeVariations(self):
        for h in self.h_list:
            if 'Up' in h.GetName() or 'Down' in h.GetName():
                tmp_proc = '_'.join(h.GetName().split('_')[:-1])
                h.Scale(self.nom_integrals[tmp_proc]/h.Integral())

    def writeFile(self, path, charge = 'all'):
        print 'writing file for {name}'.format(name=self.name)
        if charge == 'all':
            self.finalpath = path+'/'+self.name+'/'
        else:
            self.finalpath = path+'/'+charge+'_'+self.name+'/'
        if not os.path.exists(self.finalpath):
            os.makedirs(self.finalpath)
        self.outfilepath = self.finalpath+'/{name}.root'.format(name=self.name)
        self.outfile = ROOT.TFile(self.outfilepath, 'RECREATE')
        self.outfile.cd()
        for h in self.h_list:
            if (not charge == 'all') and (not charge in h.GetName() ): continue
            for proc in self.processes:
                if h.GetName() == proc[0]:
                    tmp_clone = h.Clone('data_obs')
                    tmp_clone.Write()
            h.Write()
        self.outfile.Close()

    def writeDatacards(self, charge = 'all'):
        for ip,process in enumerate(self.processes):
            if not charge == 'all' and not charge in process[0]: continue
            stdout.write('writing datacards for {name} and process {process} / {processes}\r'.format(name=self.name, process=ip+1, processes=len(self.processes)))
            stdout.flush()
            tmp_file = open('inputForCombine/dcTemplate_unmorphNEW.txt','r')
            tmp_data = tmp_file.read()
            tmp_file.close()
            tmp_data = tmp_data.replace('ZZZ', self.outfile.GetName().split('/')[-1])
            tmp_data = tmp_data.replace('XXX', process[0])
            tmp_data = tmp_data.replace('AAA', '{inte:.3f}'.format(inte=process[1]))
            for syst in self.systVarSet:
                tmp_data += '{syst}  shape  1.6\n'.format(syst=syst)
            tmp_data += 'norm_{process} rateParam * {process} 1 [0.5,1.5] \n'.format(process=process[0])
            tmp_data+='pdfUncertainties group = {pdfs} \n'.format(pdfs=(' '.join([syst for syst in self.systVarSet]) ) )
            outfile = open('{fp}/dc_{process}.txt'.format(fp=self.finalpath, process=process[0]), 'w')
            outfile.write(tmp_data)
            outfile.close()
        stdout.write('\n')
    
    def copyHistosFromBinned(self, binnedSet, binNames):
        for h in binnedSet.h_list:
            h_name = h.GetName()
            #if any( [name in h_name for name in binNames] ):
            if any( [ re.search(name, h_name) for name in binNames] ):
                #print 'extending histogram', h_name
                self.extendHistos([copy.deepcopy(h)])

def getPdfVarString(var):
    vstring = ''
    if not var: return vstring ## empty string for the nominal
    n = (var+1)/2
    if var%2: vstring = 'v{n}Up'  .format(n=n) ## let's call the odd ones up
    else    : vstring = 'v{n}Down'.format(n=n)
    return '_'+vstring

def unfoldHistogram(th3, charge):
    mass = int([p for p in h_name.split('_') if p.startswith('mass') and all(i.isdigit() for i in p[1:])][0].lstrip('mass')) ## reading the mass id out of the histogram name
    pdfv = int([p for p in h_name.split('_') if p.startswith('pdf' ) and all(i.isdigit() for i in p[1:])][0].lstrip('pdf' )) ## reading the pdf-variation id out of the name
    nbinsEta = th3.GetNbinsX()
    nbinsPt  = th3.GetNbinsY()
    hs_inclusive_pt   = {}
    hs_inclusive_eta  = {}
    hs_fullbinned     = {}
    cstring = '_plus' if charge ==1 else '_minus' if charge == -1 else '_sum' if charge == 2 else '_dif' if charge == -2 else '_foobar'
    for i_eta in range(1,nbinsEta+1):
        binstring = '_eta{eta}'.format(eta=i_eta)
        hs_inclusive_pt ['eta{ieta}'.format(ieta=i_eta)]  = th3.ProjectionZ('mass{mass}{cstring}{binstring}{pdfVar}'.format(mass=mass, pdfVar=getPdfVarString(pdfv), cstring=cstring, binstring=binstring), i_eta, i_eta   , 1   , nbinsPt)
        hs_inclusive_pt ['eta{ieta}'.format(ieta=i_eta)].SetTitle(hs_inclusive_pt ['eta{ieta}'.format(ieta=i_eta)].GetName())

    for i_pt  in range(1,nbinsPt +1):                                                            
        binstring = '_pt{pt}'.format(pt=i_pt)                                                    
        hs_inclusive_eta['pt{ipt}'.format(ipt =i_pt)]  = th3.ProjectionZ('mass{mass}{cstring}{binstring}{pdfVar}'.format(mass=mass, pdfVar=getPdfVarString(pdfv), cstring=cstring, binstring=binstring), 1    , nbinsEta, i_pt, i_pt   )
        hs_inclusive_eta['pt{ipt}'.format(ipt =i_pt)].SetTitle(hs_inclusive_eta['pt{ipt}'.format(ipt =i_pt)].GetName())
    for i_eta in range(1,nbinsEta+1):
        for i_pt  in range(1,nbinsPt +1):
            binstring = '_pt{pt}_eta{eta}'.format(pt=i_pt, eta=i_eta)
            hs_fullbinned['pt{ipt}_eta{ieta}'.format(ipt =i_pt,ieta=i_eta)] = th3.ProjectionZ('mass{mass}{cstring}{binstring}{pdfVar}'.format(mass=mass,pdfVar=getPdfVarString(pdfv),cstring=cstring,binstring=binstring), i_eta, i_eta, i_pt, i_pt)
            hs_fullbinned['pt{ipt}_eta{ieta}'.format(ipt =i_pt,ieta=i_eta)].SetTitle(hs_fullbinned['pt{ipt}_eta{ieta}'.format(ipt =i_pt,ieta=i_eta)].GetName())

    h_inclusive_both = th3.ProjectionZ('mass{mass}{cstring}{pdfVar}'.format(mass=mass, pdfVar=getPdfVarString(pdfv), cstring=cstring), 1    , nbinsEta, 1   , nbinsPt)
    h_inclusive_both.SetTitle(h_inclusive_both.GetName())
    return (h_inclusive_both, hs_inclusive_pt, hs_inclusive_eta, hs_fullbinned)

# file_neg = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-10-25-manyEtaBins//WTreeProducer_Wminus_Lumi20.root'
# file_pos = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-10-25-manyEtaBins//WTreeProducer_Wplus_Lumi20.root'
# file_neg = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-10-31-absEta-WRapiditySmaller0p5//WTreeProducer_Wminus_Lumi20.root'
# file_pos = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-10-31-absEta-WRapiditySmaller0p5//WTreeProducer_Wplus_Lumi20.root'
# wrong file_neg = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-11-03-WRapiditySmaller0p5/WTreeProducer_Wminus_Lumi20.root'
# wrong file_pos = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-11-03-WRapiditySmaller0p5/WTreeProducer_Wplus_Lumi20.root'
# buggy file_neg = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-11-03-pdfCheck_rap0p5/WTreeProducer_Wminus_Lumi20.root'
# buggy file_pos = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-11-03-pdfCheck_rap0p5/WTreeProducer_Wplus_Lumi20.root'
# file_neg = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-11-04-pdfCheck_rap0p5/WTreeProducer_Wminus_Lumi20.root'
# file_pos = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-11-04-pdfCheck_rap0p5/WTreeProducer_Wplus_Lumi20.root'
file_neg = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-11-07-pdfCheck_rap0p5_RECO/WTreeProducer_Wminus_Lumi20.root'
file_pos = '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/2016-11-07-pdfCheck_rap0p5_RECO/WTreeProducer_Wplus_Lumi20.root'

tmp_f_pos = ROOT.TFile(file_pos,'READ')
tmp_f_neg = ROOT.TFile(file_neg,'READ')

lo_keys = tmp_f_pos.GetListOfKeys()
lo_hist_names = [h.GetName() for h in lo_keys if 'h_mtPtEta' in h.GetName()]

all_hsets = []
histos_inclusive_pt   = histoset('inclusive_pt'  ) 
histos_inclusive_eta  = histoset('inclusive_eta' ) 
histos_inclusive_both = histoset('inclusive_both') 
histos_full_binning   = histoset('full_binning'  ) 
histos_sum_inclusive_pt   = histoset('sum_inclusive_pt'  ) 
histos_sum_inclusive_eta  = histoset('sum_inclusive_eta' ) 
histos_sum_inclusive_both = histoset('sum_inclusive_both') 
histos_sum_full_binning   = histoset('sum_full_binning'  ) 
histos_dif_inclusive_pt   = histoset('dif_inclusive_pt'  ) 
histos_dif_inclusive_eta  = histoset('dif_inclusive_eta' ) 
histos_dif_inclusive_both = histoset('dif_inclusive_both') 
histos_dif_full_binning   = histoset('dif_full_binning'  ) 
histos_eta_1          = histoset('eta_1'         ) 
histos_eta_2          = histoset('eta_2'         ) 
histos_eta_3          = histoset('eta_3'         ) 
histos_eta_4          = histoset('eta_4'         ) 
histos_eta_5          = histoset('eta_5'         ) 
histos_sum_eta_1          = histoset('sum_eta_1'         ) 
histos_sum_eta_2          = histoset('sum_eta_2'         ) 
histos_sum_eta_3          = histoset('sum_eta_3'         ) 
histos_sum_eta_4          = histoset('sum_eta_4'         ) 
histos_sum_eta_5          = histoset('sum_eta_5'         ) 
histos_dif_eta_1          = histoset('dif_eta_1'         ) 
histos_dif_eta_2          = histoset('dif_eta_2'         ) 
histos_dif_eta_3          = histoset('dif_eta_3'         ) 
histos_dif_eta_4          = histoset('dif_eta_4'         ) 
histos_dif_eta_5          = histoset('dif_eta_5'         ) 
#histos_eta_6          = histoset('eta_6'         ) 

all_hsets += [histos_inclusive_pt  ,
              histos_inclusive_eta ,
              histos_inclusive_both,
              histos_full_binning  ]

massids = [91, 96, 101, 106, 111]

for i_h,h_name in enumerate(lo_hist_names):
    #if i_h > 10: continue
    if not any(['m'+str(mid) in h_name for mid in massids]): continue
    stdout.write("at %1d / %5d \r" % (i_h+1, len(lo_hist_names)) )
    stdout.flush()
    h_tmp_pos = copy.deepcopy(tmp_f_pos.Get(h_name) )
    h_tmp_neg = copy.deepcopy(tmp_f_neg.Get(h_name) )

    h_tmp_sum = copy.deepcopy(tmp_f_pos.Get(h_name) )
    h_tmp_sum.Add(copy.deepcopy(tmp_f_neg.Get(h_name) ), 1.)
    h_tmp_dif = copy.deepcopy(tmp_f_pos.Get(h_name) )
    h_tmp_dif.Add(copy.deepcopy(tmp_f_neg.Get(h_name) ), -1.)

    if not h_tmp_pos or not h_tmp_neg: 
        print 'BOTH HISTOGRAMS WERE NOT FOUND!!! EXITING...'
        exit(0)
    histos_pos = unfoldHistogram(h_tmp_pos,  1)
    histos_neg = unfoldHistogram(h_tmp_neg, -1)
    histos_sum = unfoldHistogram(h_tmp_sum,  2)
    histos_dif = unfoldHistogram(h_tmp_dif, -2)
    histos_inclusive_both .extendHistos([histos_pos[0],histos_neg[0]])
    histos_inclusive_pt   .extendHistos(histos_pos[1].values()+histos_neg[1].values())
    histos_inclusive_eta  .extendHistos(histos_pos[2].values()+histos_neg[2].values())
    histos_full_binning   .extendHistos(histos_pos[3].values()+histos_neg[3].values())

    histos_sum_inclusive_both .extendHistos([histos_sum[0]])
    histos_sum_inclusive_pt   .extendHistos(histos_sum[1].values())
    histos_sum_inclusive_eta  .extendHistos(histos_sum[2].values())
    histos_sum_full_binning   .extendHistos(histos_sum[3].values())

    histos_dif_inclusive_both .extendHistos([histos_dif[0]])
    histos_dif_inclusive_pt   .extendHistos(histos_dif[1].values())
    histos_dif_inclusive_eta  .extendHistos(histos_dif[2].values())
    histos_dif_full_binning   .extendHistos(histos_dif[3].values())

stdout.write("\n") 
    
outpath = 'inputForCombine/unmorph/{date}/'.format(date=date)

histos_eta_1   .copyHistosFromBinned(histos_inclusive_pt, ['_eta1$', '_eta1_v', '_eta10$', '_eta10_v'])
histos_eta_2   .copyHistosFromBinned(histos_inclusive_pt, ['_eta2$', '_eta2_v', '_eta9$', '_eta9_v'])
histos_eta_3   .copyHistosFromBinned(histos_inclusive_pt, ['_eta3$', '_eta3_v', '_eta8$', '_eta8_v'])
histos_eta_4   .copyHistosFromBinned(histos_inclusive_pt, ['_eta4$', '_eta4_v', '_eta7$', '_eta7_v'])
histos_eta_5   .copyHistosFromBinned(histos_inclusive_pt, ['_eta5$', '_eta5_v', '_eta6$', '_eta6_v'])
#histos_eta_6   .copyHistosFromBinned(histos_inclusive_pt, ['_eta6$', '_eta6_v'])

histos_sum_eta_1   .copyHistosFromBinned(histos_sum_inclusive_pt, ['_eta1$', '_eta1_v', '_eta10$', '_eta10_v'])
histos_sum_eta_2   .copyHistosFromBinned(histos_sum_inclusive_pt, ['_eta2$', '_eta2_v', '_eta9$', '_eta9_v'])
histos_sum_eta_3   .copyHistosFromBinned(histos_sum_inclusive_pt, ['_eta3$', '_eta3_v', '_eta8$', '_eta8_v'])
histos_sum_eta_4   .copyHistosFromBinned(histos_sum_inclusive_pt, ['_eta4$', '_eta4_v', '_eta7$', '_eta7_v'])
histos_sum_eta_5   .copyHistosFromBinned(histos_sum_inclusive_pt, ['_eta5$', '_eta5_v', '_eta6$', '_eta6_v'])

histos_dif_eta_1   .copyHistosFromBinned(histos_dif_inclusive_pt, ['_eta1$', '_eta1_v', '_eta10$', '_eta10_v'])
histos_dif_eta_2   .copyHistosFromBinned(histos_dif_inclusive_pt, ['_eta2$', '_eta2_v', '_eta9$', '_eta9_v'])
histos_dif_eta_3   .copyHistosFromBinned(histos_dif_inclusive_pt, ['_eta3$', '_eta3_v', '_eta8$', '_eta8_v'])
histos_dif_eta_4   .copyHistosFromBinned(histos_dif_inclusive_pt, ['_eta4$', '_eta4_v', '_eta7$', '_eta7_v'])
histos_dif_eta_5   .copyHistosFromBinned(histos_dif_inclusive_pt, ['_eta5$', '_eta5_v', '_eta6$', '_eta6_v'])

all_hsets += [ 
    histos_eta_1, 
    histos_eta_2, 
    histos_eta_3, 
    histos_eta_4,
    histos_eta_5,
#    histos_eta_6,
    histos_sum_eta_1, 
    histos_sum_eta_2, 
    histos_sum_eta_3, 
    histos_sum_eta_4,
    histos_sum_eta_5,
    histos_dif_eta_1, 
    histos_dif_eta_2, 
    histos_dif_eta_3, 
    histos_dif_eta_4,
    histos_dif_eta_5,
]

for hset in all_hsets:
    hset.normalizeVariations()
    hset.writeFile(outpath)
    hset.writeDatacards()
    
for hset in [histos_eta_1, histos_eta_2, histos_eta_3, histos_eta_3, histos_eta_4, histos_eta_5 ]:
    hset.normalizeVariations()
    hset.writeFile(outpath, 'minus')
    hset.writeDatacards('minus')
    hset.writeFile(outpath, 'plus')
    hset.writeDatacards('plus')

#tmp_f_pos.Close()
#tmp_f_neg.Close()
