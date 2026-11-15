import sys, pypdfium2 as pdfium
from PIL import Image
pdf = pdfium.PdfDocument(sys.argv[1]); prefix = sys.argv[2]; scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.4
imgs = []
for i in range(len(pdf)):
    im = pdf[i].render(scale=scale).to_pil(); im.save(f"{prefix}-{i+1:02d}.png"); imgs.append(im)
for s in range(0, len(imgs), 6):
    group = imgs[s:s+6]; w, h = group[0].size; t = 0.5
    sheet = Image.new("RGB", (int(w*t)*3 + 40, int(h*t)*2 + 30), "white")
    for k, im in enumerate(group):
        sheet.paste(im.resize((int(w*t), int(h*t))), (10 + (k%3)*(int(w*t)+10), 10 + (k//3)*(int(h*t)+10)))
    sheet.save(f"{prefix}-sheet-{s//6+1:02d}.png")
print(len(imgs))
