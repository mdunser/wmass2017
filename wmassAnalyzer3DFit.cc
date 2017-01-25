// UNCOMMENT TO USE PDF REWEIGHTING
//#define LHAPDF_ON

#ifdef LHAPDF_ON
  #include "LHAPDF/LHAPDF.h"
#endif 

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

#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"

#include "binning.h"
#include "nuisanceHistos.h"

#include <iostream>

using namespace std;

class wmassAnalyzer {

private:

    TTreeReader     &fTreeReader;



    // my functions hooray
    bool  fIsData;
    float fLumiWeight;
    Long64_t fNEntries;
    int fMaxEvents;
    int fCharge;
    int fNMasses;
    std::vector<int> fMassIDVec;
    std::vector<int>::const_iterator int_it;
    int fMassOffset;
    int fStartMass;
    int fNPDFsCT10;

    bool doGEN;

    // Declaration of the TTreeReaderValues
    // We could do something better with RV and type references. For later.
    TTreeReaderValue<Int_t>     evtHasGoodVtx   = {fTreeReader, "evtHasGoodVtx"   };
    TTreeReaderValue<Double_t>  parton1_pdgId   = {fTreeReader, "parton1_pdgId"   };
    TTreeReaderValue<Double_t>  parton1_x       = {fTreeReader, "parton1_x"       };
    TTreeReaderValue<Double_t>  parton2_pdgId   = {fTreeReader, "parton2_pdgId"   };
    TTreeReaderValue<Double_t>  parton2_x       = {fTreeReader, "parton2_x"       };
    TTreeReaderArray<Double_t>  LHE_weight      = {fTreeReader, "LHE_weight"      };
    TTreeReaderValue<Double_t>  tkmet           = {fTreeReader, "tkmet"           };
    TTreeReaderValue<Double_t>  genpfmet        = {fTreeReader, "genpfmet"        };
    TTreeReaderValue<Int_t>     evtHasTrg       = {fTreeReader, "evtHasTrg"       };
    TTreeReaderValue<Double_t>  W_pt            = {fTreeReader, "W_pt"            };
    TTreeReaderValue<Double_t>  W_mt            = {fTreeReader, "W_mt"            };
    TTreeReaderValue<Double_t>  WGen_pt         = {fTreeReader, "WGen_pt"         };
    TTreeReaderValue<Double_t>  WGen_rap        = {fTreeReader, "WGen_rap"        };
    TTreeReaderValue<Double_t>  WGen_mass       = {fTreeReader, "WGen_mass"       };
    TTreeReaderValue<Double_t>  WGen_mt         = {fTreeReader, "WGen_mt"         };
    TTreeReaderValue<Double_t>  Mu_pt           = {fTreeReader, "Mu_pt"           };
    TTreeReaderValue<Double_t>  Mu_eta          = {fTreeReader, "Mu_eta"          };
    TTreeReaderValue<Double_t>  Mu_phi          = {fTreeReader, "Mu_phi"          };
    TTreeReaderValue<Double_t>  Mu_charge       = {fTreeReader, "Mu_charge"       };
    TTreeReaderValue<Int_t>     MuIsTightAndIso = {fTreeReader, "MuIsTightAndIso" };
    TTreeReaderValue<Double_t>  MuGen_pt        = {fTreeReader, "MuGen_pt"        };
    TTreeReaderValue<Double_t>  MuGen_eta       = {fTreeReader, "MuGen_eta"       };
    TTreeReaderValue<Double_t>  MuGen_phi       = {fTreeReader, "MuGen_phi"       };
    TTreeReaderValue<Double_t>  MuGen_charge    = {fTreeReader, "MuGen_charge"    };

public :

    std::vector< std::pair< int, nuisanceHistos * > > h_mtPtEtaVec;
    std::vector< std::pair< int, nuisanceHistos * > >::const_iterator h_mtPtEtaVec_it;
    std::vector< float > fNuisanceWeights;

    // some extra histograms. not really necessary
    TH3F * h_nominal_mtPtEta;
    TH2F * h_pdfCheckUp;
    TH2F * h_pdfCheckDn;

    wmassAnalyzer(TTreeReader& treeReader, 
                  int charge = 1, 
                  float lumi = 20.,
                  bool doGen = false);

    ~wmassAnalyzer();

    void Loop();

