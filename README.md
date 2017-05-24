# 422-Project2
This is the second group project for CIS 422 Software Methodologies course.
The project authors are:
1. Brian Leeson
2. Jamie Zimmerman
3. Amie Corso

Credit: Flask gcal auth and config code based off of a CIS-322 project whose code base the instructor
(Michal Young) wrote.

### Description:
This is a project for GreenHill Humane Society foster program to assist with daily medication reminders.
The reminder events are stored in google calendar. When using our website the user will give permission
to access their calendar. Our flask server will then parse the relevant medication data from the reminder
calendar and send emails to the appropriate foster families.

### Dependencies:
This project has been set up to run in a virtual environment in order to support installations on
platforms where the user may not have root permissions and to better insulate this project from the
host machine. All current dependencies are listed in requirements.txt. If the project were to be extended,
further instructions have been left in the Makefile on how to add dependencies in the virtual environment.
The critical dependencies that must already exist or be installed with root access are:
git  
python 3.*  
bash shell  

### Instructions:  
Setup:
 * Make sure all critical dependencies are installed.
 * "git clone https://github.com/brianLeeson/422-Project2".
 * Configure and run the project with "make run".
 * Connect to the server locally with or externally at ix.cs.uoregon.edu:PORT_NUM
 * Authenticate by clicking "TODO THING NAME"
 * Select which reminders you would like to have sent.
 * Send reminders. If successful, a list of sent reminders will be shown.
 
 ### Issues:
 This has not been tested with concurrent connections, behavior unknown. As this service is built for one 
 person to connect per day, concurrency is not an immediate concern.

 ### Platforms:
 This flask server is built to run on our schools ix server. 
 It has also tested on:
 Ubuntu 16.04

 ### Details:

 ### Ideas for Project Improvement:
 This project is specifically set up for Greenhill specifically and would need to be changed for other users
 or others uses within Greenhill. For example, reminder appointments would need to look at the appointment calendar. This
 could be made generic if we looked at all calendars for the standard template. This would require that the parsing be
 ensured to be robust.
 
 This server is geared to run on our school server at a specific port number. This is working, but not ideal.
 Working towards running the flask server on a hosting service like heroku would provide security and stability.
 

