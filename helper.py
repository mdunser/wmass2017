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
    #e = th3.GetBinError  (bins[0], bins[1], bins[2])

    return c,e
    
def fill3DBinContentError(th3, b, i1, i2, ax, c, e):
    if   ax.upper() == 'X':
        bins = [ b, i1, i2]
    elif ax.upper() == 'Y':
        bins = [i1,  b, i2]
    elif ax.upper() == 'Z':
        bins = [i1, i2,  b]

    th3.SetBinContent(bins[0], bins[1], bins[2], c)
    #th3.SetBinError  (bins[0], bins[1], bins[2], e)
    
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
    newth3 = ROOT.TH3F(th3.GetName(), th3.GetTitle(), len(axes_arrays[0])-1, axes_arrays[0], len(axes_arrays[1])-1, axes_arrays[1], len(axes_arrays[2])-1, axes_arrays[2])
    return newth3
    

def rebinTH3(th3, axis, bins):
    if not axis in ['x', 'y', 'z', 'X', 'Y', 'Z']:
        sys.exit('trying to rebin a non-axis. exiting...')
    
    thaxis  = getattr(th3, 'Get{axis}axis'.format( axis=axis.upper() ) )()
    thaxis1 = getattr(th3, 'Get{axis}axis'.format( axis= 'Y' if axis.upper() == 'X' else 'X' ) )()
    thaxis2 = getattr(th3, 'Get{axis}axis'.format( axis= 'Y' if axis.upper() == 'Z' else 'Z' ) )()


    axes = [thaxis1, thaxis2]
    axes.insert((0 if axis.upper() == 'X' else 1 if axis.upper() == 'Y' else 2 ), bins )
    th3new = clone3DHisto(th3, axes); th3new.Sumw2()

    original_bins = [] 

    for i in range(1, thaxis.GetNbins()+1):
        original_bins.append( thaxis.GetBinLowEdge(i) )
        if i == thaxis.GetNbins():
            original_bins.append( thaxis.GetBinUpEdge(i) )
        
    if not min(bins) == min(original_bins) and not max(bins) == max(original_bins):
        sys.exit('trying to rebin with different axis boundaries. exiting')

    for i1 in range(1, thaxis1.GetNbins()+1):
        for i2 in range(1, thaxis2.GetNbins()+1):
            for ib, b in enumerate(bins):
                if not ib: continue
                if not b in original_bins:
                    sys.exit('trying to merge bins across boundaries of original histogram')
                bin_content = 0.
                bin_error2  = 0.
                for ob in range(original_bins.index(bins[ib-1])+1, original_bins.index(b)+1):
                    tmp_res = get3DBinContentError(th3, ob, i1, i2, axis)
                    bin_content += tmp_res[0]
                    bin_error2  += tmp_res[1]**2
                fill3DBinContentError(th3new, ib, i1, i2, axis, bin_content, math.sqrt(bin_error2))
            
    return th3new


th3 = ROOT.TH3F('foo', 'bar', 30, 0.,30., 15, -15., 15., 100, -25., 25.)
rand3 = ROOT.TRandom3(42)
for i in range(1000000):
    th3.Fill(rand3.Gaus(15,15), rand3.Uniform(-15,15), rand3.Gaus(10,15) )
foo = rebinTH3(th3, 'x', [i for i in range(31)])

counter = 0
for i in range(1, foo.GetNbinsX()+1):
    for j in range(1, foo.GetNbinsY()+1):
        for k in range(1, foo.GetNbinsZ()+1):
            counter += 1
            if not foo.GetBinContent(i,j,k) == th3.GetBinContent(i,j,k):
                print 'ijk:', i, j, k, foo.GetBinContent(i,j,k), th3.GetBinContent(i,j,k)
print 'counted', counter

c = ROOT.TCanvas()
x_orig = th3.ProjectionX(); x_orig.GetYaxis().SetRangeUser(0., 27000.)
x_new  = foo.ProjectionX(); x_new .GetYaxis().SetRangeUser(0., 27000.); x_new.SetLineColor(ROOT.kRed)

x_orig.Draw()
x_new .Draw('same')

