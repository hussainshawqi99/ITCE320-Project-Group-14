
import json
import re
import socket
import ssl

print(25 * "=" + "\nThe client has started\n"+25 * "=")

# Creating the client socket 

cs_ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('127.0.0.1', 5000)
error_msg = "Error"
selector = ""

# securing the socket with ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.load_cert_chain(certfile="localhost.crt", keyfile="localhost.key")
cs = context.wrap_socket(cs_ss)



# Function to split time and date

def time_Adjuster(Time):
    [date, time] = re.split('T', Time)
    time = time[0:5]
    return date, time

# Connecting to server and send user requests 

try:
    cs.connect(server_address)
    name = input("Enter a user name: ") # ask the client for a user name
    cs.send(name.encode("ascii"))

    while True:

        print("menu:\n1- Arrived flights\n2- Delayed flights\n3- Flight coming from a specific city\n4- Information about a particular fight\n5- Quit")

        # Request stage

        option = input("Select an option: ")
        if (option == '1') or (option == '2') or (option == '3') or (option == '4') or (option == '5') : #send option to server
            cs.send(option.encode("ascii"))


            if option == '1':           # receiving response from the server
                msg = cs.recv(1024).decode("ascii")
                if msg == error_msg:
                    print("No Record Found")
                else:
                    data = b""
                    while int(msg) - len(data) > 0: # to receive all data 
                        data += cs.recv(1024)
                    Result = json.loads(data.decode("ascii")) # return the data to original form

                    print("Arrived flights:") 
                    n = 0 # counter for flight numbers
                    for flight in Result:   # display the output in a formated way
                        n += 1
                        print('Flight {}: '.format(n))
                        print("*" * 20)
                        print("Flight Code: {}".format(flight["IATA"]))
                        print("Departure Airport: {}".format(flight["departure airport"]))

                        date, time = time_Adjuster(flight["arrival time"])
                        print("Arrival Date: {}\nArrival Time: {}".format(date,time))

                        print("Terminal: {}".format(flight["terminal"]))
                        print("Gate: {}".format(flight["gate"]))
                        print("*" * 20)

                    print("Total Number of flights : ", n)
            

            if  option == '2':  # receiving response from the server

                msg = cs.recv(1024).decode("ascii")
                if msg == error_msg:
                    print("No Record Found")

                else:
                    data = b""
                    while int(msg) - len(data) > 0: # to receive all data 
                        data += cs.recv(1024)
                    Result = json.loads(data.decode("ascii")) # return the data to original form

                    print("Delayed Flights:")
                    n = 0

                    for flight in Result: # display the output in a formated way
                        n += 1
                        print('Flight {}: '.format(n))
                        print("*" * 20)
                        print("Flight Code: {}".format(flight["IATA"]))
                        print("Departure Airport: {}".format(flight["departure airport"]))

                        date, time = time_Adjuster(flight["departure time"])
                        print("Departure Date: {}".format(date))
                        print("Estimated Time of Arrival: {}".format(time))

                        date, time = time_Adjuster(flight["estimated time arrival"])
                        print("Estimated Date of Arrival: {}\nEstimated Time of Arrival: {}".format(date,time))

                        print("Terminal: {}".format(flight["terminal"]))
                        print("Gate: {}".format(flight["gate"]))
                        print("*" * 20)
                    print("Total Number of flights : ", n)

            elif option == "3": # receiving response from the server
                city_name = input("Enter city name: ")
                cs.send(city_name.encode("ascii"))

                msg = cs.recv(1024).decode("ascii")
                if msg == error_msg:
                    print("Error (Wrong city name)")
                else:
                    data = b""
                    while int(msg) - len(data) > 0: # to receive all data 
                        data += cs.recv(1024)
                    Result = json.loads(data.decode("ascii")) # return the data to original form

                    print("Flight Information: ")

                    print("*" * 20)
                    print("Flight Code: {}".format(Result["IATA"])) # display the output in a formated way
                    print("Departure Airport: {}".format(Result["departure airport"]))

                    date, time = time_Adjuster(Result["departure time"])
                    print("Departure Date: {}\nDeparture Time: {}".format(date,time))
                        
                    date, time = time_Adjuster(Result["estimated time arrival"])
                    print("Estimated Date of Arrival: {}\nEstimated Time of Arrival: {}".format(date,time))

                    print("Terminal: {}".format(Result["terminal"]))
                    print("Gate: {}".format(Result["gate"]))
                    print("*" * 20)


                

                

            elif option == "4": # receiving response from the server
                Flight_No = input("Enter city name: ")
                cs.send(Flight_No.encode("ascii"))

                msg = cs.recv(1024).decode("ascii")
                if msg == error_msg:
                    print("Error (Wrong Flight number)")
                else:
                    data = b""
                    while int(msg) - len(data) > 0: # to receive all data 
                        data += cs.recv(1024)
                    Result = json.loads(data.decode("ascii")) # return the data to original form
                    print("Flight Information: ")   # display the output in a formated way
                    print("*" * 20)
                    print("Flight Code: {}".format(Result["IATA"]))
                    print("Date: {}".format(Result["DATE"]))

                    print("Departure Airport: {}\nDeparture Gate: {}\nDeparture Terminal: {}".format(Result["departure airport"],Result["departure gate"],Result["departure terminal"]))
                        
                    print("Arrival Airport: {}\nArrival Gate: {}\nArrival Terminal: {}".format(Result["arrival airport"],Result["arrival gate"],Result["arrival terminal"]))
                
                    print("Flight Status: {}".format(Result["status"]))
                    date, time = time_Adjuster(Result["departure time"])
                    print("Scheduled Departure Date: {}\nDeparture Time: {}".format(date,time))

                    date, time = time_Adjuster(Result["arrival time"])
                    print("Scheduled Arrival Date: {}\nArrival Time: {}".format(date,time))

                    date, time = time_Adjuster(Result["est arrival time"])
                    print("Estimated Date of Arrival: {}\nEstimated Time of Arrival: {}".format(date,time))

                    print("Delay: {}".format(Result["delay"]))
                    print("*" * 20)



            elif option == "5": # quit
                cs.send("Quit".encode("ascii"))
                print("Goodbye")
                break


        else:
            print("Invalid option")




except ConnectionError:
    print("An error has occured ")

cs.close()
