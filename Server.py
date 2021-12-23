
import json
import requests
import socket
import threading
import ssl

server_address = ('127.0.0.1', 5000)
error_msg = "Error"

Clients_Online = []  # list of clients that are online

access_key = 'a63371f0cd47a6b9e0ad71a11167b08b' #access key for api

# securing the socket wirt ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1) 
context.load_cert_chain(certfile="localhost.crt", keyfile="localhost.key")
# Ask for airport code arr_icao

Airport_code = input("Enter Airport Code: ")
print("Requesting Flight Record ..... ")

All_flights = []
Arrival_flights = []
Delayed_flights = []

# Reterive flights info
# Reterive arrived flights info
params = {'access_key': access_key,'arr_icao': Airport_code,'flight_status':"landed"}
api_result = requests.get('http://api.aviationstack.com/v1/flights', params)
flights = api_result.json()
Arrival_flights = flights["data"]

# Reterive delayed flights info
params = {'access_key': access_key,'arr_icao': Airport_code,'min_delay_arr':1}
api_result = requests.get('http://api.aviationstack.com/v1/flights', params)
flights = api_result.json()
Delayed_flights = flights["data"]


All_flights = Arrival_flights + Delayed_flights

print("Flight Records Received")

# Store the reterived data in a json file

with open("group_14.json","w") as f:
    json.dump(All_flights,f)

# Function for each option

def option_1():
    result = {"IATA":"","departure airport":"","arrival time":"","terminal":"","gate":""}
    Flights = []
    for flight in Arrival_flights:
        result["IATA"]= flight['flight']['iata']
        result["departure airport"]= flight['departure']['airport']
        result["arrival time"]= flight['arrival']['actual']
        result["terminal"]= flight['arrival']['terminal']
        result["gate"]=flight['arrival']['gate']
        Flights.append(result)

    return Flights

def option_2():
    result = {"IATA":"","departure airport":"","departure time":"","estimated time arrival":"","terminal":"","gate":""}
    Flights = []
    for flight in Delayed_flights:
        result["IATA"]= flight['flight']['iata']
        result["departure airport"]= flight['departure']['airport']
        result["departure time"]= flight['departure']['actual']
        result["estimated time arrival"]= flight['arrival']['estimated']
        result["terminal"]= flight['arrival']['terminal']
        result["gate"]=flight['arrival']['gate']
        Flights.append(result)

    return Flights

def option_3(City_name):
    result = {"IATA":"","departure airport":"","departure time":"","estimated time arrival":"","terminal":"","gate":""}
    for flight in All_flights:
        if flight["departure"]["airport"] == City_name: # checks info only for specific city
           result["IATA"] = flight['flight']['iata']
           result["departure airport"] = flight['departure']['airport']
           result["departure time"] = flight['departure']['actual']
           result["estimated time arrival"] = flight['arrival']['estimated']
           result["terminal"] = flight['arrival']['terminal']
           result["gate"] = flight['arrival']['gate']
           return result 
    return False

def option_4(Flight_No):
    result = {"IATA":"","DATE":"","departure airport":"","departure gate":"","departure terminal":"","arrival airport":"","arrival gate":"","arrival terminal":"","status":"","departure time":"","arrival time":"","est arrival time":"","delay":""}
    for flight in All_flights:
        if flight["flight"]["number"] == Flight_No: # checks info only for a specific flight no.
           result["IATA"] = flight['flight']['iata']
           result["DATE"] = flight['flight_date']

           result["departure airport"] = flight['departure']['airport']
           result["departure gate"] = flight['departure']['gate']
           result["departure terminal"] = flight['departure']['terminal']

           result["arrival airport"] = flight['arrival']['airport']
           result["arrival gate"] = flight['arrival']['gate']
           result["arrival terminal"] = flight['arrival']['terminal']

           result["status"] = flight['flight_status']
           result["departure time"] = flight['departure']['scheduled']
           result["arrival time"] = flight['arrival']['scheduled']
           result["est arrival time"] = flight['arrival']['estimated']
           result["delay"] = flight['arrival']['delay']
           return result

# Function for assigning data from the database for each option(database from option functions)


# thread to be used by client

def thread_code (sock, id):
    try:
        client_name = sock.recv(1024).decode('ascii')
        user = {"name":client_name, "ID":id}

        Clients_Online.append(user)
        threading.currentThread().setName(client_name)
        print("[CONNECTED] Client ({}) - ID = {}".format(threading.currentThread().getName(), id))

        # receive the option from client and send the result
        while True:
            option = sock.recv(1024).decode('ascii')
            if(option == "5"):
                break

            print("[{}.{}] has requested option {}".format(client_name,id,option))


            # searching according to the option
            if (option == '1'):
                search_result = option_1()

            elif (option == '2'):
                search_result = option_2()

            elif (option == '3'):
                City_name = sock.recv(1024).decode('ascii')
                search_result = option_3(City_name)

            elif (option == '4'):
                Flight_No = sock.recv(1024).decode('ascii')
                search_result = option_4(Flight_No)


            if(search_result):
                data = json.dumps(search_result)
                msg_size = len(data)
                sock.send(str(msg_size).encode("ascii"))
                sock.sendall(data.encode("ascii"))
            else:
                sock.send(error_msg.encode("ascii"))

    except ConnectionError:
        print("something went wrong with the connection") 


    print("{} client with id:{} have left the Server".format(client_name,id))
    Clients_Online.remove(user) # removing client from online after it left

    if(len(Clients_Online) > 0): # printing online client
        print("\nClients Online: ",Clients_Online)
    else:
        print("All clients left")

# Main

sock_p = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creating the server sockect and binding server port
sock_p.bind(server_address)  
sock_p.listen(3)

# starting the thread

while True:
    try:
        ssl_cs, sockname = sock_p.accept()
        sock = context.wrap_socket(ssl_cs, server_side=True)
        t = threading.Thread(target=thread_code, args=(sock, len(Clients_Online)+1))
        t.start()
    except socket.error:
        print("something went wrong with the socket")
        break


print("All users logged off")
print(10*"*", "Server off", 10*"*")

sock.close()