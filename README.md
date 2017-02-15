# wmass
run the python wrapper:
=======================

## root://eoscms.cern.ch//eos/cms/

## the files with the WTreeProducer trees are:
## /store/group/phys_smp/Wmass/perrozzi/ntuples/ntuples_2014_05_23_53X/WMinusPOWHEG/InclWeights/
##      WTreeProducer_tree_1p1.root    WTreeProducer_tree_1p5.root    WTreeProducer_tree_2p3.root    WTreeProducer_tree_3p2.root
##      WTreeProducer_tree_1p2.root    WTreeProducer_tree_1p6.root    WTreeProducer_tree_2p4.root    WTreeProducer_tree_3p3.root
##      WTreeProducer_tree_1p3.root    WTreeProducer_tree_2p1.root    WTreeProducer_tree_2p5.root    WTreeProducer_tree_3p4.root
##      WTreeProducer_tree_1p4.root    WTreeProducer_tree_2p2.root    WTreeProducer_tree_3p1.root    WTreeProducer_tree_3p5.root
## /store/group/phys_smp/Wmass/perrozzi/ntuples/ntuples_2014_05_23_53X/WPlusPOWHEG/InclWeights/
##      WTreeProducer_tree_5p1.root    WTreeProducer_tree_4p1.root    WTreeProducer_tree_3p1.root    WTreeProducer_tree_2p1.root    WTreeProducer_tree_1p1.root
##      WTreeProducer_tree_5p2.root    WTreeProducer_tree_4p2.root    WTreeProducer_tree_3p2.root    WTreeProducer_tree_2p2.root    WTreeProducer_tree_1p2.root
##      WTreeProducer_tree_6p1.root    WTreeProducer_tree_4p3.root    WTreeProducer_tree_3p3.root    WTreeProducer_tree_2p3.root    WTreeProducer_tree_1p3.root
##      WTreeProducer_tree_6p2.root    WTreeProducer_tree_4p4.root    WTreeProducer_tree_3p4.root    WTreeProducer_tree_2p4.root    WTreeProducer_tree_1p4.root


## how to run the wmass analyzer:

# python runWmassAnalyzer.py /store/group/phys_smp/Wmass/perrozzi/ntuples/ntuples_2014_05_23_53X/WPlusPOWHEG/InclWeights/  -o <date>-<name> -c <charge 1/-1>  -l <lumi> 
# additional options
#   -m <maxevents optional> 
#   -f <runonsinglefile> 
#   -gen
# submitting to batch
#    -b -q 8nh

## compile the code in root:
#    root
#    .L wmassAnalyzer3DFit.cc+
# makes a wmassAnalyzer3DFit_cc.so shared object

##




## =============================================================
## =============================================================
## FORGET ABOUT WHAT IS WRITTEN BELOW THIS LINE.
## =============================================================
## =============================================================

## combine commands

## combine   -M MaxLikelihoodFit --saveNLL datacardShapes.txt -t -1                 --expectSignal=1     -S 1
##               do NLL           save it                     use asimov dataset    normalization        with/without systematics (bounds should change)
## 
## ## or do all masses at once
## for i in {0..201}; do combine   -M MaxLikelihoodFit --saveNLL -m $i datacardMass${i}.txt -t -1 --expectSignal=1     -S 1; done
## 
## 
## ## make asimov toy dataset from nominal mass (ID95)
## combine datacardMass95.txt -M GenerateOnly -m 888 -t -1 --expectSignal=1 --saveToys -S 0
## 
## text2workspace.py datacardMass95.txt -o shit.root
## 
## ## combining 
## combine datacard2.txt -M MaxLikelihoodFit --toysFile <fileWithToy>  -t -1 --saveNLL
## 
## combine datacardMass${i}.txt -M MaxLikelihoodFit --toysFile higgsCombineTest.GenerateOnly.mH999.123456.root  -t -1  --saveNLL -m 100${i} 
## 
## for i in {0..201}; do combine   -M MaxLikelihoodFit --toysFile higgsCombineTest.GenerateOnly.mH999.123456.root --saveNLL -m $i datacardMass${i}.txt -t -1 -S 1; done

