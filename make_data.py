import shelve

def reset_data():
	d = shelve.open('data.dat')
	#list of 1030 assignment prefixes
	d['python'] = ('00p','01p','02p','03p','04p','05p','06p','07p','08p','09p','10p','11p','12p','13p','14p','15p')
	#list of 1400 assignment prefixes
	d['java'] = ('00j','01j','02j','03j','04j','05j','06j','07j','08j','09j','10j','11j','12j','13j','14j','15j','16j','17j','18j','19j','20j','21j')
	#list of course periods
	periods = []
	for i in range(8):
		periods.append('empty')
	d['periods'] = periods
	d.close()

def validate_num(question):
	ok = False
	while not ok:
		try:
			number = int(input(f"{question}\n"))
			ok = True
		except ValueError:
			print("That wasn't a number")
	return number

def ask_yn(question):
	r = ''
	while r not in ('y','n'):
		r = input(f"{question} (Y/n)\n").lower()
	return r

def set_periods():
	r = 'n'
	d = shelve.open('data.dat')
	periods = d['periods']
	#while not correct
	while r == 'n':
		n = validate_num("How many 1030 sections this semester?")
		for i in range(n):
			x = validate_num(f"Enter class period for 1030 section number {i+1}:")
			periods[x-1] = '1030'
		n = validate_num("How many 1400 sections this semester?")
		for i in range(n):
			x = validate_num(f"Enter class period for 1400 section number {i+1}:")
			periods[x-1] = '1400'
		print(f"Periods: {periods}")
		r = ask_yn("Is this correct?")
	d['periods'] = periods
	d.close()
	print("Course periods have been saved")

def display():
	with shelve.open('data.dat') as f:
		periods = f['periods']
		p = []
		j = []
		for i in range(len(periods)):
			if periods[i] == '1030':
				p.append(i+1)
			elif periods[i] == '1400':
				j.append(i+1)
		print(f"{len(p)} Python classes, {len(j)} Java classes")
		print(f"\tPython periods: {p}")
		print(f"\tJava periods: {j}")
	
def main():
	print("Welcome to the Simonsen AutoGrater Data Utility")
	c = 0
	while c != 'q':
		print("q - Quit")
		print("v - View Classes")
		print("s - Set Classes")
		print("r - Reset Data")
		c = input("What's your selection?\n")

		if c =='q':
			print("Goodbye")
		elif c == 'v':
			display()
		elif c == 's':
			set_periods()
		elif c == 'r':
			reset_data()
		else:
			print("That's not a valid menu option.")

if __name__ == "__main__":
	main()

