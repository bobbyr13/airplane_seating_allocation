# The run_all function combines readDB, readCSV, ASSIGN_metrics_list and the 
# concluding for loop. It assumes that all functions, including count_list, 
# count_str_list have been defined already. User is able to specify the starting
# row number and end row number of the bookings file to run. By default, the 
# entire bookings list will be run, however it gives the user greater control.
# The interpretation of the separations metric can also be set, with the
# default being the number of group separations.


def run_all(DB_file,CSV_file,sep='Separations',first=1,last=0):
    nrows, seat_layout, free_seats = readDB(DB_file)
    booking_number, booking_name, booking_size = readCSV(CSV_file)
    
    start = first - 1
    if last == 0 or last == booking_number:
        end = booking_number
    else:
        end = last
    
    
    for i in range(start,end):
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
            ASSIGN_metrics_list(DB_file, booking_name[i], int(booking_size[i]), sep)
            free_seats = free_seats - int(booking_size[i])



# Sample function call to run the first 10 rows of the bookings.csv file and
# using the 'number of passengers sat alone' interpretation of the metric

run_all('airline_seating.db','bookings.csv','Alone',1,10)