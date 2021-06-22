Installation
============

## Installing the package from the PyPI repository

`python-opentree` is available from the [Python Package Index (PyPI)](https://pypi.org/)
If you don't need the latest version you can simply use:

    pip install opentree

## Installing a local copy of the package

If you want the latest version of `python-opentree` or if you are developer who wants to install multiple times, you probably want to clone the code from its [GitHub repository](https://github.com/OpenTreeOfLife/python-opentree) locally, and install it in a virtual environment.

To do so, first clone the code to your machine:

    git clone https://github.com/OpenTreeOfLife/python-opentree.git

Change to its directory:

    cd python-opentree

Create a virtual environment named `env` (you only need to ever run this once):

    python3 -m venv env

Activate the virtual environment (you will want to do this each time you are using the package)

    source env/bin/activate

Install the package requirements:

    pip install -r requirements.txt

Install the `python-opentree` package locally:

    pip install -e .


You can deactivate the virtual environment by running:

    deactivate

## Install to run the example Jupyter notebooks

If you plan to run the example Jupyter notebooks, install [Jupyter](https://jupyter.org/) within the virtual environment as well.

Create (if you haven't yet) and activate the virtual environment as shown above:

    source env/bin/activate

Install the kernel:
    pip install ipykernel
	  python -m ipykernel install --user --name=opentree

Install `jupyter`:

	  pip install jupyter

Open the example notebooks:

	  jupyter notebook docs/notebooks/
