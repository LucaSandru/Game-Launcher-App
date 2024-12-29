import pymysql

my_db = pymysql.connect(
    host= "localhost",
    user= "root",
    passwd= "sandruluca2004",
    database= "game_launcher"  # Replace with the actual database name
)

print("Connection successful:", my_db)
