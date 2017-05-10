To update the survey results:
- Obtain new data files from Olly Betts and add them into the swigsurvey directory (don't add partial month's data)
- Run:
    ./survey-analyze.py 
- Commit these three files which get created:
    SWIGSurveyOperatingSystemsPercent.png
    SWIGSurveyTargetLanguagesNextPercent.png
    SWIGSurveyTargetLanguagesTopPercent.png
- Also add and commit the new files added to the swigsurvey directory.
- Update ../swigsurvey.ht with the date of the last input survey results included (at end of page).
- Update rest of website as usual (see ../Makefile).
