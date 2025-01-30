import pandas as pd
import random
import requests
from datetime import datetime, timedelta
import time

# Airtable API setup for ticket creation (main database)
AIRTABLE_API_URL = 'https://api.airtable.com/v0/apphAso2UOGzzCCta/Tickets'
AIRTABLE_API_KEY = 'patypDr4Jcxgeo5sg.2765eba40c5171f435e9e68ceb0d36bdc0a2a15eccf5b3ac00492f906c21d431'
HEADERS = {'Authorization': f'Bearer {AIRTABLE_API_KEY}', 'Content-Type': 'application/json'}

# Define issue buckets and rules
ISSUE_BUCKETS = {
    'Scheduling': ['schedule', 'appointment', 'calendar', 'availability', 'time slots', 'PTO', 'vacation', 'reschedule', 'shift', 'overlap', 'session', 'missed appointment', 'time off', 'double-booked'],
    'System': ['API', 'integration', 'sync', 'system error', 'error code', 'bot', 'connectivity', 'syncing', 'upload', 'offline', 'data transfer', 'interface'],
    'Training': ['training', 'tutorial', 'guide', 'educational', 'learning', 'onboarding', 'course', 'e-learning', 'manual', 'new user', 'workflow', 'tips'],
    'Process': ['workflow', 'procedure', 'steps', 'issue resolution', 'manual input', 'process flow', 'steps to fix', 'administrative', 'guidelines', 'action steps'],
    'Crashing': ['crash', 'unable to load', 'error', 'fails', 'crashed', 'stopped working'],
    'Uncategorized': ['browser', 'device', 'app', 'interface', 'bugs', 'permissions', 'fix', 'issue', 'feedback', 'help', 'question', 'support', 'feature request']
}

# Define criticality based on keywords
CRITICALITY_KEYWORDS = {
    'High': ['block', 'urgent', 'critical', 'not working'],
    'Medium': ['problem', 'issue'],
    'Low': ['minor', 'small', 'not urgent']
}

# Load data from CSV
data = pd.read_csv('Updated_Case_Study_Clinic_Issues.csv')

# Function to categorize issues based on keywords (modified to allow multiple categories)
def categorize_issue(issue_description):
    issue_types = []  # This will hold the multiple issue types for multiple select
    for category, keywords in ISSUE_BUCKETS.items():
        if any(keyword.lower() in issue_description.lower() for keyword in keywords):
            issue_types.append(category)
    
    # If no categories match, return 'Uncategorized'
    if not issue_types:
        issue_types.append('Uncategorized')
    
    return issue_types  # Returning a list of categories

# Function to assign criticality based on keywords
def assign_criticality(issue_description):
    for criticality, keywords in CRITICALITY_KEYWORDS.items():
        if any(keyword.lower() in issue_description.lower() for keyword in keywords):
            return criticality
    return 'Medium'

# Function to generate a due date (3 business days after the current date)
def generate_due_date(date):
    due_date = date
    days_added = 0
    while days_added < 3:
        due_date += timedelta(days=1)
        if due_date.weekday() < 5:  # Business day check (Mon-Fri)
            days_added += 1
    return due_date

# Function to create a ticket
def create_ticket(row):
    # Generate ticket data
    clinic = row['Clinic']
    user = row['User']
    issue_description = row['Issue']
    issue_types = categorize_issue(issue_description)  # This is now a list
    criticality = assign_criticality(issue_description)
    date = datetime.now()
    due_date = generate_due_date(date)
    
    # Create the ticket payload for Airtable
    ticket = {
        'fields': {
            'Clinic': clinic,
            'User': user,
            'Type': issue_types,  # This is now a list of issue types for multiple select
            'Issue': issue_description,
            'Criticality': criticality,
            'Date': date.strftime('%Y-%m-%d'),
            'Due Date': due_date.strftime('%Y-%m-%d')
        }
    }
    
    # Log ticket for debugging
    print(f"Creating ticket: {ticket}")
    
    return ticket

# Function to insert the ticket into Airtable
def insert_ticket_to_airtable(ticket):
    response = requests.post(AIRTABLE_API_URL, json=ticket, headers=HEADERS)
    
    # Enhanced logging of response
    if response.status_code == 200:
        print(f"Ticket successfully created: {ticket['fields']['Issue']}")
    else:
        print(f"Error creating ticket: {response.status_code} - {response.text}")


# Process all issues in the CSV and create tickets
for index, row in data.iterrows():
    ticket = create_ticket(row)
    insert_ticket_to_airtable(ticket)
    time.sleep(1)  # Adding a delay to avoid hitting the rate limit
