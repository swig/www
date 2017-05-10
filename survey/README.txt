To update the survey results:
- Obtain new data files from Olly Betts and add them into the swigsurvey directory (don't add partial month's data)
- Run (you may first need to install Python3 and some missing Python3 packages, see later):
    ./survey-analyze.py 
- Commit these three files which get created:
    SWIGSurveyOperatingSystemsPercent.png
    SWIGSurveyTargetLanguagesNextPercent.png
    SWIGSurveyTargetLanguagesTopPercent.png
- Also add and commit the new files added to the swigsurvey directory.
- Update ../swigsurvey.ht with the date of the last input survey results included (at end of page).
- Update rest of website as usual (see ../Makefile).


Packages
========
Some Python3 packages are needed. I think this is all that is needed (I didn't have much luck with pip3):
sudo apt-get install python3-pandas
