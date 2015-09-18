#!/usr/bin/python -u
import datetime
import operator
import re
import subprocess
import sqlite3
import sys
 
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
        self.pict     = None
        self.team    = []
        Employee.num_employee += 1
 
    def __cmp__(self, other):
        pass
     
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
 
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
        print "fname : " + all_employees[employee].fname
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
 
 
def search_ldap(filename) :
    # Search ldap and populate temp file
    sys.stdout = open(filename, 'w+')
    print subprocess.Popen("ldapsearch -b \"DC=ORBISUK,DC=COM\" -h ldap -x objectClass=orbisPerson gecos uid x-joiningDate x-leavingDate x-orbisTeam c -S x-joiningDate", shell=True, stdout=subprocess.PIPE).stdout.read()
    sys.stdout = sys.__stdout__
 
 
def set_employee_dict(filename, all_employees):
    # Parse filename and populate the all_employee dictionary
 
    current_uid   = ""
  
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
     
    # verif(all_employees)
 
 
def load_to_sqlite(sql_cur, all_employees):
 
    for employee in all_employees.keys():
        emp = all_employees[employee]
        team = ", ".join(emp.team)
        lDate = emp.lDate
        if lDate == "-" :
            sql_exec = "INSERT INTO tEmployee (title, fname, uid, jDate, country, pict, team) VALUES (\"{0}\", \"{1}\", \"{2}\", \"{3}\", \"{4}\", \"{5}\", \"{6}\");".format(emp.title, emp.fname, emp.uid, emp.jDate, emp.country, emp.pict, team)
        else:
            sql_exec = "INSERT INTO tEmployee (title, fname, uid, jDate, lDate, country, pict, team) VALUES (\"{0}\", \"{1}\", \"{2}\", \"{3}\", \"{4}\", \"{5}\", \"{6}\", \"{7}\");".format(emp.title, emp.fname, emp.uid, emp.jDate, lDate, emp.country, emp.pict, team)
         
        sql_cur.execute(sql_exec);
 
     
    sql_exec = "INSERT INTO tControl (lastUpd) VALUES (datetime('now')); ";
    sql_cur.execute(sql_exec);
 
 
 
if __name__ == '__main__':
 
    filename = "temp_leavr.txt"
    sqlite_file = "db/leavr.db"
 
    all_employees = {}
     
    search_ldap
     
    set_employee_dict(filename, all_employees)
 
    conn = sqlite3.connect(sqlite_file)
 
    with conn:
        cur  = conn.cursor()
        # check if this is the first time the program is run
        cur.execute('select * from tControl;')
        row = cur.fetchone()
        if row == None:
            # if it is, then initialise
            load_to_sqlite(cur, all_employees)
        else:
            print "Last Updated: {0}".format(row[0])
         
    sort_by_field(all_employees)
    print "All time number of employees : " + str(Employee.num_employee)
