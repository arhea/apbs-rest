#!/bin/bash

# Used specifically with directory structure for Elvis
# Not guaranteed to work for the directory structure of whoever clones this
# Directory structure I'm working with (everything listed below is a dir):
#   +-- Parent_directory
#   |   +-- react_flask_pdb2pqr (root directory of repo)
#   |       +-- PDB2PQR_web
#   |
#   |   +-- antd_pdb2pqr
#   |       +-- build
#   |
#   |   +-- builds
#   |       +-- pdb2pqr_build


# This script sets up the symbolic links in order for development to be easier

ln -s ../builds/pdb2pqr_build ./pdb2pqr_build

cd PDB2PQR_web
ln -s ../../antd_pdb2pqr/build ./build
cd ..

cd ../builds/pdb2pqr_build
ln -s ../../apbs-rest/src/pdb2pqr_build_materials/main_cgi.py main_cgi.py
ln -s ../../apbs-rest/src/pdb2pqr_build_materials/querystatus.py querystatus.py
ln -s ../../apbs-rest/src/pdb2pqr_build_materials/apbs_cgi.py apbs_cgi.py
ln -s ../../apbs-rest/src/workflow/legacy/weboptions.py weboptions.py

cd ../../apbs-rest/src/workflow/legacy/
ln -s ../../../../builds/pdb2pqr_build/main_cgi.py
ln -s ../../../../builds/pdb2pqr_build/apbs_cgi.py
ln -s ../../../../builds/pdb2pqr_build/src/
ln -s ../../../../builds/pdb2pqr_build/dat/
ln -s ../../../../builds/pdb2pqr_build/main.pyc

ln -s ../../../../builds/pdb2pqr_build/extensions/
ln -s ../../../../builds/pdb2pqr_build/pdb2pka/
ln -s ../../../../builds/pdb2pqr_build/propka30/

cd ../../apbs-rest/src/tmp_task_exec/legacy/
ln -s ../../../../builds/pdb2pqr_build/src/
ln -s ../../../../builds/pdb2pqr_build/main.pyc

ln -s ../../../../builds/pdb2pqr_build/extensions/
ln -s ../../../../builds/pdb2pqr_build/pdb2pka/
ln -s ../../../../builds/pdb2pqr_build/propka30/

# cd ../../apbs-rest/src/workflow/legacy/src
# ln -s ../../../../../builds/pdb2pqr_build/src/utilities.pyc utilities.pyc
# ln -s ../../../../../builds/pdb2pqr_build/src/aconf.pyc aconf.pyc
cd ../../apbs-rest


# ln -s ../../react_flask_pdb2pqr/pdb2pqr.py pdb2pqr.py