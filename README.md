# UbiChallenge

**What does the API do?**
- Create occurrences (with geographic location and author associated with the occurrence). The default state of a new occurrence is **Waiting Validation**.
- Update occurrences (in order to change the occurrence's state to **Validated** or **Solved** by a System Admin).
- Filtering by Author, Category and Location (within a certain radius of this location).

**Authentication**
This API uses JWT authentication, and some of the endpoints requires a valid JWT access token.

**Error Codes**

**400**: When there is a bad request

**401**: When there is an unsuccessful authentication

**404**: When the requested data is not found

**500**: When something else unexpected occurs

Full documentation at:
https://documenter.getpostman.com/view/1583585/S1EUuwAb

**Deploy instructions:**

```bash
git clone https://github.com/AndreMPCosta/UbiChallenge.git
cd UbiChallenge
```

The dependencies of this project are managed by pipenv, so to get this up and running fast just do:
```bash
pipenv install --dev
```

Note: If you do not have pipenv, install it using: 
```bash
pip install pipenv
```

Check .env.example and configure to your needs (you can use your OS environment variables instead of the .env file)
In this project it is used POSTGRESQL plus PostGIS plugin, because of the locations part. Fill out the .env file with the regular information regarding Database (user, password, database, host, port) and you can change the JWT Key in this file too.
When you are done, rename to .env


To activate this project's virtualenv, run: 
```bash
pipenv shell
```

To run the app, simply do:

```bash
python app.py
```


