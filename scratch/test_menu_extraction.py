import asyncio
import os
import sys
from io import BytesIO
from fastapi import UploadFile
from PIL import Image, ImageDraw

# Add the parent directory to Python path to import our app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import api.restaurant_dashboard
from api.restaurant_dashboard import upload_and_parse_menu
from models import UserRole

class MockUser:
    def __init__(self):
        self.id = 1
        self.role = UserRole.RESTAURANT
        self.first_name = "Test"
        self.last_name = "Restaurant"

async def test_image_extraction():
    print("\n--- Testing Image Menu Digitization ---")
    
    # Create a simple menu image programmatically using Pillow
    print("Generating a simple mock menu image...")
    img = Image.new('RGB', (500, 400), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Draw text sections
    d.text((20, 20), "SOUND IT BEACH CLUB - MENU", fill=(0, 0, 0))
    
    d.text((20, 60), "--- APPETIZERS ---", fill=(50, 50, 50))
    d.text((20, 80), "Garlic Bread", fill=(0, 0, 0))
    d.text((400, 80), "SLE 35.0", fill=(0, 0, 0))
    d.text((20, 95), "Toasted french bread with garlic herb butter", fill=(100, 100, 100))
    
    d.text((20, 130), "--- MAIN COURSE ---", fill=(50, 50, 50))
    d.text((20, 150), "Jollof Rice with Grilled Chicken", fill=(0, 0, 0))
    d.text((400, 150), "SLE 120.0", fill=(0, 0, 0))
    d.text((20, 165), "Spicy tomato rice served with quarter chicken", fill=(100, 100, 100))
    
    d.text((20, 200), "Grilled Red Snapper", fill=(0, 0, 0))
    d.text((400, 200), "SLE 180.0", fill=(0, 0, 0))
    
    d.text((20, 240), "--- DRINKS ---", fill=(50, 50, 50))
    d.text((20, 260), "Ginger Beer (Local)", fill=(0, 0, 0))
    d.text((400, 260), "SLE 25.0", fill=(0, 0, 0))
    d.text((20, 275), "Freshly brewed fiery ginger beverage", fill=(100, 100, 100))
    
    # Save to buffer
    img_buf = BytesIO()
    img.save(img_buf, format='PNG')
    image_bytes = img_buf.getvalue()
    
    # Also save to scratch folder for visual reference
    os.makedirs("scratch", exist_ok=True)
    img.save("scratch/test_menu_input.png")
    print("Mock menu image saved to scratch/test_menu_input.png")
    
    file = UploadFile(
        filename="test_menu.png",
        file=BytesIO(image_bytes),
        size=len(image_bytes),
        headers={"content-type": "image/png"}
    )
    
    mock_user = MockUser()
    
    try:
        result = await upload_and_parse_menu(file=file, db=None, current_user=mock_user)
        print("\nImage Digitization Success!")
        print("Extracted Menu Items:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error occurred during image test: {e}")

async def test_pdf_extraction():
    print("\n--- Testing PDF Text Menu Digitization ---")
    
    # Mock class to bypass PdfReader file reading
    class MockPage:
        def extract_text(self):
            return (
                "STARTERS\n"
                "Garlic Bread - SLE 35.00\n"
                "Chicken Wings (6pcs) - SLE 75.00\n"
                "MAINS\n"
                "Cassava Leaf with Rice - SLE 110.00\n"
                "Grilled Red Snapper with Chips - SLE 180.00\n"
                "DRINKS\n"
                "Ginger Beer - SLE 20.00\n"
                "Star Beer - SLE 30.00\n"
            )
    
    class MockPdfReader:
        def __init__(self, stream):
            self.pages = [MockPage()]
            
    # Monkeypatch the PdfReader imported in restaurant_dashboard module
    original_reader = api.restaurant_dashboard.PdfReader
    api.restaurant_dashboard.PdfReader = MockPdfReader
    
    # We pass a simple mock byte stream
    pdf_bytes = b"%PDF-1.4 mock pdf bytes"
    file = UploadFile(
        filename="sample_menu.pdf",
        file=BytesIO(pdf_bytes),
        size=len(pdf_bytes),
        headers={"content-type": "application/pdf"}
    )
    
    mock_user = MockUser()
    try:
        result = await upload_and_parse_menu(file=file, db=None, current_user=mock_user)
        print("\nPDF Digitization Success!")
        print("Extracted Menu Items:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error occurred during PDF test: {e}")
    finally:
        # Restore original reader
        api.restaurant_dashboard.PdfReader = original_reader

if __name__ == "__main__":
    # Load env vars
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(test_image_extraction())
    asyncio.run(test_pdf_extraction())
