import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
import datetime
import openai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv


# Initialize the Chrome driver
driver = webdriver.Chrome()

# Open WhatsApp Web
driver.get("https://web.whatsapp.com")

# Wait for user to scan QR code
input("Press Enter after scanning the QR code")

# Search and open the chat
chat_name = "VA - New Rosa Prosper"  # Replace with the name of the chat
search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][1]')
search_box.click()
search_box.send_keys(chat_name)
search_box.send_keys(Keys.RETURN)

# Initialize the previous message count
previous_message_count = 0

# Function to print new messages
def get_new_messages():
    global previous_message_count

    # Find all message elements
    messages = driver.find_elements(By.XPATH, '//div[contains(@class,"message-in") or contains(@class,"message-out")]//div[@class="copyable-text"]')

    # Get the current message count
    current_message_count = len(messages)

    # If the current message count is greater than the previous count, print the new messages
    # if current_message_count > previous_message_count:
    new_messages = messages[previous_message_count:current_message_count]
    new_message_texts = [message.text for message in new_messages]
    
    # Update the previous message count
    # previous_message_count = current_message_count
    
    return new_message_texts
    

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def parse_event_details_with_openai(event_details):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured event details from text."},
                {"role": "user", "content": f"Extract the following details from this text: {event_details}\n"
                                            "Provide the extracted details in the following format:\n"
                                            "Booking Date: <booking_date>\n"
                                            "Event Date: <event_date>\n"
                                            "Event Time: <event_time> (if available)\n"
                                            "Phone: <phone>\n"
                                            "Name: <name>\n"
                                            "Address: <address>\n"
                                            "City: <city>\n"
                                            "State: <state>\n"
                                            "Zip Code: <zip_code>\n"
                                            "Description: <description>\n"
                                            "Note that the address ends after the zip code, and the address may be separated by tabs.\n"
                                            "Note that there may be a space between the time and 'am' or 'pm'"
                                            "Ignore any message that does not have an event time.\n"
                                            "Examples:\n"
                                            "Booking Date: 6.4.24\n"
                                            "Event Date: 6.6.24\n"
                                            "Event Time: 1pm\n"
                                            "Phone: 15104144644\n"
                                            "Name: John Hornung\n"
                                            "Address: 2835 Buena Vista Way\n"
                                            "City: Berkeley\n"
                                            "State: CA\n"
                                            "Zip Code: 94708\n"
                                            "Description: Renovation project to install or replace an asphalt shingle roof.\n"
                                            "Booking Date: 6.6.24\n"
                                            "Event Date: 6.7.24\n"
                                            "Event Time: 12noon\n"
                                            "Phone: 14086099126\n"
                                            "Name: Sunil Patel\n"
                                            "Address: 2950 Postwood Drive\n"
                                            "City: San Jose\n"
                                            "State: CA\n"
                                            "Zip Code: 95132\n"
                                            "Description: Renovation project to remodel 2 bathrooms, and kitchen cabinets, redo the floors, replace drywall and interior and exterior painting.\n"
                                            "Booking Date: 6.7.24\n"
                                            "Event Date: 6.7.24\n"
                                            "Event Time: 1pm\n"
                                            "Phone: 15105351082\n"
                                            "Name: Martin Johnson\n"
                                            "Address: 1101 57th Ave\n"
                                            "City: Oakland\n"
                                            "State: CA\n"
                                            "Zip Code: 94621\n"
                                            "Description: Renovation project to install a new concrete foundation.\n"
                                            "Booking Date: 6.7.24\n"
                                            "Event Date: 6.9.24\n"
                                            "Event Time: 2:30pm\n"
                                            "Phone: 15103004425\n"
                                            "Name: Jaydah Howlett\n"
                                            "Address: 17158 Via Alamitos\n"
                                            "City: San Lorenzo\n"
                                            "State: CA\n"
                                            "Zip Code: 94578\n"
                                            "Description: Renovation project to install wood or stone laminate flooring in 2 bedrooms plus living room and hallway."}
            ]
        )
        
        result = response['choices'][0]['message']['content'].strip()
        print(f"Parsed result: {result}")  # Log the parsed result
        # Split by lines and map to the corresponding variables
        details = {}
        for line in result.split('\n'):
            if ': ' in line:
                key, value = line.split(': ', 1)
                details[key] = value
        # Only return details if the Event Time is present
        if "Event Time" in details and details["Event Time"].strip():
            return details
        else:
            print("No event time found; ignoring this entry.")
            return {}
    except openai.error.RateLimitError:
        print("Rate limit exceeded. Please wait and try again later.")
        return {}
    except openai.error.InvalidRequestError as e:
        print(f"Invalid request error: {e}")
        return {}


