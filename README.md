# vtech_learningfactory_consolidated_database_dashboard

# Repository Overview
There are two folders in this repository.

## DatabaseGenerator
Contains the files for the database generator tool. This tool allows a user to input links to MTConnect data. It will parse the data, allow a user to choose devices, subcomponents, and the data elements they want to store in a database. There is a UML diagram, sample database schema, and demo video included as well. 

To run the database generator, first you must install the required python packages. In the command line/terminal of your development environment, run the command: pip install -r "requirements.txt". Then, run from main.py to launch the GUI. Note that a database file called "example.db" will be created if you choose to save data to a database. To change the file path or name, edit the chooseEvents.py file. 

## DashboardLearningFactory
Contains the sample XML files we had for the machines in the Learning Factory, and three files that process and simulate data (if necessary). The PowerBI dashboard file  and screenshot images of the dashboard are included as well.
