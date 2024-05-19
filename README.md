# Exam grader   
Working on a grader for any exam that requires a tar or zip compressed file containing x number of files as a deliverable. For the implementation, I combine the two design patterns AbstractFactory and Strategy. AbstractFactory to provide us with the different grader classes for different exams. Strategy to make an abstract call to the various correction methods of the classes. I started with a grader for the Bash and Linux exam and am currently working on developing graders for the others, including MongoDB and FastAPI exams.
## What does the script do ?

1. extract all the exam files of the candidates to a specific destination
2. iterate over each exam folder
3. verify the existence of the files: 'cron.txt', 'sales.txt' and 'exam.sh'
4. examine the content of each of those files and check if it's correct
   - the "cron.txt" file is examined by checking the validity of the cron configuration using the package 
   croniter
   - the "out.txt" file is examined by performing a regex matching verifying if the content is a sequence
     of this structure taking into consideration that the GPU order could change):
      ```bash
        datetime
          rtx3060: number
          rtx3070: number
          rtx3080: number
          rtx3090: number
          rx6700: number
      ```
5. run the GPU API in background and execute the 'exam.sh' script
   keeping its output in a second output file 'sales_2.txt' whose content will be
   compared to the content of 'sales.txt'
6. show the result of the exams of all candidates in a table
7. clean the project by deleting extracted files and folders

## TODO

1. write more unit tests involving many versions of correct and incorrect exams to 
   assure the correctness of the script increasing the coverage score 


## Usage
### Bash Linux
![Bash](logos/bash.png)


1. Run the script:

    ```bash
    make correction EXAM_TYPE=bash  EXAM_FOLDER=bash_linux_exams
    ```
2. Example of output:
    ```bash
    +------------------+----------+--------------------------------------------------------------------+
   | candidate_name   | result   | remarques supplémentaires                                          |
   +==================+==========+====================================================================+
   | braun            | Failed   | - cron file is not correct- sales file is not correct              |
   +------------------+----------+--------------------------------------------------------------------+
   | JACOB            | Failed   | - cron file is not correct- sales file is not correct              |
   +------------------+----------+--------------------------------------------------------------------+
   | docker           | Failed   | - cron file not found- sales file not found- script file not found |
   +------------------+----------+--------------------------------------------------------------------+
   | CLAUDE           | Failed   | - sales file is not correct                                        |
   +------------------+----------+--------------------------------------------------------------------+
   | ferreira         | Failed   | - cron file is not correct- sales file is not correct              |
   +------------------+----------+--------------------------------------------------------------------+
   | CLACO (1)        | Failed   | - cron file is not correct- sales file is not correct              |
   +------------------+----------+--------------------------------------------------------------------+
   | Rim              | Failed   | - cron file is not correct                                         |
   +------------------+----------+--------------------------------------------------------------------+
   | SALL             | Failed   | - cron file is not correct- sales file is not correct              |
   +------------------+----------+--------------------------------------------------------------------+
   | FONTAINE         | Failed   | - cron file is not correct                                         |
   +------------------+----------+--------------------------------------------------------------------+
    ```
### MongoDB
<img src="logos/mongodb.svg" alt="Bash" width="250" height="150">

1. Run the script:

    ```bash
    make correction EXAM_TYPE=mongodb  EXAM_FOLDER=mongodb_exams
    ```
   

### FastAPI
<img src="logos/fastapi.png" alt="Bash" width="250" height="100">

1. Run the script:

    ```bash
    make correction  EXAM_TYPE=fastapi  EXAM_FOLDER=fastapi_exams
    ```
   
### Docker
<img src="logos/docker.png" alt="Bash" height="150">

1. Run the script:

    ```bash
    make correction EXAM_TYPE=docker  EXAM_FOLDER=docker_exams
    ```

### GUI

![Alt Text](gui_usage.gif)


