# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 11:49:25 2017

@author: Eoin Carroll

UCD Analytics Research & Implementation MIS40750
Programming Assignment
Deadline: 5pm Friday 24th February 2017.
Worth: 20% of the module.

Resources used:
https://docs.python.org/2/library/sqlite3.html

"""

import sqlite3
import csv

DB_file = "airline_seating.db" #Filename for DB as default
CSV_file = "bookings.csv" #Filename for CSV as default

def readDB(DB_file = "airline_seating.db"): #Read and return seat layout. Return number of unoccupied seats
    
    conn = sqlite3.connect(DB_file) #Open db file
    c = conn.cursor()
    nrows = c.execute("SELECT * FROM rows_cols;").fetchone()[0] #read amount of rows
    seat_layout = c.execute("SELECT * FROM rows_cols;").fetchone()[1] #read seat layout
    seats_column = c.execute("SELECT name FROM seating;").fetchall() #read column of seated passangers

    free_seats = 0
    for row in range(nrows * len(seat_layout)): #Go through range
        if seats_column[row] == ('',): #if seat is empty, increase free seat count by one
            free_seats += 1
    
    c.close()
    conn.close()    
    
    return nrows, seat_layout, free_seats    

def readCSV(CSV_file = "bookings.csv"): #Read and return CSV file and number of bookings
    #Not ideal as this could use a lot of memory for a big CSV file
    #Need to change this to read one by one

    with open(CSV_file, 'r') as csvfile:
        booking_list = csv.reader(csvfile)
        booking_number = 0
        booking_name = []
        booking_size = []
        for row in booking_list:
            booking_name.append(row[0])
            booking_size.append(row[1])#bookings[1][0] #Read booking_size
            booking_number += 1
    
    csvfile.close()
    #print(booking_number, booking_name, booking_size)     
    #If error or reached end of file, booking_name = False

    return booking_number, booking_name, booking_size

#Seating Algorithm - recursive
#seat_all = True -> used for recursion, if we want to seat all in this run or report back there is no space
def seat(DB_file, booking_name, booking_size, seat_all = True):
    seated = 0    
    
    if assign(DB_file, booking_name, booking_size) == True: #try seat booking number
        # Print confirmation that booking has been made
        print('Booking Confirmed: ', booking_name, booking_size)
        seated = booking_size
        
    elif seat_all == True:
        
        #increase db count every time a group is split
        conn = sqlite3.connect(DB_file)
        c = conn.cursor()
        passengers_separated = c.execute("SELECT * FROM metrics;").fetchone()[1]    
        passengers_separated += 1 
        c.execute("UPDATE metrics SET passengers_separated = ?;", (passengers_separated,))
        print("passengers_separated", passengers_separated)
        conn.commit()
        c.close()
        conn.close()        
        
        i = 1
        while seated < booking_size:
            seated = seat(DB_file, booking_name, booking_size - i, False)
            i += 1
        
        seat(DB_file, booking_name, i, True)    
    
    return seated


def assign(DB_file, booking_name, booking_size):  
    conn = sqlite3.connect(DB_file)
    c = conn.cursor()
    
    seat_layout = c.execute("SELECT * FROM rows_cols;").fetchone()[1] #read seat layout
    if booking_size > len(seat_layout): #if we can't fit on one row, need to split
        c.close()
        conn.close()
        print("False returned row 102")
        return False
    
    seated_list = c.execute("SELECT name FROM seating").fetchall()

    #look for row with enough free space

    i = 0
    print(seated_list[i][0])
    conn.commit()
    c.close()
    conn.close()
    return True

#Main function now follows
nrows, seat_layout, free_seats = readDB(DB_file)
#print("nrows:", nrows)
#print("seat_layout:", seat_layout)
#print("free_seats:", free_seats)
booking_number, booking_name, booking_size = readCSV(CSV_file)
#print("booking_number:", booking_number)
#print("booking_name:", booking_name)
#print("booking_size:", booking_size)


for i in range(booking_number):
    if free_seats == 0:
        print("No more Free Seats, reject", int(booking_size[i]))
        #increase db count passengers refused by booking_size        
        conn = sqlite3.connect(DB_file)
        c = conn.cursor()
        passengers_refused = c.execute("SELECT * FROM metrics;").fetchone()[0]    
        passengers_refused += int(booking_size[i])
        c.execute("UPDATE metrics SET passengers_refused = ?;", (passengers_refused,))
        print("passengers_refused", passengers_refused)
        conn.commit()
        c.close()
        conn.close()
        
    elif int(booking_size[i]) > free_seats: #If we cannot accomodate the booking
        print("Not enough free seats, reject", int(booking_size[i]))
        #increase db count passengers refused by booking_size        
        conn = sqlite3.connect(DB_file)
        c = conn.cursor()
        passengers_refused = c.execute("SELECT * FROM metrics;").fetchone()[0]    
        passengers_refused += int(booking_size[i])
        c.execute("UPDATE metrics SET passengers_refused = ?;", (passengers_refused,))
        print("passengers_refused", passengers_refused)
        conn.commit()
        c.close()
        conn.close()

    else:
        print("Booking size okay - seat", (int(booking_size[i])))
        seat(DB_file, booking_name[i], int(booking_size[i]))
        free_seats = free_seats - int(booking_size[i])