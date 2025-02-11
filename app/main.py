from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector
from mysql.connector import Error
import os

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'user': os.getenv('DB_USER', 'user'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'retail_db')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/initdb")
async def init_db():
    try:
        with get_db_connection() as connection:
            if connection is None:
                return {"error": "Could not connect to database"}
            
            cursor = connection.cursor()
            
            with open('sql/init.sql', 'r') as file:
                init_script = file.read()
            
            # Drop existing tables if they exist
            cursor.execute("DROP TABLE IF EXISTS order_items")
            cursor.execute("DROP TABLE IF EXISTS orders")
            cursor.execute("DROP TABLE IF EXISTS products")
            cursor.execute("DROP TABLE IF EXISTS customers")
            connection.commit()
            
            # Split and execute statements
            statements = [stmt.strip() for stmt in init_script.split(';') if stmt.strip()]
            for statement in statements:
                try:
                    cursor.execute(statement)
                    connection.commit()
                except Error as e:
                    print(f"Error executing statement: {statement[:100]}...")
                    print(f"Error message: {str(e)}")
                    return {"error": f"Error during initialization: {str(e)}"}
            
            # Verify data was inserted
            tables = ['customers', 'products', 'orders', 'order_items']
            counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                counts[table] = count
                if count == 0:
                    return {"error": f"Table {table} is empty after initialization"}
            
            return {
                "message": "Database initialized successfully",
                "table_counts": counts
            }
            
    except Error as e:
        print(f"Database error during initialization: {str(e)}")
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error during initialization: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@app.get("/table/{table_name}")
async def get_table_data(table_name: str):
    valid_tables = {
        'customers': "SELECT * FROM customers LIMIT 50",
        'orders': "SELECT * FROM orders LIMIT 50",
        'products': "SELECT * FROM products LIMIT 50",
        'orderItems': "SELECT * FROM order_items LIMIT 50"
    }
    
    if table_name not in valid_tables:
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    try:
        with get_db_connection() as connection:
            if connection is None:
                return {"error": "Could not connect to database"}
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(valid_tables[table_name])
            results = cursor.fetchall()
            return {"data": results}
            
    except Error as e:
        return {"error": f"Database error: {str(e)}"}

# Template routes for lab
@app.get("/assignment1")
async def assignment1():
    query = """
    SELECT
        c.name AS customer_name,
        c.email AS customer_email,
        SUM(o.total_amount) AS total_spent
    FROM 
        customers c
    LEFT JOIN 
        orders o 
    ON 
        c.customer_id = o.customer_id
    WHERE 
        o.status='Completed'
    GROUP BY
        c.customer_id, c.name, c.email
    ORDER BY 
        total_spent DESC;
    """
    try:
        # Get a database connection
        with get_db_connection() as connection:
            if connection is None:
                raise HTTPException(status_code=500, detail="Could not connect to database")
            
            # Create a cursor
            cursor = connection.cursor(dictionary=True)
            
            # Execute the query
            cursor.execute(query)
            
            # Fetch the results
            results = cursor.fetchall()
            
            # Return the results as JSON
            return {"data": results}
    
    except Error as e:
        # Handle database errors
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/assignment2")
async def assignment2():
    # Implement a query to calculate sales metrics by product category, including:

    # Category name
    # Total number of orders
    # Total revenue
    # Average order value
    query = """
    SELECT
        p.category AS category_name,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
        CASE 
            WHEN COUNT(DISTINCT oi.order_id) = 0 THEN 0
            ELSE ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT oi.order_id), 2)
        END AS average_order_value
    FROM 
        products p
    LEFT JOIN 
        order_items oi
    ON 
        p.product_id = oi.product_id
    GROUP BY
        p.category
    ORDER BY
        total_revenue DESC;
    """
    try:
        connection = get_db_connection()
        if connection is None:
            raise HTTPException(status_code=500, detail="can not get to database")
            #curser creation for
        cursor = connection.cursor(dictionary=True)
            #Exectue query
        cursor.execute(query)
        # geting the results
        results = cursor.fetchall()
        #stopping connection
        cursor.close()
        connection.close()
        return{"data": results}
    
    except Error as e:
        raise HTTPException(status_code =500, detail = f"{str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")
    

@app.get("/assignment3")
async def assignment3():
    #Implement a query to analyze customer purchasing patterns by membership level and city, showing:
        #Membership level
        #City
        #Total orders
        #Average order value
        #Number of customers
        #Orders per customer
    query = """
    SELECT
        c.membership_level,
        c.city,
        COUNT(o.order_id) AS total_orders,
        ROUND(SUM(o.total_amount) / NULLIF(COUNT(o.order_id), 0), 2) AS average_order_value,
        COUNT(DISTINCT c.customer_id) AS number_of_customers,
        CASE 
            WHEN COUNT(DISTINCT c.customer_id) = 0 THEN 0
            ELSE COUNT(o.order_id) / COUNT(DISTINCT c.customer_id)
        END AS orders_per_customer
    FROM 
        customers c
    LEFT JOIN
        orders o
    ON 
        c.customer_id = o.customer_id
    GROUP BY
        c.membership_level, c.city
    ORDER BY
        c.membership_level, c.city;
    """
    try:
        connection = get_db_connection()
        if connection is None:
            raise HTTPException(status_code=500, detail="can not get database")
        #creating the curser
        cursor = connection.cursor(dictionary=True)
        #getting to the query
        cursor.execute(query)
        #getting all
        results = cursor.fetchall()
        #closing everything
        cursor.close()
        connection.close()
        return{"details": results}
    except Error as e:
        raise HTTPException(status_code=500,detail=f"{str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}") 


@app.get("/assignment4")
async def assignment4():
    # SImplement a query to find products that are performing above average in their category, showing:

        #Product name
        #Category
        #Total sales
        #Category average
        #Percentage above average
    query = """
    WITH CategoryAverages AS (
        SELECT 
            p.category,
            AVG(SUM(oi.quantity * oi.unit_price)) OVER (PARTITION BY p.category) AS category_average
        FROM 
            products p
        JOIN 
            order_items oi
        ON 
            p.product_id = oi.product_id
        GROUP BY 
            p.product_id, p.category
    ),
    ProductSales AS (
        SELECT 
            p.name AS product_name,
            p.category,
            SUM(oi.quantity * oi.unit_price) AS total_sales
        FROM 
            products p
        JOIN 
            order_items oi
        ON 
            p.product_id = oi.product_id
        GROUP BY 
            p.product_id, p.name, p.category
    )
    SELECT 
        ps.product_name,
        ps.category,
        ps.total_sales,
        ca.category_average,
        ROUND(((ps.total_sales - ca.category_average) / ca.category_average) * 100, 2) AS percentage_above_average
    FROM 
        ProductSales ps
    JOIN 
        CategoryAverages ca
    ON 
        ps.category = ca.category
    WHERE 
        ps.total_sales > ca.category_average;
    """
    
    try:
        # Get a database connection
        connection = get_db_connection()
        if connection is None:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        
        # Create a cursor
        cursor = connection.cursor(dictionary=True)
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Close the connection
        cursor.close()
        connection.close()
        
        # Return the results as JSON
        return {"data": results}
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")