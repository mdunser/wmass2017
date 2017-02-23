import ROOT, math, array, sys

def get3DBinContentError(th3, b, i1, i2, ax):
    c, e = 0., 0.
    if   ax.upper() == 'X':
        bins = [ b, i1, i2]
    elif ax.upper() == 'Y':
        bins = [i1,  b, i2]
    elif ax.upper() == 'Z':
        bins = [i1, i2,  b]

    c = th3.GetBinContent(bins[0], bins[1], bins[2])
    e = th3.GetBinError  (bins[0], bins[1], bins[2])

    return c,e
    
def fill3DBinContentError(th3, b, i1, i2, ax, c, e):
    if   ax.upper() == 'X':
        bins = [ b, i1, i2]
    elif ax.upper() == 'Y':
        bins = [i1,  b, i2]
    elif ax.upper() == 'Z':
        bins = [i1, i2,  b]

    th3.SetBinContent(bins[0], bins[1], bins[2], c)
    th3.SetBinError  (bins[0], bins[1], bins[2], e)
    
def clone3DHisto(th3, axes):
    axes_arrays = []
    for axis in axes:
        tmp_arr = array.array('d')
        if not type(axis) == list:
            for i in range(1,axis.GetNbins()+1):
                tmp_arr.append(axis.GetBinLowEdge(i)) 
                if i == axis.GetNbins():
                    tmp_arr.append(axis.GetBinUpEdge(i)) 
        else:
            for i in axis:
                tmp_arr.append(i)
        axes_arrays.append(tmp_arr)
    newth3 = ROOT.TH3F(th3.GetName()+'_new', th3.GetTitle()+'_new', len(axes_arrays[0])-1, axes_arrays[0], len(axes_arrays[1])-1, axes_arrays[1], len(axes_arrays[2])-1, axes_arrays[2])
    return newth3
    

def rebinTH3(th3, axis, bins):
    if not axis in ['x', 'y', 'z', 'X', 'Y', 'Z']:
        sys.exit('trying to rebin a non-axis. exiting...')
    
    thaxis  = getattr(th3, 'Get{axis}axis'.format( axis=axis.upper() ) )()
    thaxis1 = getattr(th3, 'Get{axis}axis'.format( axis= 'Y' if axis.upper() == 'X' else 'X' ) )()
    thaxis2 = getattr(th3, 'Get{axis}axis'.format( axis= 'Y' if axis.upper() == 'Z' else 'Z' ) )()


    axes = [thaxis1, thaxis2]
    axes.insert((0 if axis.upper() == 'X' else 1 if axis.upper() == 'Y' else 2 ), bins )
    th3new = clone3DHisto(th3, axes) ; th3new.Sumw2()

    original_bins = [] 

    for i in range(1, thaxis.GetNbins()+1):
        original_bins.append( thaxis.GetBinLowEdge(i) )
        if i == thaxis.GetNbins():
            original_bins.append( thaxis.GetBinUpEdge(i) )
    if not min(bins) == min(original_bins) and not max(bins) == max(original_bins):
        sys.exit('trying to rebin with different axis boundaries. exiting')

    for i1 in range(0, thaxis1.GetNbins()+2):
        for i2 in range(0, thaxis2.GetNbins()+2):
            for ib, b in enumerate(bins):
                if not b in original_bins:
                    sys.exit('trying to merge bins across boundaries of original histogram')
                    #taking care of under/overflows in the rebinned axis
                    if ib==0:
                        tmp_res = get3DBinContentError(th3, 0, i1, i2, axis)
                        bin_content = tmp_res[0]
                        bin_error2  = tmp_res[1]**2
                        fill3DBinContentError(th3new, 0, i1, i2, axis, bin_content, math.sqrt(bin_error2))
                
                        tmp_res = get3DBinContentError(th3, len(original_bins), i1, i2, axis)
                        bin_content = tmp_res[0]
                        bin_error2  = tmp_res[1]**2
                        fill3DBinContentError(th3new, len(bins), i1, i2, axis, bin_content, math.sqrt(bin_error2))

                bin_content = 0.
                bin_error2  = 0.
                for ob in range(original_bins.index(bins[ib-1])+1, original_bins.index(b)+1):
                    tmp_res = get3DBinContentError(th3, ob, i1, i2, axis)
                    bin_content += tmp_res[0]
                    bin_error2  += tmp_res[1]**2
                fill3DBinContentError(th3new, ib, i1, i2, axis, bin_content, math.sqrt(bin_error2))

    return th3new

def getPtFromEtaCM(eta):

    mw=80.385
    return mw/2*(2*math.exp(-eta))/(1+math.exp(-2*eta))

files=['plus', 'minus']

for f in files:
    print f
    fIn=ROOT.TFile('/afs/cern.ch/work/e/emanca/public/2017-01-02-comparisonWithMarc/WTreeProducer_tree_W{p}_Lumi20.root'.format(p=f))
    fOut=ROOT.TFile('/afs/cern.ch/work/e/emanca/public/2017-01-02-comparisonWithMarc/WTreeProducer_tree_W{p}_Lumi20Reb.root'.format(p=f), 'RECREATE')


    for key in fIn.GetListOfKeys():
	if not'h_mt' in key.GetName(): continue
        print key.GetName()
        th3=ROOT.TH3F

        th3 = fIn.Get(key.GetName())

#take x axis (eta) and rebin y axis (pt) with the same bin size
        
        eta_array = []
        pt_array = []

        Xaxis=th3.GetXaxis()
        Yaxis=th3.GetYaxis()

        for i in range(1,Xaxis.GetNbins()+1):
            eta_array.append(Xaxis.GetBinLowEdge(i))
            if i == Xaxis.GetNbins():
                eta_array.append(Xaxis.GetBinUpEdge(i))

        for i in range(len(eta_array)):
            pt_array.append(getPtFromEtaCM(eta_array[len(eta_array)-i-1]))

        pt_array = [int(x) for x in pt_array if x > 25.0]

        #print eta_array, 'eta, old'
        #print pt_array, 'pt, new'

        newHisto=ROOT.TH3F
        newHisto = rebinTH3(th3, 'y', pt_array)
        
        fOut.cd()
        newHisto.Write()
        """
        for i in range(1,newHisto.GetYaxis().GetNbins()+1):
            print newHisto.GetYaxis().GetBinLowEdge(i)
            if i == newHisto.GetYaxis().GetNbins():
                print newHisto.GetYaxis().GetBinUpEdge(i)
                """