    void RunJob(TString filename, bool isData = false);
    void Begin(TFile * f = nullptr);
    void End(TFile *);
    bool IsGoodEvent();
    
    // physics functions
    void fillHistograms();
    void fillPDFCheck();
    void setMaxEvents(int me){fMaxEvents = me;};
    TList* GetHistosList();
    
};

// #endif
// 
// #ifdef wmassAnalyzer_cxx
//
wmassAnalyzer::wmassAnalyzer(TTreeReader& treeReader, 
                             int charge, 
                             float lumi, 
                             bool doGen) : fTreeReader(treeReader) 
{

    doGEN = doGen;
    fMaxEvents = -1;
    fCharge = charge;
    // LHE_weight[101] has the central value stored. 80.398. it's not the right one, but whatever
    // each mass index is separated by 2 MeV
    fMassOffset = 101; 
    fNMasses    = 11;
    float fdeltaM     = 40;
    int massMinID   = fMassOffset - (int) fdeltaM/2.;
    int massMaxID   = fMassOffset + (int) fdeltaM/2.;
    int step = (massMaxID - massMinID )/fNMasses +1;
    while (massMinID <= massMaxID) {
        fMassIDVec.push_back(massMinID);
        massMinID += step;
    }
    // for (int_it = fMassIDVec.begin(); int_it != fMassIDVec.end(); int_it++){
    //     std::cout << *int_it << std::endl;
    // }
    
    fStartMass = (int) (fMassOffset - fNMasses/2. + 1);
    fNPDFsCT10 = 52;
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
    return;
}

void wmassAnalyzer::RunJob(TString filename, bool isData){ // this one is commented for some reason
   fIsData = isData;

   TFile *file = TFile::Open(filename, "recreate");
   //do the analysis
   Begin(file);
   Loop();
   End(file);
}
  
void wmassAnalyzer::Begin(TFile *file){ // book the histograms and all
    file->cd();
    int nbins_mt    =  70; float mt_min    = 50. ; float mt_max    = 120. ;
    int nbins_muEta =  10; float muEta_min = -2.1; float muEta_max =   2.1;
    int nbins_muPt  =  10; float muPt_min  = 30.0; float muPt_max  =  50.0;

    for (int_it = fMassIDVec.begin(); int_it != fMassIDVec.end(); int_it++){
        std::cout << "at mass index " << *int_it << " going to initialize stuff" << std::endl;
        nuisanceHistos * tmp_nH= new nuisanceHistos(*int_it, "pdf"); 
        h_mtPtEtaVec.push_back( std::make_pair(*int_it, tmp_nH) );
    }

    h_pdfCheckUp = new TH2F("pdfWeightUp", "pdfWeightUp", 120, 70, 100, 1000, -0.5, 30.);
    h_pdfCheckDn = new TH2F("pdfWeightDn", "pdfWeightDn", 120, 70, 100, 1000, -0.5, 30.);
    h_pdfCheckUp ->Sumw2();
    h_pdfCheckDn ->Sumw2();
}

void wmassAnalyzer::End(TFile *file){
    file->cd();

    for (h_mtPtEtaVec_it = h_mtPtEtaVec.begin(); h_mtPtEtaVec_it != h_mtPtEtaVec.end(); h_mtPtEtaVec_it++){
        h_mtPtEtaVec_it->second->writeHistos(file);
    }
        
    h_pdfCheckUp -> Write();
    h_pdfCheckDn -> Write();

    file->Close();
}

TList* wmassAnalyzer::GetHistosList(){

    // need this for map-reduce, but not at the moment

    Begin();
    Loop();

    auto l = new TList();
    l->Add(h_nominal_mtPtEta);
    // for (int m=0; m< fNMasses; m++) {
    //     for (int p = 0; p<fNPDFsCT10+1; p++){
    //         l->Add(h_mtPtEta[m][p]);
    //     }
    // }

    l->Add(h_pdfCheckUp);
    l->Add(h_pdfCheckDn);

    return l;
}

