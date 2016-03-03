#!/usr/bin/python -u
import datetime
import operator
import re
import subprocess
import sqlite3
import sys

class Employee:

	def __init__(self):
		self.fname   = 'Not Correct'
		self.title   = '-'
		self.uid     = None
		self.jDate   = None
		self.lDate   = "-"
		self.country = None
		self.pict  	  = None
		self.team    = []

        def __dir__(self):
            return ['fname', 'title', 'uid', 'jDate', 'lDate', 'country', 'team']

	def __str__(self):
		return str(self.__dict__)

	def __cmp__(self, other):
	#		print "self.title: " + self.title + "-"
	#		print "other.title: " + other.title + "-"
	#		print "self.lDate: " + self.lDate + "-"
	#		print "other.lDate: " + other.lDate + "-"
	#		print "self.team: -" + ", ".join(self.team) + "-"
	#		print "other.team: -" + ", ".join(other.team) + "-"
		return (self.title == other.title) and (self.fname == other.fname) and (self.jDate == other.jDate) and (self.lDate == other.lDate) and (self.team == other.team) and (self.country == other.country)

	def __eq__(self, other):
	#		print "self.title: " + self.title + "-"
	#		print "other.title: " + other.title + "-"
	#		print "self.lDate: " + self.lDate + "-"
	#		print "other.lDate: " + other.lDate + "-"
	#		print "self.team: -" + ", ".join(self.team) + "-"
	#		print "other.team: -" + ", ".join(other.team) + "-"
		return (self.title == other.title) and (self.fname == other.fname) and (self.jDate == other.jDate) and (self.lDate == other.lDate) and (self.team == other.team) and (self.country == other.country)

 
def get_line (filename):
	"""
		name: get_line
		param: <name of a file>

		Yield a line
	"""

	with open(filename, 'r') as f:
		for line in f:
			yield line

def print_info (all_employees, employee, fields=[]):
	"""
		name: print_info
		param: <dictionary>,<key> [, <field to print>]
		Print given field for given employee
		If no field is given, all fields will be printed
	"""
	
        for attr in dir(all_employees[employee]):
            if attr in fields:
                field_name = "* " + attr
            else:
                field_name = attr

            if attr == "team": 
                if len(all_employees[employee].team) == 0:
                        team = "None"
                else:
                        team = ", ".join(all_employees[employee].team)
                print field_name + " : " + team
            else:
               print field_name + " : " + getattr(all_employees[employee], attr)
 
	print "--"

def print_all_information (all_employees):
	"""
		name: print_all_information
		param: dictionary

		For a given dictionary of employees, it will print all the print_all_information
		in the system
	"""

	for employee in all_employees.keys():
		print_info(all_employees, employee)
	print all_employees[employee].get_num_employees()


def sort_by_field (all_employees, field="lDate"):
	"""
		name: sort_by_field
		param: <dictionary of employees> [, <field>]

		Sort by given field - defaults to leaving date
	"""

	for employee in (sorted(all_employees.values(), key=operator.attrgetter(field))):
		print_info(all_employees, employee.uid)


def search_ldap(filename) :
	"""
		name: search_ldap
		param: <name of the file where we will write the output of the file>

		Search ldap and populate temp file
	"""

	sys.stdout = open(filename, 'w+')
	print subprocess.Popen("ldapsearch -b \"DC=ORBISUK,DC=COM\" -h ldap -x objectClass=orbisPerson gecos uid x-joiningDate x-leavingDate x-orbisTeam c -S x-joiningDate", shell=True, stdout=subprocess.PIPE).stdout.read()
	sys.stdout = sys.__stdout__


def set_employee_dict(filename, all_employees):
	"""
		name: set_employee_dict
		param: <name of the file with the ldap info>, <dictionary of employee>

		Search and populate the employee dictionary
	"""

	current_uid   = ""

	
	search_ldap(filename)
 
	regexp = {}
	 
	regexp['comment'] = '^(#|search:) .*$'
	regexp['dn']      = '^dn: uid=([a-zA-Z0-9_]+),.*$'
	regexp['uid']     = '^uid: ([a-zA-Z0-9_]+)*$'
	regexp['team']    = '^x-orbisTeam: cn=([a-zA-Z0-9_]+),.*$'
	regexp['country'] = '^c: ([a-zA-Z0-9_-]+)*$'
	regexp['jDate']   = '^x-joiningDate: ([0-2][0-9][0-9][0-9]-[0-1][0-9]-[0-9]+)$'
	regexp['lDate']   = '^x-leavingDate: ([0-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9])$'
	regexp['fname']   = '^gecos: ([a-zA-Z0-9_ \-\']+), ([a-zA-Z0-9_ \-\&\+\'\.\/\(\)\;\,]+)$'
	 
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
	return all_employees
	# verif(all_employees)

