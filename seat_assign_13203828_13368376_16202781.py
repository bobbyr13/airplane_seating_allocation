import sqlite3
import csv
import pandas as pd
from pandas import read_csv
from pandas import Series, DataFrame


def count_list(plane_list, row_length, i):                                # Count number of free seats in row i of plane
    running_count = 0

    for j in range(row_length):

        if plane_list[int(j * (len(plane_list) / row_length) + i)] == '':
            running_count += 1

    return running_count


def count_str_list(plane_list, string):                                                    # Count names in entire plane
    running_count = 0

    for i in range(len(plane_list)):

        if plane_list[i] == string:
            running_count += 1

    return running_count


def read_database(db_file="airline_seating.db"):        # Read and return seat layout. Return number of unoccupied seats

    conn = sqlite3.connect(db_file)                                                                       # Open db file
    c = conn.cursor()
    number_of_rows = c.execute("SELECT * FROM rows_cols;").fetchone()[0]                           # read amount of rows
    seat_layout = str(c.execute("SELECT * FROM rows_cols;").fetchone()[1])                            # read seat layout
    seats_column = c.execute("SELECT name FROM seating;").fetchall()                  # read column of seated passengers

    free_seats = 0

    for row in range(number_of_rows * len(seat_layout)):                                              # Go through range

        if seats_column[row] == ('',):                               # if seat is empty, increase free seat count by one
            free_seats += 1

    c.close()
    conn.close()

    return number_of_rows, seat_layout, free_seats


def read_csv(csv_file="bookings.csv"):                                 # Read and return CSV file and number of bookings
                                                        # Not ideal as this could use a lot of memory for a big CSV file
                                                                                # Need to change this to read one by one

    with open(csv_file, 'r') as passenger_file:
        booking_list = csv.reader(passenger_file)
        booking_number = 0
        booking_name = []
        booking_size = []

        for row in booking_list:
            booking_name.append(row[0])
            booking_size.append(row[1])
            booking_number += 1

    passenger_file.close()
    # print(booking_number, booking_name, booking_size)
    # If error or reached end of file, booking_name = False

    return booking_number, booking_name, booking_size


# New ASSIGN function which allows the user to specify the separation metric
# interpretation they would prefer. The metric calculations included are:
#       Separated (default):  Number of group splits.
#       Alone:  Number of party members seated alone.
#       Total:  If group is split, number of members in group.
#       Dissatisfaction:  0 if all party members are seated together.
#                         1 if party members are separated but no individuals
#                             are sat alone.
#                         3 if one or more party members are sat alone.