def normalize_time_format(time_str):
    # Ensure the time format is consistent (e.g., "530pm" -> "5:30pm")
    time_str = time_str.lower().replace('.', ':')
    if 'noon' in time_str:
        return '12:00pm'
    if len(time_str) == 4 and time_str[-2:] in ['am', 'pm']:
        time_str = time_str[:-2] + ':00' + time_str[-2:]
    if len(time_str) == 5 and time_str[-2:] in ['am', 'pm']:
        time_str = time_str[:-2] + 'm'
    if len(time_str) == 6 and time_str[-2:] in ['am', 'pm'] and ':' not in time_str:
        time_str = time_str[:1] + ':' + time_str[1:]
    if len(time_str) == 7 and time_str[-2:] in ['am', 'pm'] and ':' not in time_str:
        time_str = time_str[:2] + ':' + time_str[2:]
    return time_str

def preprocess_event_details(event_details):
    # Remove any initial date that does not match the expected booking date format
    event_details = re.sub(r'^[A-Za-z]+\s\d{1,2},\s\d{2}\n', '', event_details)
    return event_details.strip()

def create_event(service, parsed_details):
    required_fields = ["Event Date", "Event Time", "Phone", "Name", "Address", "City", "State", "Zip Code", "Description"]
    print(f"Parsed details before creating event: {parsed_details}")  # Log the parsed details
    if not all(field in parsed_details for field in required_fields):
        print("Failed to parse event details correctly. Parsed details:", parsed_details)
        return False
    
    event_date = parsed_details["Event Date"]
    event_time = normalize_time_format(parsed_details["Event Time"])
    phone = parsed_details["Phone"]
    name = parsed_details["Name"]
    address = parsed_details["Address"]
    city = parsed_details["City"]
    state = parsed_details["State"]
    zip_code = parsed_details["Zip Code"]
    description = parsed_details["Description"]

    # Parse the date and time
    try:
        event_datetime_str = f"{event_date} {event_time.upper()}"
        event_datetime = datetime.datetime.strptime(event_datetime_str, "%m.%d.%y %I:%M%p")
    except ValueError:
        try:
            event_datetime = datetime.datetime.strptime(event_datetime_str, "%m.%d.%y %I%p")
        except ValueError:
            print("Invalid date/time format. Please check the input.")
            return False

    # Start and end time of the event
    start_datetime = event_datetime.isoformat()
    end_datetime = (event_datetime + datetime.timedelta(minutes=60)).isoformat()

    event = {
        'summary': f"ros {phone} {name}",
        'location': f"{address}, {city}, {state} {zip_code}",
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'America/Los_Angeles',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
        return True
    except HttpError as error:
        print(f"An error occurred: {error}")
        return False


def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        while True:
            new_messages = get_new_messages()
            for message in new_messages:
                # Preprocess the event details to remove any initial date
                event_details = preprocess_event_details(message)

                # Split the event details into individual events
                event_blocks = re.split(r'(\d+\.\d+\.\d+ Booked)', event_details)
                if len(event_blocks) > 1:
                    event_blocks = [''.join(event_blocks[i:i+2]) for i in range(1, len(event_blocks), 2)]

                # Create events for each block
                for block in event_blocks:
                    parsed_details = parse_event_details_with_openai(block.strip())
                    if parsed_details:
                        success = create_event(service, parsed_details)
                        if success:
                            print(f"Event created for message: {message}")
                        else:
                            print(f"Failed to create event for message: {message}")
                    else:
                        print(f"No valid event details found in message: {message}")

            time.sleep(5)  # Check every 5 seconds

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()