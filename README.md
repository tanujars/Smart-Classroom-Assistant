# Summary:
Cloud-based application to be designed to serve as an intelligent classroom assistant for educators. It should be capable of analyzing videos captured in the user's classroom, conducting facial recognition on the individuals in the videos, retrieving information about the identified students from a database, and providing the user with pertinent academic details for each student.

* load_data.py - Contains a Python script that manages the upload of student data to DynamoDB and the encoding file to the input bucket.
* handler.py - Includes a Python script that runs the entire application.
* workload.py - Contains a Python script created to put videos into the input bucket.
