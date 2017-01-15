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
import numpy as np

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

# Function creates array names 'plane' in order to easily iterate through the
# occupied and empty seats. This array is not returned and as a result, is 
# never stored in the main programme environment.
#
# Remaining issues to resolve are highlighted in the code body.

def count(A,i): #Eoin comment - count the number of empty seats in row i
    m = np.shape(A)[1] #Eoin added np. in front of shape and empty functions
    c = 0
    for j in range(m):
        if A[i,j] == '': #Here and 106 is where program gets stuck
            c = c+1
    return(c)

def count_str(A,string): #Eoin comment - count the number seats with same name as string
    n = np.shape(A)[0]
    m = np.shape(A)[1]
    c = 0
    for j in range(m):
        for i in range(n):
            if A[i,j] == string:
                c = c+1
    return(c)

def ASSIGN(db,bookname,booksize):
    # Connect to database and retrieve plane dimensions
    conn = sqlite3.connect(db)
    c = conn.cursor()
    rowcol = c.execute("SELECT * FROM rows_cols").fetchone()
    letters = str(rowcol[1])
    
    # Generate blank numpy array called plane that matches configuration
    plane = np.zeros([rowcol[0],len(rowcol[1])],dtype="S50") #Eoin note - took out data type
    """for i in range(rowcol[0]):
        for j in range(len(rowcol[1])): #Eoin added len here
            plane[i,j] = ''"""

    print(plane)    
    
    # Retrieve bookings currently in the database and assign them to the 
    # corresponding seats in the array 'plane'
    occupied = c.execute("SELECT * FROM seating WHERE name != '%s'" %'').fetchall()
    r = []
    s = []
    for i in range(len(occupied)):
        r.append(occupied[i][0])
        s.append(occupied[i][1])
    for k in range(len(r)):
        for i in range(rowcol[0]):
            for j in range(len(rowcol[1])):  #Eoin added len here
                if str(i) == str(r[k]) and letters[j] == str(s[k]):
                    plane[i,j] = str(occupied[k][2])

    print(plane)     
    
    # Main assign step for new booking. System operates by trying to fit the
    # largest possible group together in one row, each time scanning rows from
    # front to back. Functions 'count' and 'count_str' are already uploaded in
    # local array method branch. Assigning step assumes all seats are booked and
    # then allocated in a left-to-right manner with no gaps within a given row.
    remain = booksize
    dummy = 0
    while count_str(plane,bookname) < booksize:
        current = count_str(plane,bookname)
        print(current) #Eoin added for debugging
        for i in range(rowcol[0]):
            if count(plane,i) >= remain: #Eoin note - assume count counts empty seats in row i
                for j in range(len(rowcol[1])): #Eoin added len here
                    if plane[i,j] == '':
                        plane[i,j:j+remain] = bookname
                        for k in range(remain):
                            ##### ##### ##### ##### #####
                            
                            c.execute("UPDATE seating SET name = '%s' WHERE row = %d AND seat = '%s'" %(bookname,i+1,letters[j+k]))
                            # Line is considered too time consuming for SQLite to handle. Returns error message:
                            #      OperationalError: database is locked
                            # Needs to be fixed for function to run properly.
                            
                            ##### ##### ##### ##### #####
                            conn.commit()
                        break
                break 
        if count_str(plane,bookname) > current:
            remain = dummy
            dummy = 0
        else:
            remain = remain - 1
            dummy = dummy + 1
    
    # Retrieve current value of separation metric
    metrics = c.execute("SELECT * FROM metrics").fetchall()
    separated = metrics[0][1]
    
    # Generate list of row numbers for newly allocated seats
    position = []
    for i in range(rowcol[0]):
        for j in range(len(rowcol[1])): #Eoin added len here
            if plane[i,j] == bookname:
                position.append(i)
    
    # Define separation metric to be the number of group splits. Update the
    # database with new metric value
    separations = len(set(position)) - 1
    c.execute("UPDATE metrics SET passengers_separated = %d" %(separated+separations))
    conn.commit()
    conn.close()
    
    # Print confirmation that booking has been made
    print('Booking Confirmed')    
   



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
        ASSIGN(DB_file, booking_name[i], int(booking_size[i]))
        free_seats = free_seats - booking_size[i]