Installation
============

## From the PyPI repository

If you don't need the development version of the `python-opentree` package you can install the version available from the [Python Package Index (PyPI)](https://pypi.org/) with:

    pip install opentree

## From the GitHub repository

If you want/need the latest version of `python-opentree` or if you are a developer who wants to install multiple times, you probably want to clone the code from its [GitHub repository](https://github.com/OpenTreeOfLife/python-opentree), and install it locally in a virtual environment.

To do so, first clone the code from GitHub to your machine:

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

If you plan to run the example Jupyter notebooks, you will need to install [Jupyter](https://jupyter.org/) within the virtual environment as well.

Make sure to first create the virtual environment and activate it as shown above.

Now you can install a kernel:

    pip install ipykernel
	  python -m ipykernel install --user --name=opentree

Install `jupyter` from PyPI:

	  pip install jupyter

Open the example notebooks with:

	  jupyter notebook docs/notebooks/
