import requests
from pathlib import Path
import os
import uuid
from datetime import datetime

uid = uuid.uuid4()
current_date = datetime.now()
at = current_date.isoformat()

API_KEY = os.environ.get("PDFCO_KEY")
URL = os.environ.get("RESUME_URL")

def get(fmt="Letter"):
    config = {
        "url": URL,
        "margins": "5mm",
        "paperSize": fmt,
        "orientation": "Portrait",
        "printBackground": True,
        "header": f"AUTO GENERATED FROM RESUME.BAS.WORK WITH {uid} @ {at}",
        "footer": "",
        "mediaType": "print",
        "async": False,
        "encrypt": False,
        "profiles": "{ \"CustomScript\": \";; // put some custom js script here \"}"
    }
    api_url = "https://api.pdf.co/v1/pdf/convert/from/url"
    r = requests.post(api_url, json=config, headers={"x-api-key": API_KEY})
    
    # Check if the request was successful
    if r.status_code != 200:
        print("Error in PDF generation request:", r.status_code, r.text)
        return None
    
    result = r.json()
    
    # Verify if "url" is in the result
    if "url" not in result:
        print("Error: 'url' key not found in API response.")
        print("Response received:", result)
        return None

    # Download the PDF
    download_url = result["url"]
    r = requests.get(download_url)
    output_path = Path(f"resume.{fmt}.pdf")
    with open(output_path, "wb") as f:
        f.write(r.content)
    return output_path

if __name__ == "__main__":
    # Ensure static_pdf directory exists
    os.makedirs("static_pdf", exist_ok=True)
    
    # Generate PDFs in specified formats
    fmts = ['Letter', 'A4']
    for fmt in fmts:
        pdf_path = get(fmt=fmt)
        if pdf_path:
            pdf_path.rename(f"static_pdf/resume.{fmt.lower()}.pdf")
