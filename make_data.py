import shelve, csv, os, datetime, json
from sys import exit

class Student():
	def __init__(self, name = "Student, Sample", period = 0, github = 'username'):
		self.name = name
		self.period = period
		self.github = github
		self.assignments = {}
		self.add_assignments()

	def __str__(self):
		rep = f"{self.name}: {self.github}\n"
		rep += f"{self.period}\n"
		return rep

	def add_assignments(self):
		with shelve.open('data.dat') as d:
			tags = d['assignments']
		for t in tags:
			self.assignments[t]=Assignment(t)

	def clone(self, tag):
		return f"nuames-cs/{tag}-{self.github}"

	def print_assignments(self):
		rep = f"\tAssignments\n"
		rep += "|Tag|Score|\t|Tag|Score|\t|Tag|Score|\t|Tag|Score|\n"
		rep +="___________\t___________\t___________\t___________\n"
		keys = list(self.assignments.keys())
		for i in range(0,len(self.assignments),4):
			for j in range(4):
				try:
					a = self.assignments[keys[i+j]]
					rep += f"|{a.tag}|{a.score:>5}|\t"
				except IndexError:
					pass
			rep+='\n'
		return rep

class Assignment():
	def __init__(self, tag):
		self.tag = tag
		self.score = 0.0

	def __str__(self):
		rep = f"Assignment {self.tag}\n"
		rep += f"Score: {self.score}/10\n"
		return rep

def get_date():
	ok = False
	while not ok:
		year = validate_num("Year:(####)")
		month = validate_num("Month:(##)")
		day = validate_num("Day:(##)")
		try:
			d = datetime.datetime(year, month, day)
			ok = True
		except ValueError as e:
			print(e)
	return d

def clean():
	print("Gathering Repos...")
	os.system("gh repo list nuames-cs --json name -L 4444 > temp.json")
	old = []
	d = shelve.open('data.dat')
	tags = d['assignments']
	d.close()
	with open("temp.json") as file:
		repos = json.load(file)
	os.system("rm temp.json")
	print("Filtering Results...")
	for r in repos:
		if r["name"][:3] in tags and r["name"][-3:] != '.py':
			old.append(r['name'])
			print(f"{r['name']} added")
	total = len(old)
	print(f"{total} repos collected")
	if input("Delete?\n").lower() in ('yes','y'):
		c = 0
		print("checking authentication")
		os.system("gh auth refresh -h github.com -s delete_repo")
		for i in old:
			print(f"deleting nuames-cs/{i} ({c}/{total})")
			os.system(f"gh repo delete nuames-cs/{i} --confirm")
	print("Done.")

def reset_data():
	assignments = ["st-"]
	for i in range(26):
		assignments.append(f"{i:02}p")
	for i in range(1,12):
		assignments.append(f"P{i:02}")
	with shelve.open('data.dat','n') as d:
		d['assignments'] = assignments
		d['students'] = []
	print("Data has been reset")

def validate_num(question):
	number = None
	while not number:
		try:
			number = int(input(f"{question}\n"))
		except ValueError:
			print("That wasn't a number")
	return number

def ask_yn(question):
	r = ''
	while r not in ('y','n'):
		r = input(f"{question} (Y/n)\n").lower()
	return r

def change_float(q1, thing):
	complete = 'n'
	while complete == 'n':
		new = input(f"{q1}\n")
		try:
			new = float(new)
			complete = ask_yn(f"Change \"{thing}\" to \"{new}\"?")
		except ValueError:
			print("That wasn't a number")
	return new

def change(q1, thing, num = False):
	complete = 'n'
	while complete == 'n':
		if num:
			new = validate_num(q1)
		else:
			new = input(f"{q1}\n")
		complete = ask_yn(f"Change \"{thing}\" to \"{new}\"?")
	return new

def validate_assign():
	assign = []
	with shelve.open('data.dat') as d:
		assign += d['assignments']
		assign.append('done')
	a = ''
	print(assign)
	while a not in assign:
		a = input("Enter an assignment tag:\n").lower()
	return a

def set_students():
	students = []
	if os.path.exists('students.txt'):
		print("Loading students...")
		with open('students.txt','r') as f:
			for line in f:
				if "last,first_weber,first_nuames,period,weber,github" in line:
					continue
				last,legal,nuames,period,weber,github = line.split(',')
				name = f"{last}, {legal} ({nuames})"
				students.append(Student(name,period,github.strip()))
		with shelve.open('data.dat') as d:
			new = []
			for stu in students:
				found = False
				for s in d['students']:
					if s.github == stu.github:
						found = True
						break
				if not found:
					new.append(stu)
			d['students'] += new
			print(f"{len(new)} new students loaded")
		#os.system("rm students.txt")
	else:
		print("Couldn't find \"students.txt\" file. Did you import it from NUAMES-CS/RSA-Encryption?")

