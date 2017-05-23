#!/bin/python
from uwaterlooapi import UWaterlooAPI
uw = UWaterlooAPI(api_key="db2f06438ed0d3131473a3fef959b190")
import datetime
import json


class course:
    __subject = ""
    __catalog = ""
    __section = ""
    __startTime = ""
    __endTime = ""
    __weekdays = ""

    def __init__(self, subject, catalog, section):
        self.__subject = subject
        self.__catalog = catalog
        self.__section = section
        self.__startTime = find_start_time(subject, catalog, section)
        self.__endTime = find_end_time(subject, catalog, section)
        self.__weekdays = find_weekdays(subject, catalog, section)

    def get_subject(self):
        return self.__subject

    def get_catalog(self):
        return self.__catalog

    def get_section(self):
        return self.__section

    def get_start_time(self):
        return self.__startTime

    def get_end_time(self):
        return self.__endTime

    def get_weekdays(self):
        return self.__weekdays

    def __repr__(self):
        v = "Subject: " + str(self.__subject) + "\nCatalog: " + str(self.__catalog) + "\nSection: "
        v += str(self.__section) + "\nStart time: " + str(self.__startTime) + "\nEnd time: "
        v += str(self.__endTime) + "\nWeekdays: " + str(self.__weekdays)
        return v

    def __eq__(self, other):
        return self.__subject == other.__subject and self.__catalog == other.__catalog and self.__section == other.__section

schedule = list();

def find_start_time(subject, catalog, section):
    c = uw.term_course_schedule(1175, subject, catalog)
    for i in c:
        if i['section'] == section:
            return i['classes'][0]['date']['start_time']

def find_end_time(subject, catalog, section):
    c = uw.term_course_schedule(1175, subject, catalog)
    for i in c:
        if i['section'] == section:
            return i['classes'][0]['date']['end_time']

def find_weekdays(subject, catalog, section):
    c = uw.term_course_schedule(1175, subject, catalog)
    for i in c:
        if i['section'] == section:
            return i['classes'][0]['date']['weekdays']

def jdefault(obj):
    return obj.__dict__

def add_course(subject, catalog, section):
    c = course(subject, catalog, section)
    if c in schedule:
        print("This course is already added.")
    else:
        schedule.append(c)
        send_to_JSON()

def drop_course(subject, catalog, section):
    for i in schedule:
        if i.get_subject() == subject and i.get_catalog() == catalog and i.get_section() == section:
            schedule.remove(i)
            send_to_JSON()
            return None
    print("No such course was added to your schedule")


def send_to_JSON():
    f = open("schedule.json","w")
    f.write(json.dumps({'schedule': schedule}, default=jdefault))
    f.close()

def view_schedule():
    f = open("schedule.json","r")
    data = f.read();
    d = json.loads(data)
    print(json.dumps(d, indent=4, sort_keys=True))
    f.close()

def update_schedule():
    f = open("schedule.json","r")
    data = f.read();
    if data != "":
        d = json.loads(data)
        numberOfCourse = len(d['schedule'])
        for i in range(0,numberOfCourse):
            c = course(d['schedule'][i]['_course__subject'],d['schedule'][i]['_course__catalog'],d['schedule'][i]['_course__section'])
            schedule.append(c)
        f.close()

def weekday_to_number(str):
    if str is None:
        return [0]
    else:
        DayW = ['empty','M','T','W','Th','F','S','Su']
        DayN = [0] * len(str)
        countDayN = 0
        countStr = 0
        while countStr < len(str):
            if str[countStr] == 'T' and len(str) > 1 and str[countStr+1] == 'h':
                DayN[countDayN] = 4
                countStr += 1
            elif str[countStr] == 'S' and str[countStr+1] == 'u':
                DayN[countDayN] = 6
                countStr += 1
            else:
                DayN[countDayN] = DayW.index(str[countStr])
            countDayN += 1
            countStr += 1
        return(DayN)

def next_lecture(subject, catalog):
    c = uw.term_course_schedule(1175, subject, catalog)
    currentDay = datetime.datetime.now().weekday() + 1
    currentTime = datetime.datetime.now().time()
    attendableCount = 1

    for i in c:
        daysWithClasses = i['classes'][0]['date']['weekdays']
        startTimeString = i['classes'][0]['date']['start_time']
        weekdaysArray = weekday_to_number(daysWithClasses)
        building = i['classes'][0]['location']['building']
        room = i['classes'][0]['location']['room']

        if weekdaysArray is not None and startTimeString is not None and building is not None:
            start_time = datetime.datetime.strptime(startTimeString, '%H:%M').time()
            if currentDay in weekdaysArray and currentTime <= start_time:
                print("\nAttenable section " + str(attendableCount))
                attendable = course(i['subject'],i['catalog_number'],i['section'])
                print(attendable.__repr__())
                print("Location: " + building)
                print("Room: " + room)
                attendableCount += 1

def main_menu():
    print("1. Add course\n" + "2. Drop course\n" + "3. View Schedule\n" + "4. Next lecture")
    option = input("Enter number for the option you want: ")
    if option == 1:
        subject = raw_input("Enter subject: ")
        catalog = raw_input("Enter catalog_number: ")
        section = raw_input("Enter section: ")
        add_course(subject, catalog, section)
    elif option == 2:
        subject = raw_input("Enter subject: ")
        catalog = raw_input("Enter catalog_number: ")
        section = raw_input("Enter section: ")
        drop_course(subject, catalog, section)
    elif option == 3:
        view_schedule()
    elif option == 4:
        subject = raw_input("Enter subject: ")
        catalog = raw_input("Enter catalog_number: ")
        next_lecture(subject, catalog)
    else:
        print("Invalid input: Please enter a number! Try again!")
        main_menu()

update_schedule()
main_menu()
