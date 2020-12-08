 
Installation
============
If you don't need the latest version you, can simply use:

    pip install opentree


If you are developer who wants to install multiple times, you probably want to clone the code locally,
and install it in a virtual environment.

To do so, run:

    git clone https://github.com/OpenTreeOfLife/python-opentree.git #Copies to code to your machine
    cd python-opentree
    python3 -m venv env #Creates a virtual environment named env (you only need to ever run this once)
    source env/bin/activate # activates the virtual environment (you will wnat to do this each time you are using the package)
    pip install -r requirements.txt # Installs the requiremnets
    pip install -e . # Installs the open tree package

You can deactivate the virtual environment by running

    deactivate
    

If you plan to run the example jupyter notebooks, install jupyter within the virtual environment as well using:

Create and activate the virtual environment as shown above

    source env/bin/activate
    pip install ipykernel  
	python -m ipykernel install --user --name=opentree  
	pip install jupyter  
	jupyter notebook docs/notebooks/ # This will open the example notebooks

