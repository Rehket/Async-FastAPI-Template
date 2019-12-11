# 11-December-2019

## Updated Bootstrap Script!
Updated the script up do docker database setup, apply migrations, and initialize a user.
- Functions for remote automated setup still need to be done. 
- Functions for pulling and loading initial data need to be done on an individual basis. 

## Switching to all async!
Updating all database operations to use async/await syntax with the [databases package](https://github.com/encode/databases)!

## TODO:
- Do some cleanup...
    - Look at alembic env.py file
    - See if there is a better wat of convert the asyncpg responses to pydantic models. 