# Mesh predictor

Tensorflow and optuna-based utility to learn to predict several quantities (position, deviation, thickness) based on a set of process parameters of FEM experiments.

![](docs/sliders.png)

The documentation is at <https://hamkerlab.github.io/ML-Karoprod-MeshPredictor/>. 

## Installation

Dependencies:

* numpy 
* pandas
* matplotlib
* ipywidgets
* tensorflow >=2.6
* optuna
* h5py

```bash
pip install git+https://github.com/hamkerlab/ML-Karoprod-MeshPredictor.git@master
```

## Documentation


To generate the documentation, you will need:

```bash
pip install mkdocs mkdocs-material mkdocstrings pymdown-extensions mknotebooks
```

To see the documentation locally:

```bash
mkdocs serve
```

To push to github:

```bash
mkdocs gh-deploy
```