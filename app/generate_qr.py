import qrcode
import uuid
import os
from typing import List

from dotenv import load_dotenv
import os

load_dotenv()

def get_base_url():
    # If VERCEL_URL is set, use it regardless of VERCEL_ENV
    if os.getenv("VERCEL_URL"):
        # Make sure to include https://
        vercel_url = os.getenv("VERCEL_URL")
        if not vercel_url.startswith(("http://", "https://")):
            vercel_url = f"https://{vercel_url}"
        return vercel_url
    return os.getenv("BASE_URL", "http://localhost:8000")

def generate_qr_codes(n: int, base_url: str = None) -> List[str]:
    """
    Generate n QR codes with unique UUIDs
    
    Args:
        n: Number of QR codes to generate
        base_url: Base URL for the QR codes (optional, will use environment-based URL if not provided)
        
    Returns:
        List of generated UUIDs
    """
    # Create qrcodes directory if it doesn't exist
    qr_dir = "static/qrcodes"
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)
    
    # Hardcoded Vercel URL
    base_url = "https://node-blond-chi.vercel.app"

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