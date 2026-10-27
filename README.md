# Medical Appointment Reminder System

A web-based application built with Python and Streamlit to manage medical appointments and generate AI-powered reminder messages.

## Features

- Add patient appointments
- Store appointment details in an SQLite database
- View saved appointments
- Update appointment status: Pending, Confirmed, or Cancelled
- Generate polite appointment reminder messages using AI

## Technologies Used

- Python
- Streamlit
- SQLite
- Groq API
- Python-dotenv

## How to Run the Project

1. Install Python on your computer.
2. Install the required packages:

   ```bash
   pip install streamlit groq python-dotenv
   ```

3. Create a `.env` file in the project folder and add your own Groq API key:

   ```text
   GROQ_API_KEY=your_api_key_here
   ```

4. Run the application:

   ```bash
   python -m streamlit run main.py
   ```

## Security

- Keep your API key private.
- Do not upload your `.env` file.
- Do not upload patient databases or confidential patient information.


