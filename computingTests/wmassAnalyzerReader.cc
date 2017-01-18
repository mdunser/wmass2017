#ifndef wmassAnalyzer_h
#define wmassAnalyzer_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

#include <TH1.h>
#include <TH2.h>
#include <TH3.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TMath.h>
#include <TStopwatch.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>


#include <iostream>

using namespace std;

class wmassAnalyzer {
public :
    TTree          *fChain;   //!pointer to the analyzed TTree or TChain
    Int_t           fCurrent; //!current Tree number in a TChain

    bool doGEN;


    wmassAnalyzer(TTree *tree=0, int charge = 1, float lumi = 1., bool doGen = false);
    virtual ~wmassAnalyzer();
    virtual Int_t    GetEntry(Long64_t entry);
    virtual Long64_t LoadTree(Long64_t entry);
    virtual void     Init(TTree *tree);
    virtual void     Loop(TFile *);
    virtual Bool_t   Notify();
    virtual void     Show(Long64_t entry = -1);


    // my functions hooray
    bool  fIsData;
    float fLumiWeight;
    Long64_t fNEntries;
    int fMaxEvents;
    int fCharge;
    int fNMasses;
    int fMassOffset;
    int fStartMass;
    int fNPDFsCT10;
    virtual void RunJob(TString, bool);
    virtual void Begin(TFile *);
    virtual void End(TFile *);
    virtual bool IsGoodEvent();
    virtual void fillHistograms(float, float, float, float);
    virtual void setMaxEvents(int me){fMaxEvents = me;};
    
    //TH2F * nominal_mtEta;
    TH3F * h_nominal_mtPtEta;
    TH3F * h_mtPtEta[21][53];
    TH2F * h_pdfCheckUp;
    TH2F * h_pdfCheckDn;

    

};

// #endif
// 
// #ifdef wmassAnalyzer_cxx
//
wmassAnalyzer::wmassAnalyzer(TTree *tree, int charge, float lumi, bool doGen) : fChain(0) 
{

    doGEN = doGen;
    fMaxEvents = -1;
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
    if (tree == 0) {
       TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("/afs/cern.ch/work/m/mdunser/public/wmass/WTreeProducer_tree_6p2.root");
       if (!f || !f->IsOpen()) {
          f = new TFile("/afs/cern.ch/work/m/mdunser/public/wmass/WTreeProducer_tree_6p2.root");
       }
       f->GetObject("WTreeProducer",tree);

    }
    fCharge = charge;
    fMassOffset= 101; // LHE_weight[101] has the central value stored. 80.398. it's not the right one, but whatever
    fNMasses   = 21;
    fStartMass = (int) (fMassOffset - fNMasses/2. + 1);
    fNPDFsCT10 = 52;
    Init(tree);
    float nGen, xsec;
    if (charge > 0){
        // nGen = 131310100;
        nGen = 131330600;
        //xsec = 5913000; // xsec at 7 TeV in fb
        xsec = 7213400; // xsec at 8 TeV in fb
    }
    else{
        // nGen = 109963100;
        nGen = 110587500;
        //xsec = 4126000; // xsec at 7 TeV in fb 
        xsec = 5074700; // xsec at 8 TeV in fb
    }
    fLumiWeight = lumi*xsec/nGen;
    cout << "----- running on W "<< charge << "-----------" << endl;
    cout << "this run will have a luminosity weight of : " << fLumiWeight << endl;
    cout << " doing GEN? : " << doGEN << endl;
}

wmassAnalyzer::~wmassAnalyzer()
{
    if (!fChain) return;
    delete fChain->GetCurrentFile();
}

Int_t wmassAnalyzer::GetEntry(Long64_t entry)
{
// Read contents of entry.
    if (!fChain) return 0;
    return fChain->GetEntry(entry);
}
Long64_t wmassAnalyzer::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
    if (!fChain) return -5;
    Long64_t centry = fChain->LoadTree(entry);
    if (centry < 0) return centry;
    if (fChain->GetTreeNumber() != fCurrent) {
       fCurrent = fChain->GetTreeNumber();
       Notify();
    }
    return centry;
}

void wmassAnalyzer::Init(TTree *tree)
{
    // The Init() function is called when the selector needs to initialize
    // a new tree or chain. Typically here the branch addresses and branch
    // pointers of the tree will be set.
    // It is normally not necessary to make changes to the generated
    // code, but the routine can be extended by the user if needed.
    // Init() will be called many times when running on PROOF
    // (once per file to be processed).

    // Set branch addresses and branch pointers
    if (!tree) return;
    fChain = tree;
    fCurrent = -1;
    fChain->SetMakeClass(1);

    Notify();
}

Bool_t wmassAnalyzer::Notify()
{
    return kTRUE;
}

void wmassAnalyzer::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
    if (!fChain) return;
    fChain->Show(entry);
}


void wmassAnalyzer::RunJob(TString filename, bool isData){
   fIsData = isData;

   TFile *file = TFile::Open(filename, "recreate");
   //do the analysis
   Begin(file);
   Loop(file);
   End(file);
}
  
