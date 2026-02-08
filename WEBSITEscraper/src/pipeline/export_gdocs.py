import os.path
import pickle
import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from .models import ESGReport

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

def get_credentials():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def find_or_create_esg_doc(title="ESG Master Report"):
    """Finds an existing ESG doc or creates a new one."""
    creds = get_credentials()
    if not creds: return None
    
    service_drive = build('drive', 'v3', credentials=creds)
    service_docs = build('docs', 'v1', credentials=creds)
    
    # Search for the file
    query = f"name = '{title}' and mimeType = 'application/vnd.google-apps.document' and trashed = false"
    results = service_drive.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:
        # print(f"Found existing document: {files[0]['name']} ({files[0]['id']})")
        return files[0]['id']
    else:
        # Create new
        body = {'title': title}
        doc = service_docs.documents().create(body=body).execute()
        # print(f"Created new document: {title} ({doc.get('documentId')})")
        return doc.get('documentId')

def append_esg_analysis(document_id: str, report: ESGReport):
    """Appends (actually prepends to top) analysis to the given document."""
    creds = get_credentials()
    if not creds: return None
    service = build('docs', 'v1', credentials=creds)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format text content from Pydantic model
    text_content = (
        f"\n--------------------------------------------------\n"
        f"REPORT DATE: {timestamp}\n"
        f"TARGET URL: {report.url}\n"
        f"COMPANY: {report.company_name}\n"
        f"SUMMARY: {report.summary}\n\n"
        f"--- Environmental (Score: {report.environmental.score}) ---\n"
        f"Assessment: {report.environmental.assessment}\n"
        f"Gaps: {report.environmental.gaps or 'None'}\n\n"
        f"--- Social (Score: {report.social.score}) ---\n"
        f"Assessment: {report.social.assessment}\n"
        f"Gaps: {report.social.gaps or 'None'}\n\n"
        f"--- Governance (Score: {report.governance.score}) ---\n"
        f"Assessment: {report.governance.assessment}\n"
        f"Gaps: {report.governance.gaps or 'None'}\n"
        f"--------------------------------------------------\n\n"
    )

    # Insert at index 1 (top of document) so the newest is always first
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': text_content
            }
        }
    ]
    
    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"https://docs.google.com/document/d/{document_id}/edit"
