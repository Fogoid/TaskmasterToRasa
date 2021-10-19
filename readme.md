The files presented in this repository are in the context of the Master Thesis *Making Chatbots for Customer Support: Fast and Serious*. In this files, we present the process we used to create try to create a Rasa model for the restaurant domain using Taskmaster-1 dataset, as well as verifying if we can improve the information in this dataset using the restaurant model creating using the MultiWOZ dataset. If you want details on the implementation check **Chapter 5**.

To use the script in this repository, do the following steps:
1. Clone this repository to a new folder.
2. Go to https://github.com/google-research-datasets/Taskmaster, clone the folder `TM-1-2019` and put inside a folder called `resources`.
3. Create a folder called `Model` and create a base model using `rasa init`.
5. Run the restaurant model (You can recreate the model we defined using the MultiWOZ dataset by following the steps in https://github.com/Fogoid/MultiwozToRasa).
6. Run `main.py`.
