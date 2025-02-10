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
    JOIN 
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
        p.category AS category_name


    """
    return {"message": "Not implemented"}

@app.get("/assignment3")
async def assignment3():
    # Complex JOIN with GROUP BY
    return {"message": "Not implemented"}

@app.get("/assignment4")
async def assignment4():
    # Subquery
    return {"message": "Not implemented"} 