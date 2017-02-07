# ARIProgramming
MIS40750 Analytics Research & Implement

ARI Programming Assignment - Airline Seating

Note: Please see the included report for detailed documentation.



Assumptions:
-------------------------------------------------
Passengers seperated metric (by default) is how many times we split the group, but this can be alterted

Aisles are irrelevant and thus do not count as separating groups

Rectangular seating plan - will only be two variables (rows and seat plan) 

Assign algorithm assumes that the existing seat bookings don't have spaces in between them in a given row

Database file seat letter are ordered alphabetically - seat row is not important

Priority is given based on the order of bookings in CSV file, regardless of whether this results in empty seats



Errors/Unforseen Outcomes:
-------------------------------------------------
Entering 9 as group size resulted in 3 rows of 4 for some reason  -  corrected

Database kept locking  -  corrected

Initial plan was to use array - now modified to work with lists  -  corrected




To Do:
-------------------------------------------------
Create list based modification  -  done

Create a list of test cases - done

Correct spacing assumption - done

Create a list of optional additions/parameters  -  choice of metric interpretation added

Annotate all functions that are not obvious - done
