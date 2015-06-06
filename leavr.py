#!/usr/bin/python -u
import subprocess
import sys
import re
 
class Employee:
    # number of employees
    num_employee = 0

    def __init__(self):
        self.fname   = {'type' : 'alpha'}
        self.uid     = {'type' : 'alpha'}
        self.jDate   = {'type' : 'alpha'}
        self.lDate   = {'type' : 'alpha'}
        self.country = {'type' : 'alpha'}
        self.pict    = {'type' : 'alpha'}
        self.team    = {}
        self.num_employee += 1
    
    def get_num_employees(self):
        return self.num_employee

 
def get_line (filename):
    with open(filename, 'r') as f:
        for line in f:
            yield line
 
 
if __name__ == '__main__':
 
    filename = "../temp_leavr.txt"
    # sys.stdout = open(filename, 'w')
    # print subprocess.Popen("ldapsearch -b \"DC=ORBISUK,DC=COM\" -h ldap -x gecos uid x-joiningDate x-leavingDate x-orbisTeam c -S x-joiningDate", shell=True, stdout=subprocess.PIPE).stdout.read()
    # sys.stdout = sys.__stdout__
 
 
    dict_fields = {}
     
    dict_fields['comment'] = '^(#|search:) .*$'
    dict_fields['dn']      = '^dn: uid=([a-zA-Z0-9_]+),.*$'
    dict_fields['uid']     = '^uid: ([a-zA-Z0-9_]+)*$'
    dict_fields['team']    = '^x-orbisTeam: cn=([a-zA-Z0-9_]+),.*$'
    dict_fields['country'] = '^c: ([a-zA-Z0-9_]+)*$'
    dict_fields['jDate']   = '^x-joiningDate: ([0-2][0-9][0-9][0-9]-[0-1][0-9]-[0-9]+)$'
    dict_fields['lDate']   = '^x-leavingDate: ([0-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9])$'
    dict_fields['fname']   = '^gecos: ([a-zA-Z0-9_ ]+),.*$'
     
    all_employees = {}
     
    current_uid   = ""
 
    for line in get_line(filename):
        for field in dict_fields.keys():
            if re.match(dict_fields[field], line):
                # print "--> field : " + field
                if field == "comment":
                    print "done with : " + current_uid
                    current_uid = ""
                elif field == "dn":
                    m = re.search(dict_fields[field], line)
                    current_uid = m.group(1)
                    print "=> reset the uid to : " + current_uid
                    employee = Employee()
                    employee.uid = current_uid
                    employee.lDate = '-'
                    employee.fname = 'Not Correct'
                    all_employees[current_uid] = employee
                else:
                    m = re.search(dict_fields[field], line)
                    if current_uid != "" :
                        setattr(all_employees[current_uid], field, m.group(1))
                        print "|===>value " + m.group(1)
 

    for emp in all_employees.keys():
        print "verif for : " + emp
        print "fname :" + all_employees[emp].fname
        print "jdate : " + all_employees[emp].jDate
        print all_employees[emp].get_num_employees()