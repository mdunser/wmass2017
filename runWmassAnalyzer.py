#!/usr/bin/env python
import sys, os
import os.path as osp
import string, random

def randomid(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def getEOSlslist(directory, mask='', prepend='root://eoscms//eos/cms'):
    '''Takes a directory on eos (starting from /store/...) and returns
    a list of all files with root://eoscms//eos/cms/ prepended'''
    from subprocess import Popen, PIPE
    print 'looking into:',directory,'...'

    #eos_cmd = '/afs/cern.ch/project/eos/installation/0.2.41/bin/eos.select'
    eos_cmd = '/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'
    os.environ['X509_USER_PROXY'] = '/afs/cern.ch/user/m/mdunser/private/proxy/myproxy'
    data = Popen([eos_cmd, 'ls', '/eos/cms/'+directory],
                stdout=PIPE)
    out,err = data.communicate()

    full_list = []

    ## if input file was single root file:
    if directory.endswith('.root'):
        if len(out.split('\n')[0]) > 0:
            return [prepend + directory]

    for line in out.split('\n'):
        if len(line.split()) == 0: continue
        if not '.root' in line: continue
        ## instead of only the file name append the string
        ## to open the file in ROOT
        full_list.append('/'.join([prepend,directory,line]))

    ## strip the list of files
    if mask != '':
        stripped_list = [x for x in full_list if mask in x]
        return stripped_list
    ## if no mask given, run over all files
    else:
        return full_list

def cacheLocally(infile, tmpDir='/tmp/'):
    return infile
    #tmpfile = osp.join(tmpDir, osp.basename(infile))
    tmpfile = osp.join('/tmp/mdunser/', osp.basename(infile))

    print 'the target file in the tmp directory is', tmpfile

    # Copy locally if it's not there already
    if not osp.exists(tmpfile):
        xrcmd = "xrdcp {s} {t}".format(s=infile, t=tmpfile)
        #xrcmd = "cmsStage {s} {t}".format(s=infile[infile.find('/store'):], t=tmpfile) # cmsStage copy command
        print " transferring %s to %s" % (infile, tmpfile)
        os.environ['X509_USER_PROXY'] = '/afs/cern.ch/user/m/mdunser/private/proxy/myproxy'
        print 'this is the output of the X509_USER_PROXY:', os.environ['X509_USER_PROXY']
        print '================================================================'
        print '= running command: {cmd}'.format(cmd=xrcmd)
        print '================================================================'
        os.system(xrcmd)
        if osp.exists(tmpfile): print '... copied successfully'
        else: print 'copying unsuccessful. boh.'
    print 'THIS IS THE LS OF THE TMPDIR'
    print os.listdir(tmpDir)
    print 'THIS IS THE LS OF /tmp/'
    print os.listdir('/tmp/mdunser/')

    if osp.exists(tmpfile): infile = tmpfile
    #return infile
    print 'returning the file to process', tmpfile
    print 'does it exist though?', osp.isfile(tmpfile)
    return tmpfile

def runBatch(infiles):
    jobs = []
    for i,f in enumerate(infiles):
        randstr = randomid(6)
        runfilename = 'tmp/job_%s.sh'%randstr
        print f.split('/')[-1]
        tmp_file = open('batchSubmissionScript.sh','r')
        tmp_data = tmp_file.read()
        tmp_file.close()
        os.system('mkdir -p tmp/')
        thisdir = osp.abspath('.')
        
        tmp_data = tmp_data.replace('AAA', '/afs/cern.ch/work/m/mdunser/public/wmass/restartSeptember/')
        tmp_data = tmp_data.replace('BBB', f.split('/')[-1])
        tmp_data = tmp_data.replace('CCC', opts.outDir)
        tmp_data = tmp_data.replace('XXX', thisdir+'/'+opts.libfile)
        tmp_data = tmp_data.replace('YYY', __file__)
        tmp_data = tmp_data.replace('ZZZ', args[0])
        tmp_data = tmp_data.replace('DDD', thisdir)
        tmp_data = tmp_data.replace('EEE', str(opts.charge))
        tmp_data = tmp_data.replace('FFF', str(opts.lumi))
        tmp_data = tmp_data.replace('GGG', '--gen' if opts.doGEN else '')
        
        outfile = open(runfilename,'w')
        outfile.write(tmp_data)
        outfile.close()
        jobs.append('bsub -q %s -J %s < %s'%(opts.queue,randstr,runfilename))
    for job in jobs:
        print 'running:', job
        if not opts.pretend: os.system(job)


def run((infile, outfile, opts)):
    print 'this is the weird thing:', os.environ.get('TMPDIR', '/tmp')
    if infile.startswith("root://"):
        infile = cacheLocally(infile, os.environ.get('TMPDIR', '/tmp'))

    from ROOT import TFile
    print 'opening file: {infile}'.format(infile=infile)
    fb = TFile.Open(infile)
    tree = fb.Get("WTreeProducer")

    try: tree.GetName()
    except ReferenceError:
        print "Error: tree not found in %s" % infile
        return False
    print "... processing %s" %infile


    from ROOT import gSystem, TChain

    ## Load the previously compiled shared object library into ROOT
    print '... loading shared object library from %s'%opts.libfile
    gSystem.Load(opts.libfile)
    ## Load it into PyROOT (this is where the magic happens)
    from ROOT import wmassAnalyzer, TTreeReader

    treeReader = TTreeReader("WTreeProducer", fb)
    ana = wmassAnalyzer(treeReader, opts.charge, opts.lumi, opts.doGEN)

    if opts.maxEntries > 0:
        ana.setMaxEvents(opts.maxEntries)

    ## Check if it's data or MC
    isdata = 'Run2015' in osp.basename(infile)

    ## Run the loop
    ana.RunJob(outfile, isdata)
    fb.Close()

    return True

if __name__ == '__main__':
    from optparse import OptionParser
    usage = """%prog [opts] inputDir

    Notes:
    - Compile wmassAnalyzer.cc first with ACLiC like so:
       > root -l wmassAnalyzer.cc+
      This will produce the library file
    - Errors of <TTree::SetBranchAddress>: unknown branch occur
      for the MC-only branches when running on data.
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-m", "--maxEntries", dest="maxEntries", type="int", default=-1, help="Max entries to process"); 
    parser.add_option("-j", "--jobs", dest="jobs", type="int", default=0, help="Use N threads");
    parser.add_option("-p", "--pretend", dest="pretend", action="store_true", default=False, help="Don't run anything"); 
    parser.add_option("-b", "--batch", dest="batch", action="store_true", default=False, help="Run on the batch system");
    parser.add_option("-c", "--charge", dest="charge", action="store", type=int, default=1, help='charge of the sample. default is plus');
    parser.add_option("-l", "--lumi", dest="lumi", action="store", type=float, default=1., help='integrated luminosity in fb-1. default is %default')
    parser.add_option("-o", "--outDir", default="tnptrees", action="store", type="string", dest="outDir", help="Output directory for trees " "[default: %default/]")
    parser.add_option("-q", "--queue", default='8nh', type="string", dest="queue", help="Submit to specific queue " "[default: %default/]")
    parser.add_option("--doGEN", "--gen", default=False, action="store_true", dest="doGEN", help="do generator study instead of reco") 
    parser.add_option("-f", "--filter", default='', type="string", dest="filter", help="Comma separated list of filters to apply " "[default: %default/]")
    parser.add_option("--libfile", default='wmassAnalyzer3DFit_cc.so', type="string", dest="libfile", help="libfile to run " "[default: %default/]")

    global opts, args
    (opts, args) = parser.parse_args()

    os.environ['X509_USER_PROXY'] = '/afs/cern.ch/user/m/mdunser/private/proxy/myproxy'

    # Collect all input:
    idir = args[0]
    print idir
    if osp.exists(idir):
        if osp.isdir(idir):
            inputfiles = [osp.join(idir,f) for f in os.listdir(idir)
                                     if osp.splitext(f)[1] == '.root']
        elif osp.isfile(idir) and idir.endswith('.root'):
            inputfiles = [idir]
    elif idir.startswith('/store/') or idir.startswith('root://'):
        inputfiles = getEOSlslist(idir)
    else:
        parser.print_help()
        sys.exit(-1)

    # Apply filter (if more than one file)
    if len(inputfiles) > 1 and len(opts.filter.split(','))>0:
        filters = opts.filter.split(',')
        print "Will filter for", filters
        inputfiles = [i for i in inputfiles if
                                    any([(f in i) for f in filters])]

    print "Will process the following files:"
    for ifile in inputfiles: print ifile

    if opts.batch:
        print 'running on the batch'
        runBatch(inputfiles)

    else:
        os.system('mkdir -p %s'%(opts.outDir))

        # Assemble tasks
        tasks = []
        for ifile in inputfiles:
            oname = '%s_W%s_Lumi%d.root' % (osp.splitext(osp.split(ifile)[1])[0],'plus' if opts.charge > 0 else 'minus', int(opts.lumi))
            ofile = osp.join(opts.outDir, oname)
            tasks.append((ifile,ofile,opts))

        if opts.jobs > 0 and len(tasks) > 1:
            print "Running in parallel using %d jobs" % opts.jobs
            from multiprocessing import Pool
            pool = Pool(opts.jobs)
            pool.map(run, tasks)

        else:
            print "Running sequentially"
            map(run, tasks)

