# PEarlD

PEarlD is the face of our project - Multimodal Early Detection of Parkinson's Disease. It is a platform for anyone suspected to be in the early stages of Parkinson's, which analyses multiple symptoms to confirm its presence or absence.  

### What is the need for this project?  
There is no specific test to diagnose Parkinson's disease. Instead, neurologists diagnose the condition based on a person's medical history, a review of signs and symptoms, and a neurological and physical examination. Although some SPECT scans can help support the suspicion that a person has Parkinson's disease, their symptoms and neurologic examination ultimately determine the correct diagnosis, which is what this project aims to do - analyse as many symptoms as possible.

### How do we do it?  
We collected extensive data containing several tests and questionnaires answered by X people (including both patients and healthy controls) from the Parkinson's Progression Markers Initiative (PPMI). PPMI is a landmark study collaborating with partners worldwide to create a robust open-access dataset and biosample library. Each of these tests and questionnaires corresponds to different symptoms of the disease. We also collected a few voice samples from i.Prognosis to analyse any variations in the voice. The datasets collected went through a rigourous process of data compilation and cleaning, followed by exploratory data analysis to prepare the data for machine learning. We experimented with several machine learning algorithms to build the best models that could learn our data well and predict the outcome for any new input. Finally, we present the outcome in terms of the probability of being in the early stages of the disease.

## Files and folders  
- pickles - Contains the pickle files (serialized) corresponding to the trained ML models to make a prediction when the user submits their input. 
- templates - Contains all the vanilla HTML files.
- static - Contains assets used by the templates, including CSS files, JavaScript files, and images.
- Procfile - Specifies the commands executed by the app on startup, needed by Heroku.
- app.py - Python script containing all the endpoints.
- database.db - The application is associated with an SQL database that contains two tables - User and Test.   
- requirements.txt - A pip requirements file that specifies Python package dependencies on Heroku. 
  
The user interface is developed using the Flask framework. It consists of an application manager that lets users create an account, log in, and log out. There are 16 endpoints that determine the URL to each webpage. The user, once logged in, can proceed to answer a questionnaire or take a preliminary voice analysis test. The user can view the results of their previously taken tests in ‘My Tests.’ This repository is also deployed and active on a Heroku production environment for global access over the internet.   

  
### To run the app  
- To run locally on your machine, 
  -  install and set up the Flask 1.1.2 environment on your computer
  -  run app.py on the terminal
  -  this launches a builtin Flask server at http://127.0.0.1:5000/
- Or head over to https://pearld.herokuapp.com/ to view the deployed web app.  


## Collaborators:
- Sakshi Shetty [PES1201800190]
- Snigdha S Chenjeri [PES1201800045]
- Sruthy S [PES1201801143]
- Swanuja Maslekar [PES1201800369]  
