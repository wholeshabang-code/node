import qrcode
import uuid
import os
from typing import List

from dotenv import load_dotenv
import os

load_dotenv()

def generate_qr_codes(n: int, base_url: str = None) -> List[str]:
    """
    Generate n QR codes with unique UUIDs
    
    Args:
        n: Number of QR codes to generate
        base_url: Base URL for the QR codes (optional, will use BASE_URL from env if not provided)
        
    Returns:
        List of generated UUIDs
    """
    # Create qrcodes directory if it doesn't exist
    qr_dir = "static/qrcodes"
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)
    
    if base_url is None:
        base_url = os.getenv("BASE_URL", "http://localhost:8000")

    generated_uuids = []
    
    for _ in range(n):
        # Generate unique UUID
        unique_id = str(uuid.uuid4())
        generated_uuids.append(unique_id)
        
        # Create QR code URL
        qr_url = f"{base_url}/note/{unique_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        qr_image.save(f"{qr_dir}/{unique_id}.png")
    
    return generated_uuids

if __name__ == "__main__":
    import sys
    
    try:
        if len(sys.argv) != 2:
            print("Usage: python generate_qr.py <number_of_codes>")
            sys.exit(1)
            
        num_codes = int(sys.argv[1])
        uuids = generate_qr_codes(num_codes)
        print(f"Generated {len(uuids)} QR codes:")
        for uuid in uuids:
            print(f"- {uuid}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)