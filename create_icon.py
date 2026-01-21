from PIL import Image, ImageDraw, ImageFont
import os

# Crea un'immagine 256x256 con sfondo blu
img = Image.new('RGB', (256, 256), color=(70, 130, 180))  # Blu acciaio

# Aggiungi un cerchio bianco
draw = ImageDraw.Draw(img)
draw.ellipse([(28, 28), (228, 228)], fill=(255, 255, 255), outline=(0, 0, 0), width=3)

# Aggiungi la lettera "M" al centro
try:
    # Prova a caricare un font, altrimenti usa il font di default
    font = ImageFont.truetype("arial.ttf", 120)
except:
    font = ImageFont.load_default()
    
draw.text((80, 60), "M", fill=(70, 130, 180), font=font)

# Salva l'immagine come icona
img.save('icon.ico', format='ICO', sizes=[(256, 256)])