def assign_metrics_list(db, booking_name, booking_size, sep='Separations'):
                                                                    # Connect to database and retrieve plane dimensions
    conn = sqlite3.connect(db)
    c = conn.cursor()
    row_col = c.execute("SELECT * FROM rows_cols").fetchone()
    letters = str(row_col[1])
                                                    # Retrieve bookings currently in the database and assign them to the
                                                                                # corresponding seats in the list plane
    plane = []
    occupied = c.execute("SELECT * FROM seating WHERE name != '%s'" % '').fetchall()
    r = []
    s = []

    for i in range(len(occupied)):
        r.append(occupied[i][0])
        s.append(occupied[i][1])

    for j in range(len(row_col[1])):

        for i in range(row_col[0]):
            x = len(plane)

            for k in range(len(r)):

                if str(i + 1) == str(r[k]) and letters[j] == str(s[k]):
                    plane.append(str(occupied[k][2]))

            if len(plane) == x:
                plane.append('')

    # Main assign step for new booking. System operates by trying to fit the
    # largest possible group together in one row, each time scanning rows from
    # front to back. Functions 'count' and 'count_str' are already uploaded in
    # local array method branch. Assigning step assumes all seats are booked and
    # then allocated in a left-to-right manner with no gaps within a given row.

    while count_str_list(plane,booking_name) > 0:                          # Avoid issue of multiple bookings with same booking name
        booking_name += ' (1)'
      
    remain = booking_size
    dummy = 0

    while count_str_list(plane, booking_name) < booking_size:
        current = count_str_list(plane, booking_name)

        for i in range(row_col[0]):

            if count_list(plane, len(letters), i) >= remain:

                for j in range(len(row_col[1])):

                    if plane[j * row_col[0] + i] == '':

                        for k in range(remain):
                            plane[(j + k) * row_col[0] + i] = booking_name
                            c.execute("UPDATE seating SET name = ? WHERE row = ? AND seat = ?;",
                                      (booking_name, i + 1, letters[j + k],))
                            conn.commit()                                         # update database with booking details
                        break
                break

        if count_str_list(plane, booking_name) > current:
            remain = dummy
            dummy = 0

        else:
            remain -= 1
            dummy += 1
                                                                        # Fetch the current value of separation metric
    metrics = c.execute("SELECT * FROM metrics").fetchall()
    separated = metrics[0][1]

    position = []                                               # Generate list of row numbers for newly allocated seats

    for i in range(row_col[0]):

        for j in range(len(row_col[1])):

            if plane[j * row_col[0] + i] == booking_name:
                position.append(i)

    if sep == 'Alone':                      # Separation metric defined to be the number of party members seated alone.
        alone = 0

        for i in range(len(position)):

            if position.count(position[i]) == 1:
                alone += 1

        if booking_size > 1:
            c.execute("UPDATE metrics SET passengers_separated = ?;", (separated + alone,))
            conn.commit()

    elif sep == 'Dissatisfaction':

        # Separation metric for a given booking defined to be:
        # 0 if all party members are seated together.
        # 1 if party members are separated but no individuals are sat alone.
        # 3 if one or more party members are sat alone.

        alone = 0
        for i in range(len(position)):

            if position.count(position[i]) == 1:
                alone += 1

        separations = len(set(position)) - 1

        if booking_size > 1:
            if separations == 0:
                c.execute("UPDATE metrics SET passengers_separated = ?;", (separated + 0,))
                conn.commit()

            elif separations > 0 and alone == 0:
                c.execute("UPDATE metrics SET passengers_separated = ?;", (separated + 1,))
                conn.commit()

            else:
                c.execute("UPDATE metrics SET passengers_separated = ?;", (separated + 3,))
                conn.commit()
    
    elif sep == 'Total':                            # Separation metric defined to be the size of a party that is split.
        alone = 0

        for i in range(len(position)):

            if position.count(position[i]) == 1:
                alone += 1

        if booking_size > 1:
            c.execute("UPDATE metrics SET passengers_separated = ?;", (separated + booking_size,))
            conn.commit()
           
    else:
                                                        # Separation metric defined to be the number of group splits.
        separations = len(set(position)) - 1
        c.execute("UPDATE metrics SET passengers_separated = ?;", (separated + separations,))
        conn.commit()

    conn.close()
                                                                                    # Remove 'plane' array from storage
    del plane


def run_all(DB_file = "airline_seating.db",CSV_file = "bookings.csv",sep = 'Separated',first=1,last=0):
    nrows, seat_layout, free_seats = read_database(DB_file)
    booking_number, booking_name, booking_size = read_csv(CSV_file)
    
    start = first - 1
    if last == 0 or last == booking_number:
        end = booking_number
    else:
        end = last
    
    X = pd.DataFrame.from_csv('bookings.csv', header= None, index_col = None)
    X.columns = ['Name','Size']
    status = ['']*booking_number
    X['Status'] = status
    
    for i in range(start,end):
        if free_seats == 0:
            #increase db count passengers refused by booking_size        
            conn = sqlite3.connect(DB_file)
            c = conn.cursor()
            passengers_refused = c.execute("SELECT * FROM metrics;").fetchone()[0]    
            passengers_refused += int(booking_size[i])
            c.execute("UPDATE metrics SET passengers_refused = ?;", (passengers_refused,))
            conn.commit()
            c.close()
            conn.close()
            X.set_value(i, 'Status', 'Refused - No Seats Left')
            
        elif int(booking_size[i]) > free_seats: #If we cannot accomodate the booking
            #increase db count passengers refused by booking_size        
            conn = sqlite3.connect(DB_file)
            c = conn.cursor()
            passengers_refused = c.execute("SELECT * FROM metrics;").fetchone()[0]    
            passengers_refused += int(booking_size[i])
            c.execute("UPDATE metrics SET passengers_refused = ?;", (passengers_refused,))
            conn.commit()
            c.close()
            conn.close()
            X.set_value(i, 'Status', 'Refused - Not Enough Seats Left')
    
        else:
            assign_metrics_list(DB_file, booking_name[i], int(booking_size[i]), sep)
            free_seats = free_seats - int(booking_size[i])
            X.set_value(i, 'Status', 'Booking Confirmed')
    
    print(X)


run_all()



