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

