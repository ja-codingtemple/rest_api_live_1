# Starter Code: Relational Databases & REST APIs (Building an E-commerce API with Flask, SQLAlchemy, Marshmallow, and MySQL)

To use this repository:
1. Clone the repository.
2. Open the project folder.
3. Open terminal.
4. Create a Python virtual environment with ``python3 -m venv venv``
5. Activate the virtual environment ``venv\Scripts\activate``
6. Install the dependencies with ``pip install Flask Flask-SQLAlchemy Flask-Marshmallow marshmallow-sqlalchemy mysql-connector-python``
7. Make sure you've created the desired database in MySQLWorkBench with the ``CREATE DATABASE mydatabasenamehere`` command.
8. Make sure you update your password in your database connection string and your database name in your connection string. This is line 60 in the ``main.py`` application.
<br><br>Currently it is set to ``mysql+mysqlconnector://root:410Luna@localhost/ecommerce_api_2`` where ``410Luna`` is an example password and ``e_commerce_api_2`` is my chosen database name. You will need to change these values to the ones you've chosen for your database.
9. Save your changes and then run the application in terminal by activating your venv and typing ``python main.py``
10. Once you've got your Python application running, open Postman and you can use Postman to send HTTP requests to your API endpoints to test that they are working.

Make sure you add all the other required endpoints specified in your project instructions. If you're at any point confused about how to do this, please check out Lesson 5 in the Relational Databases & REST API module in Disco.