bool wmassAnalyzer::IsGoodEvent()
{
    if(!*evtHasGoodVtx)      return false;
    if(!*evtHasTrg)          return false;
    if(*tkmet  < 25.)        return false;
    if(!*MuIsTightAndIso)    return false;
    if(std::abs(*WGen_rap)  > 0.5)  return false;
    if(*W_pt  > 10.)  return false; // upper cut on W-pt

    // very basic event selection
    if (doGEN) {
        if(*MuGen_pt  < 20.)           return false;
        if(*WGen_mt   < 30.)           return false;
        if(std::abs(*MuGen_eta) > 2.1) return false;
    }
    else {
        if(*Mu_pt  < 20.)           return false;
        if(*W_mt   < 30.)           return false;
        if(std::abs(*Mu_eta) > 2.1) return false;
    }
    return true;
}

void wmassAnalyzer::Loop()
{
    TStopwatch stopWatch;
    stopWatch.Start();

    if (fMaxEvents > 0) std::cout << " running on only " << fMaxEvents << " events " << std::endl;

    Long64_t loopedEvents = 0;

    while (fTreeReader.Next()) {
        if ( loopedEvents > 0 && loopedEvents%((int) pow(10, ((int)TMath::Log10(loopedEvents))) )== 0) cout << ">>> Processing event # " << loopedEvents << endl;

        // keep count
        loopedEvents++;

        // break if looped enough
        if (fMaxEvents > 0 && loopedEvents >= fMaxEvents) break;

        // basic event selection
        if (!IsGoodEvent()) continue;

        // do relevant stuff here
        fillHistograms();
        fillPDFCheck();

    } // end loop on events with fTreeReader

    double elapsed = stopWatch.RealTime();
    cout << "it took " << elapsed << " seconds to loop on " << loopedEvents << " events" << endl;
    cout << loopedEvents/elapsed << " ev/s" << endl;

} // end Loop() function

void wmassAnalyzer::fillHistograms(){

    float wgt;
    float pt  = (doGEN ? *MuGen_pt  : *Mu_pt );
    float eta = (doGEN ? *MuGen_eta : *Mu_eta);
    float mt  = (doGEN ? *WGen_mt   : *W_mt  );

    // fill the nominal histogram
    // h_nominal_mtPtEta ->Fill(eta, pt, mt, fLumiWeight*LHE_weight[309]*LHE_weight[101]);

    for (h_mtPtEtaVec_it = h_mtPtEtaVec.begin(); h_mtPtEtaVec_it != h_mtPtEtaVec.end(); h_mtPtEtaVec_it++){
        // this is the weight for lumi and the correct mass:
        wgt = fLumiWeight * LHE_weight[ h_mtPtEtaVec_it->first ];

        if ( h_mtPtEtaVec_it->second->isPdfUncertainty ){
            for (int i = 309; i < 362; ++i){
                fNuisanceWeights.push_back( wgt * LHE_weight[i] ); // stores all the weights for the pdf uncertainties
            }
        }

        fNuisanceWeights = h_mtPtEtaVec_it->second->fillHistos(eta, pt, mt, fNuisanceWeights); // this function resets the fNuisanceWeights!
        
    }

} // end fillMTandETAHistograms

void wmassAnalyzer::fillPDFCheck(){

    float x1 = *parton1_x; float id1 = *parton1_pdgId;
    float x2 = *parton2_x; float id2 = *parton2_pdgId;

    for (int p = 0; p<fNPDFsCT10+1; p++){
        if (fCharge > 0){
            if ( !( (id1 ==  2 && id2 == -1) || (id2 ==  2 && id1 == -1)) ) continue;
        }
        else {
            if ( !( (id1 == -2 && id2 ==  1) || (id2 == -2 && id1 ==  1)) ) continue;
        }
        // cout << " val: " << TMath::Sqrt(x1*x2*7000*7000) << " mW " << WGen_mass << " LHE_weight[309+p]/LHE_weight[309]+( (int) p/2 ): " << LHE_weight[309+p]/LHE_weight[309]+( (int) p/2 ) << endl;
        if (doGEN && p%2 == 1) h_pdfCheckUp ->Fill(TMath::Sqrt(x1*x2*7000*7000), LHE_weight[309+p]/LHE_weight[309]+( (int) p/2 )  );
        if (doGEN && p%2 == 0) h_pdfCheckDn ->Fill(TMath::Sqrt(x1*x2*7000*7000), LHE_weight[309+p]/LHE_weight[309]+( (int) p/2 )-1);
    } // end for loop over pdf variations

} // end fillPDFCheck function

#endif // #ifdef wmassAnalyzer_cxx
