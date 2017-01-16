# Alternative ASSIGN function which allows the user to specify the separation
# metric interpretation they would prefer. The metric calculations included are:
#       Separated (default):  Number of group splits.
#       Alone:  Number of party members seated alone.
#       Dissatisfaction:  0 if all party members are seated together.
#                         1 if party members are separated but no individuals
#                             are sat alone.
#                         3 if one or more party members are sat alone.


def ASSIGN_metrics(db,bookname,booksize,sep = 'Separations'):
    # Connect to database and retrieve plane dimensions
    conn = sqlite3.connect(db)
    c = conn.cursor()
    rowcol = c.execute("SELECT * FROM rows_cols").fetchone()
    letters = str(rowcol[1])
    
    # Generate blank numpy array called plane that matches configuration
    plane = empty([rowcol[0],len(rowcol[1])],dtype='S50')
    for i in range(rowcol[0]):
        for j in range(len(rowcol[1])):
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
            for j in range(len(rowcol[1])):
                if str(i+1) == str(r[k]) and letters[j] == str(s[k]):
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
                for j in range(len(rowcol[1])):
                    if plane[i,j] == '':
                        plane[i,j:j+remain] = bookname
                        for k in range(remain):
                            c.execute("UPDATE seating SET name = ? WHERE row = ? AND seat = ?;", (bookname,i+1,letters[j+k],))
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
        for j in range(len(rowcol[1])):
            if plane[i,j] == bookname:
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
