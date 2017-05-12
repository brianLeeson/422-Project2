# 422-Project2
This is the second group project for CIS 422 Software Methodologies course.
The project authors are:
1. Brian Leeson
2. Jamie Zimmerman
3. Amie Corso
Credit: Flask gcal auth and config code based of a 322 project whose code base the instructor 
(Michal Young) wrote

### Description:
This is a project for GreenHill humane society foster program to assist with daily medication reminders.  
The reminder events are stored in google calendar. When using our website the user will give permission  
to access their calendar. Our flask server will then parse the relevant medication data from the reminder   
calendar and send emails to the appropriate foster families.

### Dependencies:
This project has been set up to run in a virtual environment in order to support installations on 
platforms where the user may not have root permissions and to better insulate this project from the
host machine. All current dependencies are listed in requirements.txt. If the project were to be extended,  
further instructions have been left in the Makefile on how to add dependencies in the virtual environment.  
git  
python 3.*  
bash shell  

### Instructions:  
Setup:
 * make sure all dependencies are installed.
 * "git clone https://github.com/brianLeeson/422-Project1".
 * survey available at: https://tinyurl.com/422formsurvey. modifications are not supported.
 * remove previous survey results before sending out new surveys.
 * send the survey to students by clicking the "Send" button at the top.
 * after all responses are gathered, export the google form to csv if needed.
 
To run the application:
 * run the application with "make run".
 * import the survey results csv
 * sort students into teams
 * optionally export sorted teams to csv for review.
 
 ### Issues:
 This application does not have a command line interface and by consequence cannot be run 
 by ssh-ing into a system, including ix
 
 ### Platforms:
This application has successfully been run on the following platforms:
 * macOS 10.12 ~ Python 3.5
 * Ubuntu 16.0 ~ Python 3.5 
 * this program successfully runs when logged in to Desktop machines in Deschutes 100 - the OS must have a Desktop to run!
### Details:
The soring algorithm accommodates class sizes up to 90 students and team sizes on the range [2, 7].
The resulting "Quality Score" for a given team reflects the aggregate of 3 criteria: shared 
programming language expertise, overlapping schedule availability, and the satisfaction of teammate 
requests. A team is considered "viable" if they share at least 4 weekly hours of available meeting 
time, and have a mutual proficiency of at least 3 (on a scale from 1 to 5) in at least one programming 
language. The algorithm prioritizes the creation of viable teams, while favoring higher quality scores.
It is not guaranteed that all produced teams will be viable, or that a given class input can necessarily 
be sorted into viable teams.  In the case that the class size is not a multiple of the team size, the 
remaining students are assigned to existing teams (creating teams that are oversize by 1).  If there 
are not enough teams to accommodate all remaining students, these students are instead grouped into 
an under-sized team.  The sorting process may take several seconds to complete.

### Ideas for Project Improvement:
- Increased user input, such as the ability to specify the relative importance of the sorting criteria.
- Other types of user input, such as fixing certain student arrangements and allowing the sorting 
process to act on the rest.
- Improved GUI that displays more information about resulting teams (such as which are viable and which 
are not).
- Information displayed when there are students who may not actually be a viable member of ANY team 
(such as a student that has no availability or no language expertise).
- A GUI that supports manually-overridden team creation, such as drag-and-drop.
- Support for sorting on different types of criteria, allowing the program to be useful for other types 
of classes or groups.

