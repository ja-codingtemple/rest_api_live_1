#Flask - gives us all the tools we need to run a flask app by creating an instance of this class
#jsonify - converst data to JSON
#request - allows us to interact with HTTP method requests as objects
from flask import Flask, jsonify, request

#SQLAlchemy = ORM to connect and relate python classes to SQL tables
from flask_sqlalchemy import SQLAlchemy

#DeclarativeBase - gives ust the base model functionallity to create the Classes as Model Classes for our db tables
#Mapped - Maps a Class attribute to a table column or relationship
#mapped_column - sets our Column and allows us to add any constraints we need (unique,nullable, primary_key)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

#Marshmallow - allows us to create a schema to valdite, serialize, and deserialize JSON data
from flask_marshmallow import Marshmallow

#date - use to create date type objects
from datetime import date

#List - is used to creat a relationship that will return a list of Objects
from typing import List

#fields - lets us set a schema field which includes datatype and constraints
from marshmallow import ValidationError, fields

#select - acts as our SELECT FROM query
#delete - acts as our DELET query
from sqlalchemy import select, delete

'''
WHAT IS SQLALCHEMY?
SQLAlchemy is a ORM (Object-Relational Mapping) library for Python. It can be used to interact directly with a database to build tables, work with records, and execute SQL queries.

WHAT IS FLASK?:
Flask is a web framework for building web applications in Python. It can be used to create APIs.

WHAT IS MARSHMALLLOW?:
Marshmallow is a Python library for object serialization and deserialization. It also ensures that data matches schema specifications prior to accepting it.

WHAT IS SERIALIZATION & DESERIALIZATION?
Serialization means converting an object into an easily transferrable format.
Deserialization is when we convert it from that format back into an object.

WHAT IS A SCHEMA?
A schema defines the structure of a database. It specifies what tables will exist in the database, what fields those tables will have, what datatypes each field will have
and what relationships will exist between each table. It also defines constraints, such as NOT NULL, UNIQUE, and FOREIGN KEY.

There are three major components to this application:
- Models
- Schemas
- API Routes

Databases are the highest level structure. They can contain multiple schemas, views, and tables.
Schemas organize related database objects and contain tables.
Tables represent entities (models), which in this case are built from Python classes.

'''

app = Flask(__name__) # Creates an instance of our flask application.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:410Luna@localhost/ecommerce_api_2'

# Each class in our Model is going to inherit from the Base class, which inherits from the SQLAlchemy base model DeclarativeBase
class Base(DeclarativeBase):
    pass # This class can be further configured but for our use case we don't need to configure it any further, so we're passing.

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

#====================== MODELS ==============================================
'''
Each model represents a different table in the database.
Each model attribute represents a column in the table.
'''
class Customer(Base):
    
    __tablename__ = 'Customer' #Make your class name the same as your table name (trust me)

    #mapping class attributes to database table columns
    # name: datatype
    # mapped_column is how we add constraints
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225), nullable=False)
    email: Mapped[str] = mapped_column(db.String(225))
    address: Mapped[str] = mapped_column(db.String(225))
    '''
    This creates a one-to-many relationship to the Orders table.
    This relates one Customer to many Orders.
    
    back_populates ensures that the relationship is read on both ends. It creates a bidirectional relationship.
    It ensures these two tables are in sync with one
    '''
    orders: Mapped[List["Orders"]] = db.relationship(back_populates='customer') #back_populates ensures that both ends of the relationship have access to the other
    
'''
ASSOCIATION TABLE: order_products
Because we have many-to-many relationships, an association table is required.
This table facilitiates the relationship from one order to many products, or many products back to one order.
This only includes foreign keys, so we don't need to create a complicated class model for it.
'''
order_products = db.Table(
    "Order_Products",
    Base.metadata, #Allows this table to locate the foreign keys from the other Base class
    db.Column('order_id', db.ForeignKey('orders.id')),
    db.Column('product_id', db.ForeignKey('products.id'))
)


