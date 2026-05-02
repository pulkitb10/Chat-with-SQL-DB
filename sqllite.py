import sqlite3

## Connect to Sqllite
connection = sqlite3.connect('student.db')

# Create a cursor object to insert record, create table
cursor = connection.cursor()

## Create the table
table_info = """
create table STUDENT(NAME VARCHAR(25),CLASS VARCHAR(25),SECTION VARCHAR(25),MARKS INT)
"""

cursor.execute(table_info)

## Insert some more records
cursor.execute('''INSERT INTO STUDENT VALUES('John','Data Science','A',85)''')
cursor.execute('''INSERT INTO STUDENT VALUES('Pulkit','Data Science','A',95)''')
cursor.execute('''INSERT INTO STUDENT VALUES('Chris','Devops','B',80)''')
cursor.execute('''INSERT INTO STUDENT VALUES('David','Ansible','C',40)''')
cursor.execute('''INSERT INTO STUDENT VALUES('Krish','Data Science','A',90)''')

## Display all the records
print("The inserted records are")
data = cursor.execute('''SELECT * FROM STUDENT''')
for row in data:
    print(row)

## Commit the changes to the database
connection.commit()
connection.close()