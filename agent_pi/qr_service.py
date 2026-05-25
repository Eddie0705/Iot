import qrcode
import base64
import json
from io import BytesIO


def generate_qr_base64(booking_id, token):
    """Generate a QR code from booking_id + token, return as base64 string for HTML embedding."""
    data = json.dumps({"booking_id": booking_id, "token": token})
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
