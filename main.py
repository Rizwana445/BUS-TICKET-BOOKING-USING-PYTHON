import mysql.connector
from datetime import datetime, time
import random
import string
import tour_places  # Assuming tour_places module is correctly defined and imported

# Establish database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="booking"
)
mycursor = mydb.cursor()

distances = []

def generate_distance(choice):
    distance_map = {
        1: 500,
        2: 400,
        3: 300,
        4: 250,
        5: 350,
        6: 450,
        7: 600,
        8: 500,
        9: 350
    }
    if choice in distance_map:
        if not distances or choice == 9:
            distance = distance_map[choice]
            if distances and choice == 9:
                distance = distances[-1] + 1
            distances.append(distance)
            return distance
    return "Invalid choice"

def insert_userdata():
    try:
        sql = "INSERT INTO passenger_details (passenger_name, source, destination, date_of_journey, bus_type, mobile_no, email_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        passenger_name = input("Enter passenger name: ")
        source = input("Enter source: ")
        destination = input("Enter destination: ")
        date_of_journey_str = input("Enter date of journey (YYYY-MM-DD): ")
        bus_type = input("Enter bus type: ")
        mobile_no = input("Enter mobile no: ")  # Assuming mobile_no is stored as a string in the database
        email_id = input("Enter email id: ")
        try:
            date_of_journey = datetime.strptime(date_of_journey_str, '%Y-%m-%d').date()
        except ValueError:
            print("Incorrect date format, should be YYYY-MM-DD")
            return
        val = (passenger_name, source, destination, date_of_journey, bus_type, mobile_no, email_id)
        mycursor.execute(sql, val)
        mydb.commit()  # Committing the transaction
        print("Data saved successfully")
        # Generate bill after successful data insertion
        generate_bill(passenger_name, source, destination, date_of_journey, bus_type, mobile_no, email_id)
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def generate_bus_number():
    """Generate a random bus number."""
    prefix = "TN"  # Assuming TN as the state code
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))  # Generate 8 random characters/digits
    return f"{prefix}{suffix}"

def generate_random_time():
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)
    return time(hours, minutes, seconds).strftime('%H:%M:%S')

def calculate_total_bill(source, destination, bus_type):
    base_fare = 200  # Base fare amount
    # Define distances between sources and destinations (hypothetical values)
    distances = {
        ("Ooty", "Chennai"): 500,
        ("Kodaikanal", "Chennai"): 400,
        ("Madurai", "Ooty"): 300,
        ("Chennai", "Yercaud"): 250,
        ("Coimbatore", "Puducherry"): 350,
        ("Palani", "Chennai"): 450,
        ("Puducherry", "Kodaikanal"): 600,
        ("Yercaud", "Coimbatore"): 500,
        ("Yelagiri", "Chennai"): 350
    }
    # User chooses the method to generate distance
    print("1. Fixed distance value of 500")
    print("2. Generate next distance value in the sequence")
    choice = int(input("Enter your choice (1-9): "))
    distance_charge = generate_distance(choice)
    distance_factor = 10  # Example per kilometer charged

    def get_distance(city1, city2):
        if (city1, city2) in distances:
            return distances[(city1, city2)]
        else:
            return distance_charge

    def calculate_total_fare(base_fare, bus_type, source, destination, distances):
        distance = get_distance(source, destination)
        if bus_type == "deluxe":
            bus_type_factor = 1.5
        elif bus_type == "ac":
            bus_type_factor = 1.3
        elif bus_type == "sleeper":
            bus_type_factor = 1.1
        else:
            bus_type_factor = 1.0
        distance_charge = distance * distance_factor
        bus_type_charge = base_fare * bus_type_factor
        total_without_gst = base_fare + distance_charge + bus_type_charge
        return total_without_gst, distance, distance_charge

    total_without_gst, distance, distance_charge = calculate_total_fare(base_fare, bus_type, source, destination, distances)
    gst_rate = 0.18
    gst_amount = total_without_gst * gst_rate
    total_with_gst = total_without_gst + gst_amount + distance_charge
    return total_without_gst, gst_amount, total_with_gst, distance, distance_charge

