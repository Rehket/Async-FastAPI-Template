# FastAPI Template Repo
## Based on the backend in [@tiangolo's](https://github.com/tiangolo) [full-stack-fastapi-postgresql](https://github.com/tiangolo/full-stack-fastapi-postgresql)

### Setup
- Create and activate a virtual environment
- Setup the env.ps1 script with desired variables. 
- In the virtual environment:
    - run the ```env.ps1``` script to set the environment variables. 
    - install the packages included in the ```req-dev.txt```
    - run ```python ./bootstrap.py```
    
    Lastly...
    - run ```uvicorn app.main:app --reload``` to start the application 

### Usage
- Once the application is running, by 
going to ```localhost:8000/docs``` or what you configured in the env.ps1, you will be able to login and tryout the endpoints. 


### Change Log:
#### 1-Aug-2019
Changing this repo from a repo used for demoing an issue to a template for making an API service using postgres and FastAPI.

- Adding an archive with the old readme detailing the error. 
