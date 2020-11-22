# CSE472Project2
Detecting Twitter bots using a logistical regression. 

# Execution Instructions
Type the following commands in the terminal to run the code

python dataManipulation.py This creates the model using the provided feature vectors.

python dataManipulation.py -f 1 This runs all steps of the process from data collection to model creation.

python dataManipulation.py -h To see all command options.

# Deliverables 
dataManipulation.py: Performs timeline collection from the dataset, convert them into graphs, convert the graphs into feature vectors, and then train the model and predict its accuracy.

Information: This folder contains the following:

  - graphFeatures.csv: The final form of the information of our dataset. This is the information that the model will train off of.
  
  - userDataset.csv: The merged collection of datasets from Botometer.
  
  - (The following are created after the first execution):
  
    - botGraphs: An empty folder that will contain the timeline graphs of bot accounts.

    - botTimeline: An empty folder that will contain the timeline JSONs of bot accounts.

    - humanGraphs: An empty folder that will contain the timeline graphs of human accounts.

    - humanTimeline: An empty folder that will contain the timeline JSONs of human accounts.
