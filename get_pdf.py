import requests
from pathlib import Path
import os
import uuid
from datetime import datetime

# Generate unique ID and timestamp for logs
uid = uuid.uuid4()
current_date = datetime.now()
at = current_date.isoformat()

# Fetch environment variables
API_KEY = os.environ.get("PDFCO_KEY")
URL = os.environ.get("RESUME_URL")

# Validate and fix URL if needed
if not API_KEY:
    raise ValueError("Environment variable 'PDFCO_KEY' is not set.")
if not URL:
    raise ValueError("Environment variable 'RESUME_URL' is not set or is invalid.")

# Ensure URL uses HTTPS
if not URL.startswith("http://") and not URL.startswith("https://"):
    print(f"URL '{URL}' does not include a scheme. Prepending 'https://'.")
    URL = f"https://{URL}"
elif URL.startswith("http://"):
    print(f"URL '{URL}' uses 'http://'. Updating to 'https://'.")
    URL = URL.replace("http://", "https://", 1)

def get(fmt="Letter"):
    """Generate a PDF from the given URL using PDF.co API."""
    config = {
        "url": URL,
        "margins": "5mm",
        "paperSize": fmt,
        "orientation": "Portrait",
        "printBackground": True,
        "footer": "",
        "mediaType": "print",
        "async": False,
        "encrypt": False,
        "profiles": "{ \"CustomScript\": \";; // put some custom js script here \"}"
    }
    api_url = "https://api.pdf.co/v1/pdf/convert/from/url"
    
    # Send the request to the PDF generation API
    print(f"Sending request to generate PDF for URL: {URL}")
    r = requests.post(api_url, json=config, headers={"x-api-key": API_KEY})
    
    # Check if the request was successful
    if r.status_code != 200:
        print(f"Error in PDF generation request: {r.status_code}")
        print(f"Response: {r.text}")
        return None
    
    result = r.json()
    print(f"API Response: {result}")
    
    # Verify if "url" is in the result
    if "url" not in result:
        print("Error: 'url' key not found in API response.")
        return None

    # Download the PDF
    download_url = result["url"]
    print(f"Downloading PDF from: {download_url}")
    r = requests.get(download_url)
    if r.status_code != 200:
        print(f"Error downloading PDF: {r.status_code}")
        return None

    # Save the downloaded PDF
    output_path = Path(f"resume.{fmt}.pdf")
    with open(output_path, "wb") as f:
        f.write(r.content)
    print(f"PDF saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    # Ensure static_pdf directory exists
    os.makedirs("static_pdf", exist_ok=True)
    
    # Generate PDFs in specified formats
    fmts = ['Letter']
    for fmt in fmts:
        pdf_path = get(fmt=fmt)
        if pdf_path:
            final_path = Path("static_pdf") / f"resume.{fmt.lower()}.pdf"
            pdf_path.rename(final_path)
            print(f"PDF moved to: {final_path}")
