import time
from carList import *
from selenium import webdriver
import os
import sqlite3

pushbullet_on = 0
try:
    from pushhbullet import Pushbullet
    #https://www.pushbullet.com/#settings/account
    #Click Create Access Token and put it here if you want a push whenever a new car is added
    pushbullet_access_token = ''
    #from pushbullet_access import *
    pb = Pushbullet(pushbullet_access_token)
    pushbullet_on = 1
except Exception as e:
    print("pushbullet.py not installed or token not defined. Pushbullet notifications will not be sent.")


def getAllCars():
    with conn:
        cur.execute('SELECT ' + field + ' FROM ' + table_name)
        print(cur.fetchall())

def insertStockNumber(stock_number_to_insert):
    stbSQL = 'INSERT INTO ' + table_name + ' (stock_number)'
    stbSQL += 'SELECT \'' + stock_number_to_insert + '\''
    stbSQL += ' WHERE NOT EXISTS(SELECT 1 FROM ' + table_name + ' WHERE stock_number = \'' + stock_number_to_insert + '\');'
    cur.execute(stbSQL)

#Returns 1 if stock_number already exists in table
def checkStockNumber(stock_number):
    cur.execute('SELECT (EXISTS(SELECT 1 FROM ' + table_name + ' WHERE stock_number=\'' + stock_number + '\' LIMIT 1));')
    return cur.fetchone()[0]

#We don't want to flood the user with new car notifications for every car on first run
#This sets variable first_run = 1 if this is the first_run so we can disable the notifications
#Otherwise it will notify them for each entry
def initializeFirstRun():
    #Runs if table is empty (and this must be the first run)
    if ((cur.execute('SELECT COUNT(' + field + ') FROM ' + table_name).fetchone()[0]) == 0):
        print("Welcome!")
        print("This program will take a few seconds to run for the first time. After that each time you run this program it will notify you if there is a new car added (since this run). Hope it helps you! :)")

        #Insert '1' so that this new table isn't empty (just incase there aren't any cars this first run)
        insertStockNumber('1')
        return 1
    return 0


sqlite_file = 'car_db.sqlite'    # name of the sqlite database file
table_name = 'car'  # name of the table to be created
field = 'stock_number' # name of the column
field_type = 'STRING'  # column data type

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS ' + table_name + ' (' + field + ' ' + field_type + ')')

#This determines if we should notify the user of car additions (because no spam on first run)
first_run = initializeFirstRun()
if first_run == 0: print("Looking for cars. Please wait.")

#Print all cars in DB now
#getAllCars()

#Get current directory
dir = os.path.dirname(os.path.realpath(__file__))

chrome_driver_path = dir + "/chromedriver"
phantomjs_path = dir + "/phantomjs"

#PhantomJS doesn't open a browser window, so it is more discreet and nice. Use Chrome if errors?
driver = webdriver.PhantomJS(phantomjs_path)
#driver = webdriver.Chrome(chrome_driver_path)

#Load website and wait for it to load
driver.get('http://parts.pickapart.ca/?md=submit&model=' + car_type)
time.sleep(2)

#Give the main table an id, just to make things easier when using Selenium selectors
tbody_id = 'car-tbody'
driver.execute_script('$(\'table.main tbody\').attr(\'id\', \'' + tbody_id + '\');')

#Get main table by id, then get a list of all rows in the table
car_tbody = driver.find_element_by_id(tbody_id)
rows = car_tbody.find_elements_by_tag_name('tr')

#Table row is being used for headers, so remove them from the list
rows.pop(0)

#Traverse each row in the table
new_cars_found = 0
for row in rows:
    #Get a list of all cells in the row
    cells = row.find_elements_by_tag_name('td')

    #Get pickapart stock number of car in row
    current_stock_number = cells[10].get_attribute('innerHTML')

    #Find out of car is in our DB or not
    new_car_bool = checkStockNumber(current_stock_number)

    #Runs if a new car is found, only if you have run the program before
    if new_car_bool == 0:
        #Add to DB so it is not counted next time
        insertStockNumber(current_stock_number)
        new_cars_found += 1

        #Notify the user
        if first_run == 0:
            #Get some more information about the car
            date_added = cells[1].get_attribute('innerHTML')
            make = cells[2].get_attribute('innerHTML')
            model = cells[3].get_attribute('innerHTML')
            year = cells[4].get_attribute('innerHTML')
            body = cells[5].get_attribute('innerHTML')
            engine = cells[6].get_attribute('innerHTML')
            descriptor_string = year + " " + make + " " + model + ", " + body + ", " + engine + " was added on " + date_added
            print(descriptor_string)

            #Send notification to my pushbullet
            if pushbullet_on == 1:
                push = pb.push_note("New car available at Pick-a-Part!", descriptor_string)


if new_cars_found == 0:
    print("No new cars found :(")

conn.commit()
conn.close()
quit()