class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    '''
    A foreign key constraint is a key used to link two tables together.
    A foreign key is a field in one table that refers to the primary key in another table.
    Here, we're specifying that the customer_id in an Order is the primary key for a Customer in the Customer table.
    '''
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('Customer.id'))
    #creating a many-to-one relationship to Customer table
    customer: Mapped['Customer'] = db.relationship(back_populates='orders')
    #creating a many-to-many relationship to Products through or association table order_products
    #we specify that this relationship goes through a secondary table (order_products)
    products: Mapped[List['Products']] = db.relationship(secondary=order_products, back_populates="orders")
    
class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(db.String(255), nullable=False )
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    orders: Mapped[List['Orders']] = db.relationship(secondary=order_products, back_populates="products")
     
# Initialize the database & create tables
with app.app_context():
    # db.drop_all()
    '''
    First we check which tables already exist, and then we creates any tables we can't find.
    This will not update tables that already exist that match these names. So, to modify them, we would have to drop the table & recreate it.
    '''
    db.create_all()
 
#============================ SCHEMAS ==================================
'''
A schema a collection of database objects, such as tables and views.
The schema describes the structure of the data and how the various tables and fields relate to one another.

We use schemas for:
- Validation: When people send us information we have to ensure it's valid & complete information.
- Serialization: Converting our Python objects into JSON.
- Deserialization: Translating JSON objects into a Python usable object or dictionary.

By using a schema we can automatically serialize objects.
'''
# Define Customer Schema
class CustomerSchema(ma.SQLAlchemyAutoSchema): # SQLAlchemyAutoSchemas create schema fields based on the SQLAlchemy model passed in.
    class Meta:
        model = Customer

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        include_fk = True # Need this because Auto Schemas doesn't automatically recognize foreign keys (customer_id)
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# =================== API ROUTES (WITH FLASK) ==============
@app.route('/')
def home():
    return "Home"

#=============== API ROUTES: Customer CRUD==================

# Create a customer with a POST request
@app.route("/customers", methods=["POST"])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], address=customer_data['address'])
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({"Message": "New Customer addess successfully!",
                    "customer": customer_schema.dump(new_customer)}), 201
    
# Get all customers using a GET method
@app.route("/customers", methods=['GET'])
def get_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars() #Execute query, and convert row objects into scalar objects (python useable)
    customers = result.all() #packs objects into a list
    return customers_schema.jsonify(customers)

# Get specific customer using a GET method and dynamic route
@app.route("/customers/<int:id>", methods=['GET'])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalars().first() # first() grabs the first object returned
    
    if result is None:
        return jsonify({"Error": "Customer not found"}), 404
    
    return customer_schema.jsonify(result)


#=============== API ROUTES: Products CRUD==================


@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Products(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"Messages": "New Product added!",
                    "product": product_schema.dump(new_product)}), 201

@app.route("/products", methods=['GET'])
def get_products():
    query = select(Products)
    result = db.session.execute(query).scalars() #Exectute query, and convert row objects into scalar objects (python useable)
    products = result.all() #packs objects into a list
    return products_schema.jsonify(products)
    

#=============== API ROUTES: Order Operations ==================
#CREATE an ORDER
@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Retrieve the customer by its id.
    customer = db.session.get(Customer, order_data['customer_id'])
    
    # Check if the customer exists.
    if customer:
        new_order = Orders(order_date=order_data['order_date'], customer_id = order_data['customer_id'])

        db.session.add(new_order)
        db.session.commit()

        return jsonify({"Message": "New Order Placed!",
                        "order": order_schema.dump(new_order)}), 201
    else:
        return jsonify({"message": "Invalid customer id"}), 400

#ADD ITEM TO ORDER
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product(order_id, product_id):
    order = db.session.get(Orders, order_id) #can use .get when querying using Primary Key
    product = db.session.get(Products, product_id)

    if order and product: #check to see if both exist
        if product not in order.products: #Ensure the product is not already on the order
            order.products.append(product) #create relationship from order to product
            db.session.commit() #commit changes to db
            return jsonify({"Message": "Successfully added item to order."}), 200
        else:#Product is in order.products
            return jsonify({"Message": "Item is already included in this order."}), 400
    else:#order or product does not exist
        return jsonify({"Message": "Invalid order id or product id."}), 400

if __name__ == '__main__':
    app.run(debug=True)