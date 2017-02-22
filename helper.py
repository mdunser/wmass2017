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
        #for s in original_bins: print(s, 'original')
    if not min(bins) == min(original_bins) and not max(bins) == max(original_bins):
        sys.exit('trying to rebin with different axis boundaries. exiting')

    for i1 in range(0, thaxis1.GetNbins()+2):
        for i2 in range(0, thaxis2.GetNbins()+2):
            for ib, b in enumerate(bins):
                if not b in original_bins:
                    sys.exit('trying to merge bins across boundaries of original histogram')
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

fIn=ROOT.TFile('/afs/cern.ch/work/e/emanca/public/2017-01-02-comparisonWithMarc/WTreeProducer_tree_Wplus_Lumi20.root')

th3=ROOT.TH3F
th3 = fIn.Get('h_mtPtEta_m111_p18')

rand3 = ROOT.TRandom3(42)

bin_array = []
axis=th3.GetXaxis()


for i in range(1,axis.GetNbins()+1):
    bin_array.append(axis.GetBinLowEdge(i))
    if i == axis.GetNbins():
        bin_array.append(axis.GetBinUpEdge(i))

print(bin_array, 'new')

foo = rebinTH3(th3, 'x', [i for i in bin_array])

counter = 0
for i in range(0, foo.GetNbinsX()+1):
    for j in range(0, foo.GetNbinsY()+1):
        for k in range(0, foo.GetNbinsZ()+1):
            counter += 1
            bin=foo.GetBin(i,j,k)
            if bin==1: print(foo.GetBin(i,j,k))
            if not foo.GetBinContent(i,j,k) == th3.GetBinContent(i,j,k):
                print 'ijk:', foo.GetBinContent(i,j,k), th3.GetBinContent(i,j,k)
print 'counted', counter

print(th3.GetBinContent(11, 1, 3), foo.GetBinContent(11, 1, 3))

x_orig = th3.ProjectionY("qq")
x_new  = foo.ProjectionY("pp")

for i in range(0, x_orig.GetNbinsX()+2):
    if (x_orig.GetBinContent(i) == x_new.GetBinContent(i)):
        #print('damn', x_orig.GetBinContent(i), x_new.GetBinContent(i), i)
        pass


