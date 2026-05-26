# =============================================================================
# CUSTOM ENHANCEMENT 2: QR Code Booking Token
# Generates a QR code from the booking ID and access token after a successful
# booking. The QR code is displayed on the Agent Pi booking page and can be
# scanned at the Room Pi for check-in, replacing manual token entry.
# =============================================================================
import qrcode
import base64
import json
from io import BytesIO


def generate_qr_base64(booking_id, token):
    # Encode booking_id + token as JSON so Room Pi can extract both from one scan
    data = json.dumps({"booking_id": booking_id, "token": token})
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    # Return as base64 so it can be embedded directly in HTML without file storage
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
