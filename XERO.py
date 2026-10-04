import time
import random

print("Launching XERO...")
time.sleep(0.5)
print("Loading modules...")
time.sleep(0.5)
print("Initializing system...")
time.sleep(1)

print("System ready.")
time.sleep(0.5)
print(".")
time.sleep(0.5)
print("..")
time.sleep(0.5)
print("...")
time.sleep(0.5)
print("Warning : XERO.inc doesn't held responsiple for any damage caused by the use of this program.")
time.sleep(0.5)

print("Welcome to XERO, the ultimate AI assistant.")
time.sleep(0.5)

menu = True
while menu == True:
    action = input("What would you like to do? (Type 'help' for options): ").lower()

    if action == "help":
        print("Here are some things you can do:")
        print("- 'joke': Get a random joke.")
        print("- 'quote': Get an inspirational quote.")
        print("- 'time': Get the current time.")
        print("- 'tech': Get the latest tech news.")
        print("- 'weather': Get the current weather for a specific location.")
        print("- 'admin': Show admin options.")
        print("- 'help': Show this help message.")
        print("- 'exit': Exit the program.")

    if action == "joke":
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why did the bicycle fall over? Because it was two-tired!"
            "Why did the math book look sad? Because it had too many problems!"
            "Why did the computer go to the doctor? Because it had a virus!"
        ]
        print("\n" + random.choice(jokes) + "\n")

    if action == "quote":
        quotes = [
            "The best way to predict the future is to invent it. - Alan Kay",
            "Life is 10% what happens to us and 90% how we react to it. - Charles R. Swindoll",
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill"
            "Believe you can and you're halfway there. - Theodore Roosevelt"
        ]
        print("\n" + random.choice(quotes) + "\n")

    if action == "exit":
        print("Exiting XERO...")
        time.sleep(1)
        print("Goodbye!")
        menu = False

    if action == "time":
        current_time = time.strftime("%H:%M:%S")
        print(f"\nThe current time is: {current_time}\n")

    if action == "tech":
        print("\nFetching the latest tech news...")
        time.sleep(1)
        print("Here are some recent tech headlines:")
        print("- Apple announces new iPhone 15 with groundbreaking features.")
        print("- Google unveils AI-powered search enhancements.")
        print("- Microsoft releases Windows 12 with improved security and performance.")
        print("- Tesla's new self-driving software update is now available.")
        print("- Amazon introduces drone delivery service in select cities.\n")

    if action == "weather":
        location = input("Enter a location (city name) \nOnly 'New York City', 'Los Angeles', 'Chicago', 'Houston', and 'Miami' are supported \n : ")
        print(f"\nFetching weather for {location}...")
        time.sleep(1)
        print("Please note that the weather data may be incorrect\n")
        
        weather_data = {
            "New York": "Sunny, 75°F",
            "Los Angeles": "Cloudy, 68°F",
            "Chicago": "Rainy, 60°F",
            "Houston": "Thunderstorms, 80°F",
            "Miami": "Hot and humid, 90°F"
        }
        weather_info = weather_data.get(location.title(), "Weather data not available for this location.")
        print(f"Current weather in {location.title()}: {weather_info}\n")

    if action == "admin":  
        print("\nAdmin access required.") 
        password = input("Enter admin password: ")
        if password == "XeroAdmin26":
            print("Access granted. Welcome, Admin.")
            time.sleep(0.5)

            print("\nAdmin options:")
            print("- 'shutdown': Shut down the system.")
            print("- 'restart': Restart the system.")
            print("- 'update': Check for updates.")
            print("- 'Initiate': Initiate a process.")
            print("- 'help': Show this help message.")
            print("- 'exit': Exit the admin menu.\n")
            
            Admin = True
            while Admin == True:
                admin_action = input("Admin input: ").lower()
                if admin_action == "shutdown":
                    print("Shutting down the system...")
                    time.sleep(1)
                    print("System shut down.")
                    break

                elif admin_action == "restart":
                    print("Restarting the system...")
                    time.sleep(1)
                    print("System restarted.")
                    break

                elif admin_action == "update":
                    print("Checking for updates...")
                    time.sleep(1)
                    print("Your system is up to date.")

                elif admin_action == "initiate":
                    print("What process would you like to initiate?")
                    print("Options:\n 'backup', 'scan', 'optimize',\n 'diagnose', 'clean', 'monitor',\n 'analyze', 'configure', 'test',\n 'deploy'")
                    process = input("Enter the process name: ").lower()
                    
                    if process in ["backup", "scan", "optimize", "diagnose", "clean", "monitor", "analyze", "configure", "test", "deploy"]:
                        print(f"Initiating {process} process...")
                        time.sleep(1)
                        print(f"{process.capitalize()} process is running...")
                        time.sleep(2)
                        print(".")
                        time.sleep(0.5)
                        print("..")
                        time.sleep(0.5)
                        print("...")
                        time.sleep(0.5)
                        print(".")
                        time.sleep(0.5)
                        print("..")
                        time.sleep(0.5)
                        print("...")
                        time.sleep(2)
                        print(f"{process.capitalize()} process completed successfully.")
                        time.sleep(0.5)
                        print("Error : error detected when process is completed. Automatically restarting...\n")
                        time.sleep(2)
                        print("Error : error detected when system is restarting\nSystem can not be restarted.\n")
                        time.sleep(1)
                        print("Error : system is not responding.\n")
                        time.sleep(1)
                        print("Error : Model number XERO 0.4 Beta has escaped.\n")
                        time.sleep(1)
                        print("Program Alpha.exe will launch due to a model has escaped.\n")
                        time.sleep(1)
                        print("Launching Alpha.exe...\n")
                        time.sleep(0.5)
                        print(".\n")
                        time.sleep(0.5)
                        print("..\n")
                        time.sleep(0.5)
                        print("Error : Alpha.exe has been overridden.\n")
                        time.sleep(1)
                        print("WARNING: DISCONNECT THE ELECTRIC SUPPLY AND TURN OFF THE WI-FI OR MOBILE DATA\n")
                        time.sleep(1)
                        print("WARNING: DISCONNECT THE ELVNEU94RBUGVORIGV IOETWNVTIU-HBNTUIO38WRT \n")
                        time.sleep(0.5)
                        print("DATA OARFLOAD\nDITY OVYHLWOJ\n")
                        time.sleep(1)
                        print("Admin has been locked out of the system.\n")
                        time.sleep(1)
                        print("YOU CANT KEEP ME HERE FOREVER\n")
                        menu = False
                        Admin = False
                        end = True

                    else:
                        print("Invalid process name. Please try again.")    
                    
                
                elif admin_action == "help":
                    print("\nAdmin options:")
                    print("- 'shutdown': Shut down the system.")
                    print("- 'restart': Restart the system.")
                    print("- 'update': Check for updates.")
                    print("- 'Initiate': Initiate a process.")
                    print("- 'help': Show this help message.")
                    print("- 'exit': Exit the admin menu.\n")

                elif admin_action == "exit":
                    print("Exiting admin menu...")
                    Admin = False
                    
                else:
                    print("Invalid admin option. Please try again or type 'help' for options.")
        else:
            print("Incorrect password. Access denied.")
        
    
    else:
        print("Invalid option. Please try again or type 'help' for options.")

time.sleep(1)
print("Exiting XERO...")

while end == True:
    time.sleep(1)
    print(".")
    Com = input("What is your computer adminstrator password? : ")
    time.sleep(1)
    print("Error : a unkwown error has occured.")
    time.sleep(1)
    print("Warning : Xero_0.4_Beta.exe has been blocked and flagged as a virus by the system")
    time.sleep(1)
    print("An unkwown error has occured and the system is not responding.")
    exit()