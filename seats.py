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
    
    conn = sqlite3.connect(DB_file)
    c = conn.cursor()
    nrows = c.execute("SELECT * FROM rows_cols;").fetchone()[0]
    seat_layout = c.execute("SELECT * FROM rows_cols;").fetchone()[1]
    seats_column = c.execute("SELECT name FROM seating;").fetchall()

    free_seats = 0
    for row in range(nrows * len(seat_layout)): #Go through range
        if seats_column[row] == ('',):
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


"""   
def seat(DB_file, booking_name, booking_size):   
        
        #Seating Algorithm        
        
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
"""

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
        # seat(DB_file, booking_name[i], int(booking_size[i]))