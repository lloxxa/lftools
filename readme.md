The following directories must be in your PYTHONPATH for the functions to run:

PATH_TO_LFTOOLS/lftools/
PATH_TO_LFTOOLS/lftools/tspscripts
PATH_TO_LFTOOLS/lftools/pyCONTIN/dev

export PYTHONPATH=$PYTHONPATH:PATH_TO_LFTOOLS/lftools:PATH_TO_LFTOOLS/lftools/tspscripts:PATH_TO_LFTOOLS/lftools:pyCONTIN/dev

Alternatively,you may add them to an anaconda environment by running

conda install conda-build
conda develop PATH_TO_LFTOOLS/lftools/
conda develop PATH_TO_LFTOOLS/lftools/tspscripts
conda develop PATH_TO_LFTOOLS/lftools/pyCONTIN/dev
