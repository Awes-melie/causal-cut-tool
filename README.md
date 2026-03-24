# causal-cut-tool
Implementation of the Causal Cut library as a usable tool. 
Run with `./causal_cut.sh datafile.pqt`.
## Environment setup
This project uses uv to manage the python environment. Setup the
environment by installing uv and then (in the causal_cut_tool directory) 
running:

`uv pip install -e .`

`uv run bash ./causal_cut.sh [DATAFILE TO TEST].pqt`

## Adapting the tool
In order to run your system using the tool, you will need to allow the tool to call a method that can run your system 
(or model of your system). This can be done in the causal_cut_plugin directory. Details about the implementation needed
can be found in the tutorial.ipynb file along with information about the data that needs to be provided.

TODO:
- Descriptions of datafiles
- Strip down datafiles