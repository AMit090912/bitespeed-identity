Bitespeed Identity Reconciliation API

This project is a solution for the Bitespeed backend task.

The goal is to build an endpoint that identifies and links multiple
contacts belonging to the same customer based on shared email or phone number.

------------------------------------------------------------

Hosted Endpoint:

POST https://bitespeed-identity-pa8h.onrender.com/identify

------------------------------------------------------------

How It Works:

- Contacts are linked if they share the same email OR phoneNumber.
- The oldest contact in a linked group becomes the primary contact.
- All other related contacts become secondary.
- If new information is provided, a new secondary contact is created.
- The API always returns a consolidated view of the identity cluster.

------------------------------------------------------------

Request Format (JSON):

{
  "email": "test@example.com",
  "phoneNumber": "123456"
}

At least one field (email or phoneNumber) must be provided.

------------------------------------------------------------

Response Format:

{
  "contact": {
    "primaryContactId": 1,
    "emails": ["test@example.com"],
    "phoneNumbers": ["123456"],
    "secondaryContactIds": []
  }
}

------------------------------------------------------------

Tech Stack:

- Python
- Django
- Django REST Framework
- SQLite
- Gunicorn
- Hosted on Render

------------------------------------------------------------

Running Locally:

1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt
3. Run migrations:
   python manage.py migrate
4. Start the server:
   python manage.py runserver

Then test at:
http://127.0.0.1:8000/identify

------------------------------------------------------------

Only POST method is supported.
The endpoint returns 400 if both email and phoneNumber are missing.