def insert_db (sql_cur, employee_data):
	
	if len(employee_data.team) == 0:
		team = "None"
	else:
		team = ", ".join(employee_data.team)
	lDate = employee_data.lDate
	if lDate == "-" :
		sql_exec = "INSERT INTO tEmployee (title, fname, uid, jDate, country, pict, team) VALUES (\"{0}\", \"{1}\", \"{2}\", \"{3}\", \"{4}\", \"{5}\", \"{6}\");".format(employee_data.title, employee_data.fname, employee_data.uid, employee_data.jDate, employee_data.country, employee_data.pict, team)
	else:
		sql_exec = "INSERT INTO tEmployee (title, fname, uid, jDate, lDate, country, pict, team) VALUES (\"{0}\", \"{1}\", \"{2}\", \"{3}\", \"{4}\", \"{5}\", \"{6}\", \"{7}\");".format(employee_data.title, employee_data.fname, employee_data.uid, employee_data.jDate, lDate, employee_data.country, employee_data.pict, team)
		
	sql_cur.execute(sql_exec);


def update_db (sql_cur, employee_data):
	
	if len(employee_data.team) == 0:
		team = "None"
	else:
		team = ", ".join(employee_data.team)
	lDate = employee_data.lDate
	if lDate == "-" :
		sql_exec = "Update tEmployee set title = \"{0}\", fname = \"{1}\", uid = \"{2}\", jDate = \"{3}\", country = \"{4}\", pict = \"{5}\", team = \"{6}\"  where uid = \"{2}\";".format(employee_data.title, employee_data.fname, employee_data.uid, employee_data.jDate, employee_data.country, employee_data.pict, team)
	else:
		sql_exec = "Update tEmployee set title = \"{0}\", fname = \"{1}\", uid = \"{2}\", jDate = \"{3}\", lDate = \"{4}\", country = \"{5}\", pict = \"{6}\", team = \"{7}\"  where uid = \"{2}\";".format(employee_data.title, employee_data.fname, employee_data.uid, employee_data.jDate, lDate, employee_data.country, employee_data.pict, team)

	sql_cur.execute(sql_exec);



def load_to_sqlite(sql_cur, all_employees):

	for employee in all_employees.keys():
		emp = all_employees[employee]
		insert_db(sql_cur, emp)

	sql_exec = "INSERT INTO tControl (lastUpd) VALUES (datetime('now')); ";
	sql_cur.execute(sql_exec);

def unload_from_sqlite(sql_cur, employees_dict):

	sql_stmt = "select title, fname, uid, jDate, lDate, country, pict, team from tEmployee;"	
	sql_cur.execute(sql_stmt)

	rows = sql_cur.fetchall()

	for row in rows:
		employee = Employee()
		employee.title = row[0]
		employee.fname = row[1]
		employee.uid   = row[2]
		employee.jDate = row[3]
		lDate = row[4]
		if lDate == None or lDate == "":
			employee.lDate = "-"
		else:
			employee.lDate = row[4]
		employee.country = row[5]
		employee.pict    = row[6]
		if row[7] == "None":
			employee.team = []
		else:
			employee.team  = row[7].split(", ")

		employees_dict[employee.uid] = employee
	
	return employees_dict

def changed_fields(old_dict, new_dict, employee):
    new_details  = new_dict[employee]
    old_details  = old_dict[employee]

    list_fields = []
    for attr in dir(new_details):
        if getattr(new_details, attr) != getattr(old_details, attr):
            print "field: {0},  old value: {1},  new value: {2}".format(attr, getattr(new_details, attr), getattr(old_details, attr))
            list_fields.append(attr)
    return list_fields

def update_dict(sql_cur, old_dict, new_dict):

	for key in new_dict.keys():
		if key in old_dict.keys():
			# Check for modification (always assume new is correct)
			if new_dict[key] == old_dict[key]:
				pass
                        else:
				# Update entry in DB
				update_db(sql_cur, new_dict[key])
                                sql_exec = "Update tControl set lastUpd = datetime('now'); "
				sql_cur.execute(sql_exec)
				print_info(new_dict, key, changed_fields(old_dict, new_dict, key))

		else:
			# Check for new entries in new (we dont delete so there wouldnt be a need to check for removal)
			print "Inserting {0}".format(key)
			sql_exec = "Update tControl set lastUpd = datetime('now'); "
			sql_cur.execute(sql_exec)
			insert_db(sql_cur, new_dict[key])
			print_info(new_dict, key)

def current_stat(sql_cur):
    sql_exec = "select country, count(*) from tEmployee where lDate is null group by country order by count(*);"
    for row in sql_cur.execute(sql_exec):
        print row

def create_or_update():

	filename = "temp_leavr.txt"
	sqlite_file = "db/leavr.db"

	employees_new = {}
	

	conn = sqlite3.connect(sqlite_file)

	with conn:
		
		conn.text_factory = str
		cur  = conn.cursor()
		# check if this is the first time the program is run
		cur.execute('select * from tControl;')
		row = cur.fetchone()
		# if row == None:
		#	employees_ldap = set_employee_dict(filename, employees_old)
			# if it is, then initialise
		#	load_to_sqlite(cur, employees_ldap)
		#else:
		employees_new = set_employee_dict(filename, employees_new)
                employees_old = {}
		unload_from_sqlite(cur, employees_old)
                update_dict(cur, employees_old, employees_new)
		# print "Last Updated: {0}".format(row[0])
                current_stat(cur)
	# sort_by_field(employees_old)

if __name__ == '__main__':
	create_or_update()
