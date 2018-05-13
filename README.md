# item-catalog
---
### Udacity Full Stack Web Developer Nanodegree Backend Project
---
This app will let users to signup, login and make CRUD operations on an item list based on categories. 

## Getting Started

This project requires:

- Python
- SqlAlchemy

## Installing

First clone the code into your computer.

`git clone https://github.com/rehas/item-catalog.git`

Then cd into the folder and run in order to create the database engine:

`python models.py`

After that in order to create first several users and the dummy categories/ items execute

`python catalog-population.py`

Now the dummy objects should be ready, so run the server by:

`python server.py`

Now visit `localhost:8000`

To make changes, a user needs to be logged in.

---
## Notes

- A user can only change / delete the items created by the user
- Initial caregories can not be changed but new categories can be added
- JSON API endpoints are available for
    - categories : `/catalog/JSON`
    - items : `/catalog/<category_name>/JSON`
---
## Author

- **Berat Reha Sonmez**

