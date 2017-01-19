import sqlite3
import csv
import numpy as np

DB_file = "airline_seating.db" #Filename for DB as default
CSV_file = "bookings.csv" #Filename for CSV as default

def count(A,i):
    m = shape(A)[1]
    c = 0
    for j in range(m):
        if A[i,j] == '':
            c = c+1
    return(c)

def count_str(A,str):
    n = shape(A)[0]
    m = shape(A)[1]
    c = 0
    for j in range(m):
        for i in range(n):
            if A[i,j] == str:
                c = c+1
    return(c)

def readDB(DB_file = "airline_seating.db"): #Read and return seat layout. Return number of unoccupied seats
    
    conn = sqlite3.connect(DB_file) #Open db file
    c = conn.cursor()
    nrows = c.execute("SELECT * FROM rows_cols;").fetchone()[0] #read amount of rows
    seat_layout = str(c.execute("SELECT * FROM rows_cols;").fetchone()[1]) #read seat layout
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


# New ASSIGN function which allows the user to specify the separation metric
# interpretation they would prefer. The metric calculations included are:
#       Separated (default):  Number of group splits.
#       Alone:  Number of party members seated alone.
#       Dissatisfaction:  0 if all party members are seated together.
#                         1 if party members are separated but no individuals
#                             are sat alone.
#                         3 if one or more party members are sat alone.


def ASSIGN_metrics_list(db,bookname,booksize,sep = 'Separations'):
    # Connect to database and retrieve plane dimensions
    conn = sqlite3.connect(db)
    c = conn.cursor()
    rowcol = c.execute("SELECT * FROM rows_cols").fetchone()
    letters = str(rowcol[1])
    
    # Retrieve bookings currently in the database and assign them to the 
    # corresponding seats in the list 'plane'
    plane = []
    occupied = c.execute("SELECT * FROM seating WHERE name != '%s'" %'').fetchall()
    r = []
    s = []
    for i in range(len(occupied)):
        r.append(occupied[i][0])
        s.append(occupied[i][1])
    for j in range(len(rowcol[1])):
        for i in range(rowcol[0]):
            x = len(plane)
            for k in range(len(r)):
                if str(i+1) == str(r[k]) and letters[j] == str(s[k]):
                    plane.append(str(occupied[k][2]))
            if len(plane) == x:
                plane.append('')
        
    # Main assign step for new booking. System operates by trying to fit the
    # largest possible group together in one row, each time scanning rows from
    # front to back. Functions 'count' and 'count_str' are already uploaded in
    # local array method branch. Assigning step assumes all seats are booked and
    # then allocated in a left-to-right manner with no gaps within a given row.
    remain = booksize
    dummy = 0
    while count_str_list(plane,bookname) < booksize:
        current = count_str_list(plane,bookname)
        for i in range(rowcol[0]):
            if count_list(plane,i) >= remain:
                for j in range(len(rowcol[1])):
                    if plane[j*rowcol[0]+i] == '':
                        for k in range(remain):
                            plane[(j+k)*rowcol[0]+i] = bookname
                            c.execute("UPDATE seating SET name = ? WHERE row = ? AND seat = ?;", (bookname,i+1,letters[j+k],))
                            conn.commit()
                        break
                break 
        if count_str_list(plane,bookname) > current:
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
        for j in range(len(rowcol[1])):
            if plane[j*rowcol[0]+i] == bookname:
                position.append(i)
    
    if sep == 'Alone':
        # Separation metric defined to be the number of party members seated alone.
        alone = 0
        for i in range(len(position)):
            if position.count(position[i]) == 1:
                alone = alone + 1
        if booksize > 1:
            c.execute("UPDATE metrics SET passengers_separated = ?;", (separated+alone,))
            conn.commit()
    
    elif sep == 'Dissatisfaction':        
        # Separation metric for a given booking defined to be:
        # 0 if all party members are seated together.
        # 1 if party members are separated but no individuals are sat alone.
        # 3 if one or more party members are sat alone.
        alone = 0
        for i in range(len(position)):
            if position.count(position[i]) == 1:
                alone = alone + 1
        separations = len(set(position)) - 1
        if booksize > 1:
            if separations == 0:
                c.execute("UPDATE metrics SET passengers_separated = ?;", (separated+0,))
                conn.commit()
            elif separations > 0 and alone == 0:
                c.execute("UPDATE metrics SET passengers_separated = ?;", (separated+1,))
                conn.commit()
            else:
                c.execute("UPDATE metrics SET passengers_separated = ?;", (separated+3,))
                conn.commit()                    
    
    else:
        # Separation metric defined to be the number of group splits.
        separations = len(set(position)) - 1
        c.execute("UPDATE metrics SET passengers_separated = ?;", (separated+separations,))
        conn.commit()       
    
    conn.close()
    
    # Remove 'plane' array from storage
    del plane
    
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
        ASSIGN_metrics_list(DB_file, booking_name[i], int(booking_size[i]))
        free_seats = free_seats - int(booking_size[i])
