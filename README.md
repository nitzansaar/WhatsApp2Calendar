# WhatsApp2Calendar

Building/Setup

1. Clone the repository:
git clone <repository-url>
2. Navigate to the project directory:
cd Whatsapp2Calendar
3. Install the required dependencies:
pip install -r requirements.txt
4. Set up Google Calendar API credentials:

- Go to the Google Cloud Console.
- Create a new project or use an existing one.
- Enable the Google Calendar API for the project.
- Create credentials (OAuth 2.0 Client IDs) and download the credentials.json file.
- Place the credentials.json file in the project directory.

5. Set up OpenAI API key:

- Sign up for OpenAI API access and obtain your API key.
- Add your API key to the script by setting openai.api_key = 'your_openai_api_key_here'.

6. Install Selenium WebDriver:

- Download the ChromeDriver that matches your version of Chrome from
<https://sites.google.com/a/chromium.org/chromedriver/>.
- Place the ChromeDriver in a directory included in your system's PATH.

Running & Example Usage

1. Open the terminal and navigate to the project directory:
cd Whatsapp2Calendar
2. Run the script:
python main.py
3. Follow the instructions in the terminal:

- Open WhatsApp Web in your browser and scan the QR code.
- The script will start monitoring the specified WhatsApp chat for new messages.

4. Example usage:

- When a new message is received in the specified chat with valid event details, the script will
parse the message and create an event in Google Calendar.
- If the message does not contain valid event details, it will be ignored.
- You can monitor the terminal for logs indicating the success or failure of event creation.

During this project, I learned how to:

1. Use Selenium to automate web interactions and extract data from WhatsApp Web.
2. Integrate the OpenAI API to parse unstructured text and extract structured information.
3. Work with the Google Calendar API to programmatically create events.
4. Handle various edge cases in text parsing and ensure robust error handling.
5. Combine different technologies to build an end-to-end automation solution.
