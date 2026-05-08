import cv2, os, shutil, numpy as np

RAW = 'data/raw_images'
OUT = 'data/validated_images'
BLUR_THRESHOLD = 5

os.makedirs(OUT, exist_ok=True)
hashes = set()

for fname in os.listdir(RAW):
    path = os.path.join(RAW, fname)
    img = cv2.imread(path)
    if img is None: continue
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    if blur < BLUR_THRESHOLD:
        print(f'Skipped (blur): {fname}')
        continue
    h = hash(gray.tobytes())
    if h in hashes:
        print(f'Skipped (duplicate): {fname}')
        continue
    hashes.add(h)
    shutil.copy(path, os.path.join(OUT, fname))
    print(f'Validated: {fname}')
