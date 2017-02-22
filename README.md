# ARI Programming - Report

#### MIS40750 - Analytics Research & Implementation
  
  ----
  

## Contributors:
  
| *Student*       | *ID Number*   |
|:---------------:|:-------------:|
| Eoin Carroll    | 16202781      | 
| Bobby Reardon   | 13203828      |
| Chris Taylor    | 13368376      |

  
## Statement of Authorship

We declare that all of the undersigned have contributed to this work and that it is all our own work as understood by UCD policies on Academic Integrity and Plagiarism, unless otherwise cited.
  
  
## Contribution by Team Member:


Eoin Carroll:   
                
- read_database
				        
- read_csv
				        
- run_all
				        
- Report sections: 1,3,5,8

Bobby Reardon:  
                
- count_list
				        
- count_str_list
				        
- assign_metrics_list
				        
- run_all
				        
- Report sections: 2,4,7,9,editing

Chris Taylor:   

- SeatsTest
				        
- code editing & annotating
				        
- Report sections: 6

<br><br>

  ----

# REPORT
  
  ----

###  Contents:
  
1. **INTRODUCTION**
2. **CODING ASSUMPTIONS**
  1. Rectangular Plane
  2. Ignoring Aisles
  3. Existing Bookings
  4. Passengers Separated Metric
  5. Priority of Bookings
  6. Database Ordering
  7. First Come First Served
  8. Bookings with Same Name
3. **CODING STRUCTURE**
  1. Run Time & Machine Resources
  2. Robustness
  3. Simplicity
4. **DESCRIPTION OF USER COMMANDS**
5. **TROUBLESHOOTING**
6. **TESTING**
  * def test_count_list(self)
  * def test_count_str_list(self)
  * def test_read_database(self) def test_read_csv(self)
  * def test_assign_metrics_list(self)
7. **REMAINING ISSUES**
8. **CONCLUSION**
9. **FUNCTION DOCUMENTATION**
  * count_str_list
  * count_list
  * assign_metrics_list
  * run_all
  * read_database
  * read_csv
  


### 1. INTRODUCTION
  
   This assignment simulates a real world problem of an airline seating system. It was required of us to write a python program to read a plane's seating layout from an SQL database, take a CSV list of booking information and then implement an algorithm to seat as many passengers as possible while separating as few booking groups as possible. The assignment had a number of required outputs saved to an SQL database - the booking names in each seat, number of passengers rejected and number of groups separated.  
   
   A program was successfully created that meets the assignment brief in a team of three. This document is a record of the thought process in creating the program, the approach taken, the obstacles overcome, the testing performed and a conclusion that relates back to the learning outcomes. The appendix includes detail user documentation for each function.  
   
   
### 2. ASSUMPTIONS

   Due to the variety of factors and scenarios to be accounted for when developing the program, several assumptions were made to overcome them or to simplify the functionality. What follows are a list of the main assumptions made by the program and any changes made to remove them, beginning with the shape of the plane.  
   
   **2.1 Rectangular plane:**   Based on the row_cols table of the sample database and to increase the simplicity of the model, it was assumed that the seat layout would be rectangular and wouldn’t include the possibility of rows with fewer/more seats than others. Figure 1 overleaf shows the plane layout generated from the sample database.  
   
   **2.2 Ignoring Aisles:**   The sample database gave no information about the location of aisle(s) on the plane. This could be an issue for planes with a high number of seats per row as there would be several possible configurations. Hence, in order to generalise for all planes, the aisles were taken to be irrelevant with regard to splitting passengers. As a result, a couple assigned to the seats 3C and 3D, as per the red group in figure 1, would be considered in the model to be beside each other and not separated.  
  
   **2.3 Existing Bookings:**   Initially our program was designed such that it assumed no bookings existed prior to running the algorithm. However, this has been corrected and the program now adapts to this situation. In the sample database, seats 1A and 1C were already assigned to Donald Trump and Hillary Clinton respectively, as seen in the blue seats in figure 1. As a result, our algorithm assigns the remaining 58 seats to passengers in the bookings CSV file. However, a further assumption still being made is that the existing bookings are not spaced out and if they are in different rows, they at least operate from left to right (A → F) in each row.  
   
   **2.4 Passengers Separated Metric:**   The definition provided for this metric is “a number representing how many passengers are seated away from any other member of their party”. Following discussion of how this should be interpreted, we assumed by default that this metric should represent the total number of passengers in a booking, if that booking has been split at all. In this case, the red group would lead to an increase of 0, while the yellow and green groups would increase the metric by 6 and 7 respectively. However, the model has been adapted to take in user specified interpretations. The alternatives for this metric are the Alone, Separated and Dissatisfaction metrics. The Alone interpretation increases the metric by the number of passengers in a booking who get seated completely alone from the rest of their party. In this case, the green group would lead to an increase of 0, while the yellow group would increase the metric by 1. Next is the Separated metric which counts the total number of group separations. Under this interpretation, the metric would be increased by 1 for the green booking in figure 1 and increased by 2 for the yellow group. The Dissatisfaction metric is an alternative measure which applies a football metric approach. The metric is increased by 1 in a situation where a group has been separated but no passenger is alone (such as the green group). This is irrelevant of how many splits there are. If one or more passengers in a group are sitting entirely alone (such as in the yellow group) then the metric is increased by 3, thus penalising separations of this kind more heavily. These interpretations can be called by the user by setting the sep parameter to Total (default), Alone, Separated or Dissatisfaction as required.

   **2.5 Priority of Bookings:**   It was intuitively assumed that the bookings should be processed in order of the rows in the provided CSV file. It can be modified however as the program can take inputs for the first and last rows to be processed in a single run of the program. This allows for the user to run the program for a block of bookings in isolation, e.g. bookings 10 through 20. Further information about these parameters are included in the function documentation.  
   
   **2.6 Database Ordering:**   Initially the algorithm was designed in such a way that it assumed the ordering of the rows in the seating table of the database would be the same for any other databases tested. However, this assumption has been corrected as it now identifies seats by row and seat number and hence, it is independent of the original order of database tables.  
   
   **2.7 First Come First Served:**   Unlike a lot of booking systems which intentionally disallow bookings that would result in a single seat being left alone, our program proceeds anyway. As a result, a booking of two people will be accommodated in a row with three free seats, ignoring the fact that this isolates a seat. This simplifies the seat assigning process, but doesn’t create many problems due to the large number of bookings of size 1 which will fill those places. It does however work in a greedy front to back manner, and will place the two person booking in the three seats, even when rows further back might have even numbers of seats available.  
   
   **2.8 Bookings with Same Name:**   Initially the algorithm wasn’t able to deal with multiple bookings of the same name and assumed this would not occur. However, it is no longer assumed to be the case. Should a booking be assigned with the name “Donald Trump”, the same as the existing booking for seat 1A in figure 1, the booking name is modified to “Donald Trump (1)” and processed. Further bookings of the same name will be changed to “Donald Trump (1) (1)” and so on.
