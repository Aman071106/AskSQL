import sqlite3

'''
    Local sql db for testing streamlit app.
'''

def createdb():
    conn=sqlite3.connect('Student.db')
    conn.close()
createdb()

def create_table():
    conn=sqlite3.connect('Student.db')
    cursor=conn.cursor()
    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS Students(
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            marks INTEGER,
                            class INTEGER
                        )
                    ''')
    conn.commit()
    conn.close()

def insert_element(stu_name,marks,class_):
    conn=sqlite3.connect('Student.db')
    cursor=conn.cursor()
    cursor.execute(
                   '''
                        INSERT INTO Students (name,marks,class)
                        VALUES(?,?,?)                       
                   '''
                   ,(stu_name,marks,class_)
                   )
    conn.commit()
    conn.close()
def show_table():
    conn=sqlite3.connect('Student.db')
    cursor=conn.cursor()
    cursor.execute('''
                        SELECT * FROM Students                       
                   '''
                   )
    records=cursor.fetchall()
    conn.commit()
    conn.close()
    
    for record in records:
        print(record)
create_table()
insert_element('Alice', 30, 5)
insert_element('Aman', 50, 12)
insert_element('Ali', 10, 7)
insert_element('Ace', 30, 5)
insert_element('Alice', 30, 6)
insert_element('Alice', 30, 3)
insert_element('Shyam', 30, 6)
insert_element('Ram', 30, 8)
insert_element('Harsh', 70, 12)
show_table()