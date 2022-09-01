import shelve, os, datetime, json
from sys import exit

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

def set_students():
	students = []
	if os.path.exists('students.dat'):
		print("Loading students...")
		with shelve.open('students.dat') as d:
			for e in d:
				students.append(Student(e.name,e.period,e.github))
		with shelve.open('data.dat') as d:
			d['students'] = students
		print(f"{len(students)} loaded")
		os.system("rm students.dat")
	else:
		print("Couldn't find \"students.dat\" file. Did you import it from NUAMES-CS/RSA-Encryption?")

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
			score = int(f.read())
		os.system("rm score.txt")
	except KeyboardInterrupt:
		print("Student test terminated")
		score = None
	except ValueError:
		print("non-numeric data in score.txt")
		score = None
	except FileNotFoundError:
		print("couldn't find score.txt file")
		score = None
	return score

def grade(stu, tag, simple = True):
	os.system(f"gh repo clone nuames-cs/{tag}{github} student -- -q")
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
		grade(stu, tag)
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
			if assign.score < 5 and assign.late:
				print(f'Grading {stu.name} -- late')
				grade(stu,tag, False)
				print(f'{stu.name}: {tag} - {stu.assignments[tag].score}/10')
			elif assign.score < 10 and not assign.late:
				print(f'Grading {stu.name} -- on time: {stu.github}')
				grade(stu, tag, False)
				print(f'{stu.name}: {tag} - {stu.assignments[tag].score}/10')
			elif (assign.score == 10 and not assign.late) or (assign.score == 5 and assign.late):
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
