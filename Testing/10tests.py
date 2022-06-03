import unittest, sys, random
from unittest.mock import patch
from io import StringIO
import student

class Tests(unittest.TestCase):
	inputs = "8\n6\n"
	@patch('sys.stdin', StringIO(inputs))
	@patch('sys.stdout', new_callable = StringIO)
	def test01_part_1(self, stdout):
		correct = "How many dice would you like to roll?\nHow many sides do the dice have?\n\nRolling 8x d6.\n"
		student.main()
		result = stdout.getvalue()[:len(correct)]
		self.assertEqual(result, correct)

	inputs = "5\n20\n"
	@patch('sys.stdin', StringIO(inputs))
	@patch('sys.stdout', new_callable = StringIO)
	def test02_part_2(self, stdout):
		correct = "Roll 1: 4\nRoll 2: 20\nRoll 3: 17\nRoll 4: 8\nRoll 5: 9\n"
		random.seed(14)
		student.main()
		result = stdout.getvalue()[88:len(correct)+88]
		self.assertEqual(result, correct)

	inputs = "5\n4\n"
	@patch('sys.stdin', StringIO(inputs))
	@patch('sys.stdout', new_callable = StringIO)
	def test03_part_3(self, stdout):
		correct = "How many dice would you like to roll?\nHow many sides do the dice have?\n\nRolling 5x d4.\nRoll 1: 4\nRoll 2: 4\nRoll 3: 1\nRoll 4: 3\nRoll 5: 4\nTotal: 16\n"
		random.seed(0)
		student.main()
		result = stdout.getvalue()
		self.assertEqual(result, correct)

def main(verbose=False):
	suite = unittest.defaultTestLoader
	runner = unittest.TextTestRunner(stream=StringIO(), descriptions=False)
	result = runner.run(suite.loadTestsFromTestCase(Tests))
	total = result.testsRun
	if result.wasSuccessful():
		score = 10
		passed = total
	else:
		passed = total - len(result.failures) - len(result.errors)
		score = round(passed/total*10,2)
	print(f"Passed: {passed}/{total}")
	print(f"Score: {score}")
	if verbose:
		failed = []
		for i in result.failures:
			failed.append(f"Fail: {i[0].id()[15:]}")
		for i in result.errors:
			failed.append(f"Error: {i[0].id()[15:]}")
		print("Failed:")
		for i in failed:
			print(f"	{i}")
	return score

if __name__ == '__main__':
	main(True)