void wmassAnalyzer::Begin(TFile *file){ // book the histograms and all
    file->cd();
    int nbins_mt    =  70; float mt_min    = 50. ; float mt_max    = 120. ;
    int nbins_muEta =  10; float muEta_min = -2.1; float muEta_max =   2.1;
    int nbins_muPt  =  10; float muPt_min  = 30.0; float muPt_max  =  50.0;

    // make histograms for mt and muEta
    h_nominal_mtPtEta = new TH3F("h_nominal_mtPtEta", "h_nominal_mtPtEta", nbins_muEta, muEta_min, muEta_max, nbins_muPt, muPt_min, muPt_max, nbins_mt, mt_min, mt_max);
    h_nominal_mtPtEta ->Sumw2();
    for (int m=0; m< fNMasses; m++){
        for (int p = 0; p<fNPDFsCT10+1; p++){
            h_mtPtEta[m][p] = new TH3F(Form("h_mtPtEta_m%d_p%d",m+fStartMass,p), Form("h_mtPtEta_m%d_p%d",m+fStartMass,p), nbins_muEta, muEta_min, muEta_max, nbins_muPt, muPt_min, muPt_max, nbins_mt, mt_min, mt_max);
            h_mtPtEta[m][p] ->Sumw2();
        } // end loop on pdf variations
    } // end loop on masses
    h_pdfCheckUp = new TH2F("pdfWeightUp", "pdfWeightUp", 120, 70, 100, 1000, -0.5, 30.);
    h_pdfCheckDn = new TH2F("pdfWeightDn", "pdfWeightDn", 120, 70, 100, 1000, -0.5, 30.);
    h_pdfCheckUp ->Sumw2();
    h_pdfCheckDn ->Sumw2();
}

void wmassAnalyzer::End(TFile *file){
    file->cd();
    h_nominal_mtPtEta -> Write();
    for (int m=0; m< fNMasses; m++){
        for (int p = 0; p<fNPDFsCT10+1; p++){
            h_mtPtEta[m][p] -> Write();
        }
    }
    //file->Write();

    h_pdfCheckUp -> Write();
    h_pdfCheckDn -> Write();

    gROOT->SetBatch();
    TCanvas * c = new TCanvas("sanity_check_pdfs", "sanity_check_pdfs", 800, 600);
    c->cd();
    h_nominal_mtPtEta->Project3D("yx")->Draw("");
    for (int i = 2; i<10; i++){
        h_mtPtEta[5][i] ->SetLineColor(i); 
        h_mtPtEta[5][i]->ProjectionY()->Draw("same");
    }
    c->Write();
    c->Clear();
    c->SetName("sanity_check_masses");
    for (int i = 0; i<7; i++){
        h_mtPtEta[i][0] ->SetLineColor(i+1); 
        h_mtPtEta[i][0] ->SetMarkerStyle(20+i);
        cout << "mean for mass " << i+fStartMass << " : " << h_mtPtEta[i][0]->GetMean() << endl;
        h_mtPtEta[i][0]->ProjectionX()->Draw("same");
    }
    c->Write();
    
    file->Close();
}

bool wmassAnalyzer::IsGoodEvent()
{
    return true;
}

void wmassAnalyzer::Loop(TFile * myFile)
{
    TStopwatch stopWatch;
    stopWatch.Start();

    //     This is the loop skeleton where:
    //    jentry is the global entry number in the chain
    //    ientry is the entry number in the current Tree
    //  Note that the argument to GetEntry must be:
    //    jentry for TChain::GetEntry
    //    ientry for TTree::GetEntry and TBranch::GetEntry

    if (fMaxEvents > 0) cout << " running on only " << fMaxEvents << " events " << endl;
    if (fChain == 0) return;

    fNEntries = fChain->GetEntriesFast();

    Long64_t loopedEvents = 0;

    cout << "myfile->isopen " << myFile->IsOpen() << endl;

    TTreeReader myReader(fChain);
    TTreeReaderValue<Double_t> pt (myReader, "Mu_pt");
    TTreeReaderValue<Double_t> eta(myReader, "Mu_eta");
    TTreeReaderValue<Double_t> mt (myReader, "W_mt");
    //TTreeReaderValue<std::vector<Double_t> > wgt(myReader, "LHE_weight"); // how do i get the whole array then? can i get a vector?
    TTreeReaderArray<Double_t> wgt(myReader, "LHE_weight"); // this thing tells me LHE_weight is a Double.
    
    std::cout << "this is the reader.getentries " << myReader.GetEntries(true) << std::endl;

    while (myReader.Next()) {
     // Just access the data as if myPx and myPy were iterators (note the '*' in front of them):
        fillHistograms(*pt, *eta, *mt, wgt[309] );
        loopedEvents++;
        if (loopedEvents > 1000) break;
    }

    double elapsed = stopWatch.RealTime();
    cout << "it took " << elapsed << " seconds to loop on " << loopedEvents << " events" << endl;
    cout << loopedEvents/elapsed << " ev/s" << endl;

} // end Loop() function

void wmassAnalyzer::fillHistograms(float pt, float eta, float mt, float wgt){

    // fill the nominal histogram
    h_nominal_mtPtEta ->Fill(eta, pt, mt, wgt);

} // end fillMTandETAHistograms


#endif // #ifdef wmassAnalyzer_cxx
