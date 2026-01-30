from flask import Flask, render_template, request, jsonify
import qrcode
from PIL import Image
import io
import base64
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qr():
    try:
        data = request.json
        content = data.get('content') # Changed from 'url' to 'content' to be generic
        fill_color = data.get('fill_color', '#000000')
        back_color = data.get('back_color', '#ffffff')
        logo_data = data.get('logo_data') # Base64 encoded logo string

        if not content:
            return jsonify({'error': 'Content is required'}), 400

        # Create QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H, # High error correction for logos
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)

        # Generate Image
        img = qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGBA')

        # Embed Logo if provided
        if logo_data:
            try:
                # Decode base64 logo
                logo_bytes = base64.b64decode(logo_data.split(',')[1])
                logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")

                # Calculate logo size (max 20% of QR size)
                width, height = img.size
                logo_size = int(width * 0.25) 
                logo.thumbnail((logo_size, logo_size))

                # Calculate position (center)
                logo_pos = ((width - logo.size[0]) // 2, (height - logo.size[1]) // 2)
                
                # Paste logo
                img.paste(logo, logo_pos, mask=logo)
            except Exception as e:
                print(f"Logo processing error: {e}")
                # Continue without logo if it fails

        # Save to memory
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Encode to Base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        return jsonify({'image_data': img_base64})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
