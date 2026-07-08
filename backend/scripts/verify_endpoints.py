import requests
from PIL import Image, ImageDraw, ImageFont
import io
import os

API = os.environ.get('API_BASE', 'http://127.0.0.1:8000')


def test_text():
    print('Testing /predict/text...')
    resp = requests.post(f'{API}/predict/text', data={'text': 'This is a breaking rumor about a miracle cure'})
    print('Status:', resp.status_code)
    print(resp.json())


def test_image():
    print('Testing /predict/image...')
    # create an image with text
    img = Image.new('RGB', (600, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 24)
    except Exception:
        font = ImageFont.load_default()
    text = "Official statement: project approved"
    d.text((10, 50), text, fill=(0, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    files = {'file': ('test.png', buf, 'image/png')}
    resp = requests.post(f'{API}/predict/image', files=files)
    print('Status:', resp.status_code)
    print(resp.json())


if __name__ == '__main__':
    test_text()
    test_image()