def display_student():
	stu = select_student()
	if stu:
		print(f"{stu.name} Assignments - P{stu.period}")
		print(stu.print_assignments())

def select_student(text=None):
	if not text:
		search = input("Enter a part of a student name or '0' to exit:\n")
	else:
		search = text
	if search == '0':
		return None
	d = shelve.open('data.dat')
	students = d['students']
	d.close()
	while search != '0':
		results = []
		for i in students:
			if search.lower() in i.name.lower():
				results.append(i)
		if len(results)>1:
			print("0 - Quit")
			for i in range(len(results)):
				print(f"{i+1} - {results[i].name}")
			n = validate_num("Which student?")-1
			if n >= 0:
				return results[n]
			else:
				return None
		elif len(results)==1:
			return results[0]
		else:
			if search != '0':
				print(f"No students matched \"{search}\"")
				search = input("Enter a part of a student name or '0' to exit:\n")

def drop():
	d = shelve.open('data.dat')
	students = d['students']
	d.close()
	stu = select_student()
	if not stu:
		return
	print(f"Dropping {stu.name.upper()}, {stu.period}")
	if ask_yn("Are you sure? This CANNOT be undone.") == 'y':
		for i in range(len(students)):
			if students[i].name == stu.name:
				students.pop(i)
				break
		d = shelve.open('data.dat')
		d['students'] = students
		d.close()
		print(f"{stu.name} dropped")
	else:
		print("Drop Aborted")

def run_python(simple):
	try:
		os.system(f"python3 Tests.py {'simple' if simple else ''}")
		with open('score.txt','r') as f:
			score = float(f.read())
		os.system("rm score.txt")
	except KeyboardInterrupt:
		print("Student test terminated")
		score = 0
	except ValueError as e:
		print("non-numeric data in score.txt")
		score = 0
	except FileNotFoundError:
		print("couldn't find score.txt file")
		score = 0
	return score

def grade(stu, tag, simple = True):
	os.system(f"gh repo clone {stu.clone(tag)} student -- -q")
	if os.path.isdir('student'):
		print("Testing...")
		os.chdir('student')
		os.system(f"cp ../Testing/{tag}tests.py Tests.py")
		stu.assignments[tag].score = run_python(simple)
		extract_algorithm(stu, tag)
		os.chdir('..')
		os.system('rm -rf student')
	else:
		print(f"{stu.name} hasn't started the assignment")

def extract_algorithm(stu, tag):
	if tag[0] == 'P':
		name = f'../Algorithms-{tag}'
		if not os.path.isdir(name):
			os.system(f'mkdir {name}')
		with open('student.py','r') as f:
			text = f.readlines()
		algo = []
		for line in text:
			if line.strip()[0]=='#':
				algo.append(line)
		with open(f'{name}/{stu.name}-Algo.txt','w') as f:
			f.writelines(algo)

def mod_student():
	stu = select_student()
	if not stu:
		return
	choice = -1
	new = Student(stu.name, stu.period, stu.github)
	new.assignments = stu.assignments
	while choice != 0 and stu:
		print(stu)
		print("0 - Save/Back to Main Menu")
		print("1 - Change name")
		print("2 - Change github username")
		print("3 - Change class period")
		choice = -1
		while choice not in range(4):
			choice = validate_num("What would you like to change?")
		if choice == 1:
			print(f"Changing {stu.name} name:")
			new.name = change("Enter a new name:",stu.name)
		elif choice == 2:
			print(f"Changing {stu.name} username:")
			new.github = change("Enter a new github username:",stu.github)
		elif choice == 3:
			print(f"Changing {stu.name} period:")
			new.period = change(f"Enter a new period for {stu.name}:",stu.period, True)
		elif choice == 0:
			d = shelve.open('data.dat')
			students = d['students']
			for i in range(len(students)):
				if students[i].name == stu.name:
					students[i] = new
					break
			d['students'] = students
			d.close()
			print('Data saved')

#function to use as a sorting key in choice 5 of mod_student
def fsort(obj):
	return obj.name