def generate_bill(passenger_name, source, destination, date_of_journey, bus_type, mobile_no, email_id):
    try:
        total_without_gst, gst_amount, total_with_gst, distance, distance_charge = calculate_total_bill(source, destination, bus_type)
        if total_without_gst is not None:
            print(f"Base Fare: {total_without_gst:.2f}")
            print(f"Distance: {distance} km")
            print(f"Distance Charge: {distance_charge:.2f}")
            print(f"GST (18%): {gst_amount:.2f}")
            print(f"Total Bill: {total_with_gst:.2f}")
            with open("bill.txt", "a") as f:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"Passenger Name: {passenger_name}\n")
                f.write(f"Source: {source}\n")
                f.write(f"Destination: {destination}\n")
                f.write(f"Date of Journey: {date_of_journey}\n")
                f.write(f"Bus Type: {bus_type}\n")
                f.write(f"Mobile No: {mobile_no}\n")
                f.write(f"Email ID: {email_id}\n")
                f.write(f"Base Fare: {total_without_gst:.2f}\n")
                f.write(f"Distance: {distance} km\n")
                f.write(f"Distance Charge: {distance_charge:.2f}\n")
                f.write(f"GST (18%): {gst_amount:.2f}\n")
                f.write(f"Total Bill: {total_with_gst:.2f}\n")
                f.write(f"Bill generated at: {current_time}\n\n")
            print("Bill generated successfully.")
        else:
            print("Error generating bill due to invalid fare or GST rate input.")
    except Exception as e:
        print(f"Error generating bill: {e}")

def bus_details():
    try:
        bus_name = "PARVEEN TRAVELS"
        bus_no = generate_bus_number()
        bus_timing = generate_random_time()
        sql = "INSERT INTO buses (bus_name, bus_timing, bus_number) VALUES (%s, %s, %s)"
        val = (bus_name, bus_timing, bus_no)
        mycursor.execute(sql, val)
        mydb.commit()
        print("Bus details saved successfully")
        print("THANK YOU FOR BOOKING OUR TICKETS IN PARVEEN TRAVELS")
        print("HAPPY JOURNEY & HOPE YOU MAKE MILLIONS OF AMAZING MEMORIES")
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    except Exception as e:
        print(f"Error in bus_details: {e}")

def tour_place_details():  # available source and destination buses
    try:
        print("Available Tours:")
        print("1. Ooty to Chennai")
        print("2. Kodaikanal to Chennai")
        print("3. Madurai to Ooty")
        print("4. Chennai to Yercaud")
        print("5. Coimbatore to Puducherry")
        print("6. Palani to Chennai")
        print("7. Puducherry to Kodaikanal")
        print("8. Yercaud to Coimbatore")
        print("9. Yelagiri to Chennai")
        user_choice = int(input("Enter your choice (1-9): "))
        bus_available = input("Is the bus available? (yes/no): ").lower()
        if bus_available == "yes":
            print("The bus is available")
        elif bus_available == "no":
            print("Bus is not available.")
        else:
            print("Invalid input. Assuming bus is not available.")
        if user_choice == 1:
            tour_places.ooty_to_chennai()
            insert_userdata()
            bus_details()
        elif user_choice == 2:
            tour_places.kodaikanal_to_chennai()
            insert_userdata()
            bus_details()
        elif user_choice == 3:
            tour_places.madurai_to_ooty()
            insert_userdata()
            bus_details()
        elif user_choice == 4:
            tour_places.chennai_to_yercaud()
            insert_userdata()
            bus_details()
        elif user_choice == 5:
            tour_places.coimbatore_to_puducherry()
            insert_userdata()
            bus_details()
        elif user_choice == 6:
            tour_places.palani_to_chennai()
            insert_userdata()
            bus_details()
        elif user_choice == 7:
            tour_places.puducherry_to_kodaikanal()
            insert_userdata()
            bus_details()
        elif user_choice == 8:
            tour_places.yercaud_to_coimbatore()
            insert_userdata()
            bus_details()
        elif user_choice == 9:
            tour_places.yelagiri_to_chennai()
            insert_userdata()
            bus_details()
        else:
            print("Invalid choice")
    except ValueError:
        print("Not available for this source and destination buses. Please enter the available source and destination bus.")

tour_place_details()
# Close the database connection
mycursor.close()
mydb.close()






