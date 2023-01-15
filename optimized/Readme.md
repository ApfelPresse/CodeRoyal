denv --userns=host python:3.11.0-bullseye

pip3.11 install cython==3.0.0a11 numpy
python setup.py build_ext --inplace
