# ARIProgramming
ARI Programming Assignment - Airline Seating




Assumptions:
Sperated metric is how many times we split the group,
Aisles are irrelevant,
Rectangular seating plan - will only be two variables (rows and seat plan),

Questions:
Will there be names in the database before starting?

Errors/Unforseen outcomes:
Entering 9 as group size resulted in 3 rows of 4 for some reason



Have a look through, the program is laid out like this:
------------------------------------------------------------------

readDB #read plane seating parameters - return (nrows, seat_layout, free_seats)
readCSV #read in booking list - return (number of bookings, booking_name[], booking_size[])
def seat #seat individual booking when required (Bobbys magic goes here)

for i in range(number of bookings):
    if free_seats == 0:
        increase db count passengers refused by booking_size[i]        
        
    elif booking_size > free_seats:
        increase db count passengers refused by booking_size[i]        

    else:
        seat(booking_name[i], booking_size[i])
