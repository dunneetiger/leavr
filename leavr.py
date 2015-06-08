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

def verif (emp):
    for emp in all_employees.keys():
        print "verif for : " + emp
        print "fname :" + all_employees[emp].fname
        print "jdate : " + all_employees[emp].jDate
        print "lDate : " + all_employees[emp].lDate
        print "country : " + all_employees[emp].country
        print "team : " + ", ".join(all_employees[emp].team)
        print "title: " + all_employees[emp].title
        print all_employees[emp].get_num_employees()


 
if __name__ == '__main__':
 
    filename = "../temp_leavr.txt"
    sys.stdout = open(filename, 'w')
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
                # print "--> field : " + field
                if field == "comment":
                    # print "done with : " + current_uid
                    current_uid = ""
                elif field == "dn":
                    m = re.search(regexp[field], line)
                    current_uid = m.group(1)
                    # print "=> reset the uid to : " + current_uid
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
                        # print "|===>value " + m.group(1)
 
    # verif(all_employees)