def create():
	print("Adding a student to the roster.")
	correct = 'n'
	d =  shelve.open('data.dat')
	students = d['students']
	d.close()
	while correct == 'n':
		fname = input("What is the student's first name?\n").title()
		lname = input("What is the student's last name?\n").title()
		period = int(input("What class period is the student in?\n"))
		git = input("What is the student's GitHub username?\n")
		print(f"Student: {lname}, {fname}")
		print(f"Period: {period}")
		print(f"GitHub username: {git}")
		correct = ask_yn("Is this information correct?")
	#make the student
	new = Student(f"{lname}, {fname}", period, git)
	print("...student created")
	new.add_assignments()
	print("...assignments created")
	students.append(new)
	students.sort(key=fsort)
	d = shelve.open('data.dat')
	d['students'] = students
	print("Student created and added to database. Data Saved.")

def mod_assign():
	stu = select_student()
	if not stu:
		return
	choice = None
	while choice != 0 and stu:
		print(stu)
		print(stu.print_assignments())
		print("0 - Save/Back to Main Menu")
		print("1 - Change a score")
		print("2 - Set as late")
		choice = -1
		while choice not in (0,1,2):
			choice = validate_num("What would you like to do?")
		if choice == 1:
			tag = validate_assign()
			stu.assignments[tag].score = change_float("Enter a new score:", stu.assignments[tag].score)
		elif choice == 2:
			tag = validate_assign()
			l = not stu.assignments[tag].late
			if ask_yn(f"Set {tag} to {l}?") == 'y':
				stu.assignments[tag].set_late()
		elif choice == 0:
			d = shelve.open('data.dat')
			students = d['students']
			for i in range(len(students)):
				if students[i].name == stu.name:
					students[i] = stu
					break
			d['students'] = students
			d.close()
			print('Data saved')

def grade_assignment(tag = None):
	if not tag:
		tag = validate_assign()
	d = shelve.open('data.dat')
	students = d['students']
	d.close()
	for stu in students:
		a = stu.assignments[tag]
		if a.score == 10:
			print(f"{stu.name} already has completed assignment")
		else:
			print(f"Cloning {stu.name}")
			grade(stu,tag)
			print(f"{stu.name}: {tag} - {stu.assignments[tag].score}/10")
	print("Grading complete -- saving...")
	with shelve.open('data.dat') as d:
		d['students'] = students
	print("finished")

def grade_all():
	stu = select_student()
	if not stu:
		return
	with shelve.open('data.dat') as d:
		students = d['students']
		tags = d['assignments']
	for tag in tags:
		print(f"Grading {tag}")
		grade(stu, tag, False)
	for i in range(len(students)):
		if students[i].name == stu.name:
			students[i] = stu
			break
	with shelve.open('data.dat') as d:
		d['students'] = students
		print("Data saved")
	print(f"{stu.name} Assignments: {stu.github}")
	print(stu.print_assignments())


def grade_student(text):
	stu = select_student(text)
	if stu:
		tag = validate_assign()
		try:
			assign = stu.assignments[tag]
			if assign.score < 10:
				print(f'Grading {stu.name} -- on time: {stu.github}')
				grade(stu, tag)
				print(f'{stu.name}: {tag} - {stu.assignments[tag].score}/10')
			elif assign.score == 10:
				print(f"{stu.name} already has completed assignment")
			else:
				print(f"something strange happened in grade_student()")
			print("Grading complete -- saving...")
			d = shelve.open('data.dat')
			students = d['students']
			for i in range(len(students)):
				if students[i].name == stu.name:
					students[i] = stu
					break
			d['students'] = students
			d.close()
			print("Data saved")
		except KeyError as e:
			if tag != "done":
				print("That student doesn't have that assignment")

def report():
	with shelve.open('data.dat') as d:
		students = d['students']
		tags = d['assignments']
	header = ['Period','Name',]
	for tag in tags:
		header.append(tag)
	stuff = [header]
	for stu in students:
		row = [stu.period,stu.name]
		for a in tags:
			s = str(stu.assignments[a].score)
			row.append(s)
		stuff.append(row)
	with open(f'report.csv','w',newline='') as f:
		w = csv.writer(f, delimiter=',')
		w.writerows(stuff)
	print("Report complete")

def grade_multiple():
	tags = []
	r = ''
	while r != 'done':
		print("Enter assignment tags - type 'done' when finished.")
		r = validate_assign()
		if r != 'done':
			tags.append(r)
			print(tags)
	for tag in tags:
		grade_assignment(tag)
	print(f"Grading and Reporting done for {tags}")
