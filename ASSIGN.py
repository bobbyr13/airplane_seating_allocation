# Function creates array names 'plane' in order to easily iterate through the
# occupied and empty seats. This array is not returned and as a result, is 
# never stored in the main programme environment.
#
# Remaining issues to resolve are highlighted in the code body.


def ASSIGN(db,bookname,booksize):
    # Connect to database and retrieve plane dimensions
    conn = sqlite3.connect(db)
    c = conn.cursor()
    rowcol = c.execute("SELECT * FROM rows_cols").fetchone()
    letters = str(rowcol[1])
    
    # Generate blank numpy array called plane that matches configuration
    plane = empty([rowcol[0],len(rowcol[1])],dtype='S50')
    for i in range(rowcol[0]):
        for j in range(rowcol[1]):
            plane[i,j] = ''
    
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
            for j in range(rowcol[1]):
                if str(i) == str(r[k]) and letters[j] == str(s[k]):
                    plane[i,j] = str(occupied[k][2])
    
    # Main assign step for new booking. System operates by trying to fit the
    # largest possible group together in one row, each time scanning rows from
    # front to back. Functions 'count' and 'count_str' are already uploaded in
    # local array method branch. Assigning step assumes all seats are booked and
    # then allocated in a left-to-right manner with no gaps within a given row.
    remain = booksize
    dummy = 0
    while count_str(plane,bookname) < booksize:
        current = count_str(plane,bookname)
        for i in range(rowcol[0]):
            if count(plane,i) >= remain:
                for j in range(rowcol[1]):
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
        for j in range(rowcol[1]):
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
   
