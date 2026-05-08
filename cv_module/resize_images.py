import cv2, os

SRC = 'data/validated_images'
DST = 'data/resized_images'
TARGET_W = 800

os.makedirs(DST, exist_ok=True)
for fname in os.listdir(SRC):
    img = cv2.imread(os.path.join(SRC, fname))
    if img is None: continue
    h, w = img.shape[:2]
    new_h = int(h * TARGET_W / w)
    resized = cv2.resize(img, (TARGET_W, new_h), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(os.path.join(DST, fname), resized)
    print(f'Resized {fname}: {w}x{h} -> {TARGET_W}x{new_h}')
