#include "TString.h"

struct binning {
    int nbins_mt   ; float mt_min   ; float mt_max   ;
    int nbins_muEta; float muEta_min; float muEta_max;
    int nbins_muPt ; float muPt_min ; float muPt_max ;

    binning(){ setValues();};
    
    void setValues(){
    nbins_mt    =  70; mt_min    = 50. ; mt_max    = 120. ;
    nbins_muEta =  10; muEta_min = -2.1; muEta_max =   2.1;
    nbins_muPt  =  10; muPt_min  = 30.0; muPt_max  =  50.0;
    };

};

class nuisanceHistos {
public:
    int fMassID;
    binning fBins;
    TString fNuisName;
    std::vector< std::pair< int, TH3F * > > h_mtPtEta;

    bool isPdfUncertainty = false;

    nuisanceHistos();
    nuisanceHistos(int mass, TString nuisanceName, binning bins);
    ~nuisanceHistos();
    void testFunction(TString a) {std::cout << fMassID << "  " << a << std::endl;};
    void checkAndInit();

    std::vector<float> fillHistos(float, float, float, std::vector<float>);
    void writeHistos(TFile *);
    

};

nuisanceHistos::nuisanceHistos(int mass, TString nuisanceName, binning bins){
    fMassID = mass; 
    fNuisName = nuisanceName; 
    fBins = bins;
    testFunction(fNuisName);
    checkAndInit();
}

void nuisanceHistos::checkAndInit(){
    int nVariations = -1;
    TString nuisShort;
    if (fNuisName.Index("pdf") != -1) {
        std::cout << "pdf is in the string" << std::endl;
        nVariations = 53;
        nuisShort = "p";
        isPdfUncertainty = true;
    }
    else if (fNuisName.Index("super") != -1) {
        std::cout << "super is in the string" << std::endl;
    }

    for (int var = 0; var<nVariations; var++){
        TH3F * tmp_h = new TH3F( Form("h_mtPtEta_m%d_"+nuisShort+"%d", fMassID, var), Form("h_mtPtEta_m%d_"+nuisShort+"%d", fMassID, var), 
                                 fBins.nbins_muEta, fBins.muEta_min, fBins.muEta_max, 
                                 fBins.nbins_muPt , fBins.muPt_min , fBins.muPt_max , 
                                 fBins.nbins_mt   , fBins.mt_min   , fBins.mt_max   ); tmp_h->Sumw2();
        h_mtPtEta.push_back( std::make_pair(var, tmp_h) );
    } // end loop on pdf variations

    std::cout << Form("done initializing nuisance "+fNuisName+" with %d variations", h_mtPtEta.size()) << std::endl;

}

std::vector<float> nuisanceHistos::fillHistos(float eta, float pt, float mt, std::vector<float> weightsVec){
    if (weightsVec.size() != h_mtPtEta.size() ){
        std::cout << Form("YOU ARE TRYING TO FILL UNCERTAINTY "+fNuisName+" WITH A DIFFERENT SIZED VECTOR!!") << std::endl;
        exit(0);
    }
    for (int i = 0; i < h_mtPtEta.size(); i++){
        // std::cout << "mass " << fMassID << " at variation in float vector " << i << " filling histogram with var " << h_mtPtEta[i].first << " with name " << h_mtPtEta[i].second->GetName() << std::endl;
        h_mtPtEta[i].second->Fill( eta, pt, mt, weightsVec[ i ] );
    }
    weightsVec.clear();
    return weightsVec;
}

void nuisanceHistos::writeHistos(TFile * f){
    f->cd();
    for (int i = 0; i < h_mtPtEta.size(); i++){
        h_mtPtEta[i].second->Write();
    }
}
