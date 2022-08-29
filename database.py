import sqlite3
from os.path import exists
from os import listdir

DATABASE_NAME = 'data.sqlite3'

def connect(db=DATABASE_NAME):
	'''established a connection to the given database, creates a database using create() if it didn't already exist'''
	connection = None
	reset = not exists(db)
	try:
		connection = sqlite3.connect(db)
		if reset:
			create(connection)
	except sqlite3.Error as e:
		print(f"Connection Error:\n{e}")
	return connection

def execute(connection, query):
	cursor = connection.cursor()
	try:
		cursor.execute(query)
		connection.commit()
	except sqlite3.Error as e:
		print(f"Execute Error:\n{e}\n{query}")

def read(connection, query):
	cursor = connection.cursor()
	result = None
	try:
		cursor.execute(query)
		result = cursor.fetchall()
		return result
	except sqlite3.Error as e:
		print(f"Read Error:\n{e}\n{query}")

def create(connection):
	'''creates the database for the auto-grader schema'''
	create_students_table='''
	CREATE TABLE IF NOT EXISTS students (
		github TEXT PRIMARY KEY,
		first_weber TEXT NOT NULL,
		first_nuames TEXT,
		last TEXT NOT NULL,
		weber TEXT NOT NULL,
		period INTEGER NOT NULL
	);'''
	execute(connection, create_students_table)
	create_assignments_table='''
	CREATE TABLE IF NOT EXISTS assignments (
		tag TEXT PRIMARY KEY,
		total INTEGER NOT NULL
		);'''
	execute(connection, create_assignments_table)
	create_scores_table='''
	CREATE TABLE IF NOT EXISTS scores (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		github TEXT NOT NULL,
		tag TEXT NOT NULL,
		earned INTEGER,
		FOREIGN KEY (github) REFERENCES students (github)
		FOREIGN KEY (tag) REFERENCES assignments (tag)
	);'''
	execute(connection, create_scores_table)
	create_assignments(connection)

def create_assignments(connection):
	testing = listdir("Testing")
	for file in testing:
		tag = file[:3]
		try:
			int(tag[0])
			points = 10
		except ValueError:
			points = 20
		enter_assignment=f'''
		INSERT INTO assignments (tag, total)
		VALUES ('{tag}', {points});'''
		execute(connection, enter_assignment)

def remove_student(github):
	c = connect()
	delete_scores =	f"DELETE FROM scores WHERE github = '{github}';"
	execute(c,delete_scores)
	delete_student = f"DELETE FROM students WHERE github = '{github}';"
	execute(c,delete_student)

def change_grade(github, tag, score):
	c = connect()
	id = read(c, f"SELECT id FROM scores WHERE github = '{github}' and tag = '{tag}';")
	if id:
		id = id[0][0]
		query = f"UPDATE scores SET earned = {score} WHERE id = {id};"
	else:
		query = f"INSERT INTO scores (github, tag, earned) VALUES ('{github}','{tag}',{score});"
	execute(c, query)

if __name__ == "__main__":
	c = connect("data.sqlite3")
	#execute(c,"INSERT INTO students(github, first_weber, last, weber, period) VALUES ('ssmith2','Sue','Smith','ssmith',2);")
	change_grade("ssmith2", "00p",10)
	change_grade("ssmith2", "st-",20)
	change_grade("ssmith2", "P03",10)
	#print(read(c,"SELECT * FROM scores INNER JOIN students ON scores.github = students.github WHERE period = 2;"))
	#r = read(c, "SELECT scores.tag, score, assignments.points FROM scores INNER JOIN assignments ON scores.tag = assignments.tag WHERE scores.github = 'bsmith2';")
	#print(r)
	#change_grade('bsmith2','00p',10)
	#change_grade('bsmith2','11p',22)
	#remove_student('bsmith2')
	