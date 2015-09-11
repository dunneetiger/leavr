#!/usr/bin/python -u
import subprocess
import sys
import re
import operator

class Employee:
	# number of employees
	num_employee = 0

	def __init__(self):
		self.fname   = 'Not Correct'
		self.title   = '-'
		self.uid     = None
		self.jDate   = None
		self.lDate   = "-"
		self.country = None
		self.pict    = None
		self.team    = []
		Employee.num_employee += 1
	
	def get_num_employees(self):
		return Employee.num_employee

 
def get_line (filename):
	with open(filename, 'r') as f:
		for line in f:
			yield line

def print_info (all_employees, employee, fields=[]):
	# Print given field for given employee
	print "verif for : " + employee

	if len(fields) == 0:
		print "fname :" + all_employees[employee].fname
		print "jdate : " + all_employees[employee].jDate
		print "lDate : " + all_employees[employee].lDate
		print "country : " + all_employees[employee].country
		print "team : " + ", ".join(all_employees[employee].team)
		print "title: " + all_employees[employee].title
	else:
		for field in fields:
			print field + " : " + getattr(all_employees[employee], field)
 
	print "--"

def verif (all_employees):
	for employee in all_employees.keys():
		print_info(all_employees, employee)
	print all_employees[employee].get_num_employees()

def sort_by_field (all_employees, field="lDate"):
	# Sort by giving field - defaults to leaving date
	for employee in (sorted(all_employees.values(), key=operator.attrgetter(field))):
		print_info(all_employees, employee.uid)

if __name__ == '__main__':
 
	filename = "temp_leavr.txt"
	sys.stdout = open(filename, 'w+')
	print subprocess.Popen("ldapsearch -b \"DC=ORBISUK,DC=COM\" -h ldap -x objectClass=orbisPerson gecos uid x-joiningDate x-leavingDate x-orbisTeam c -S x-joiningDate", shell=True, stdout=subprocess.PIPE).stdout.read()
	sys.stdout = sys.__stdout__
 
	regexp = {}
	 
	regexp['comment'] = '^(#|search:) .*$'
	regexp['dn']      = '^dn: uid=([a-zA-Z0-9_]+),.*$'
	regexp['uid']     = '^uid: ([a-zA-Z0-9_]+)*$'
	regexp['team']    = '^x-orbisTeam: cn=([a-zA-Z0-9_]+),.*$'
	regexp['country'] = '^c: ([a-zA-Z0-9_-]+)*$'
	regexp['jDate']   = '^x-joiningDate: ([0-2][0-9][0-9][0-9]-[0-1][0-9]-[0-9]+)$'
	regexp['lDate']   = '^x-leavingDate: ([0-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9])$'
	regexp['fname']   = '^gecos: ([a-zA-Z0-9_ \-\']+), ([a-zA-Z0-9_ \-\&\+\'\.\/\(\)\;\,]+)$'
	 
	all_employees = {}
	 
	current_uid   = ""
 
	for line in get_line(filename):
		for field in regexp.keys():
			if re.match(regexp[field], line):
				if field == "comment":
					current_uid = ""
				elif field == "dn":
					m = re.search(regexp[field], line)
					current_uid = m.group(1)
					employee = Employee()
					employee.uid = current_uid
					all_employees[current_uid] = employee
				else:
					m = re.search(regexp[field], line)
					if current_uid != "" :
						if field == "team" :
							all_employees[current_uid].team.append(m.group(1))
						elif field == "fname" :
							all_employees[current_uid].fname = m.group(1)
							all_employees[current_uid].title = m.group(2)
						else :	
							setattr(all_employees[current_uid], field, m.group(1))
	
	# verif(all_employees)
	sort_by_field(all_employees)
