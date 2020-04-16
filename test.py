import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Patent List of Dict to Create

Patent_List_Create = [{"Display_Name": "2A", "Given_Name": "2A", "Honorific_Prefix": "2P", "Phone_Number": "0001"}
    , {"Display_Name": "3A", "Given_Name": "3A", "Honorific_Prefix": "3P", "Phone_Number": "0002"}]

SCOPES = ["https://www.googleapis.com/auth/contacts"]  # Scope of Contacts


def create_contact(Display_Name, Given_Name, Honorific_Prefix, Phone_Number):
    people.createContact(
        body={
            "names": [{"displayName": Display_Name, "givenName": Given_Name, "honorificPrefix": Honorific_Prefix}]

            , "phoneNumbers": [
                {
                    'value': Phone_Number
                }
            ]}
    ).execute()


if __name__ == "__main__":
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token_contacts.pickle'):
        with open('token_contacts.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token_contacts.pickle', 'wb') as token:
            pickle.dump(creds, token)

    contacts_service = build('people', 'v1', credentials=creds)

    people = contacts_service.people()

    # Get All Contacts

    temp_people = people.connections().list(
        resourceName='people/me'
        , personFields='names'
    ).execute()

    temp_page_token = temp_people["nextPageToken"]

    connection_list = temp_people["connections"]

    try:
        while temp_page_token:
            temp_people = people.connections().list(
                resourceName='people/me'
                , pageToken=temp_page_token
                , personFields='names'
            ).execute()
            connection_list += temp_people["connections"]
            temp_page_token = temp_people["nextPageToken"]


    except:
        None

    # Get Current Patients in the Contacts

    Current_Patient_ID = []

    for val in connection_list:
        try:
            Current_Patient_ID.append(val["names"][0]["honorificPrefix"])
        except:
            continue

    # Create Contacts not available in Current Contacts

    for val in Patent_List_Create:
        if val["Honorific_Prefix"] not in Current_Patient_ID:
            create_contact(val["Display_Name"], val["Given_Name"], val["Honorific_Prefix"], val["Phone_Number"])