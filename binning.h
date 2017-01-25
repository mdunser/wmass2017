
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
