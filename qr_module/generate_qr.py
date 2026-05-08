import qrcode

URL = 'http://192.168.1.3:8000'
img = qrcode.make(URL)
img.save('qr_module/viewer_qr.png')
print('QR saved to qr_module/viewer_qr.png')
