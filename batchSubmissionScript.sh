# Lxplus Batch Job Script

export WMASS_SO="XXX"
export PY_WRAPPER="YYY"
export EOS_DIR="ZZZ"
export BASEDIR="AAA"
export FILENAME="BBB"
export OUTDIR="CCC"
export THISDIR="DDD"
export CHARGE="EEE"
export LUMI="FFF"

echo "BATCH: i am here"
$PWD
echo "BATCH: this is in the directory"
$LS
echo "BATCH: getting the shared object..."
cp $WMASS_SO .
echo "ensuring the output directory exists"
mkdir -p $BASEDIR/$OUTDIR
echo "BATCH: copying the executable here"
cp $THISDIR/$PY_WRAPPER .
echo "==========================================================================="
echo "=============== i am going to run this command ============================"
echo python $PY_WRAPPER $EOS_DIR  -o $BASEDIR/$OUTDIR/ -f $FILENAME -c $CHARGE -l $LUMI
echo "==========================================================================="
echo "==========================================================================="
echo "BATCH: starting the job"
python $PY_WRAPPER $EOS_DIR  -o $BASEDIR/$OUTDIR/ -f $FILENAME -c $CHARGE -l $LUMI
