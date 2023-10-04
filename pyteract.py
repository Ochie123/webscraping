
import pytesseract as pt
from PIL import Image
img = Image.open("/Users/patrick/Desktop/webscrapingd/logo_JDC0FGGU4V.png") 
text = pt.image_to_string(img) 
print(text)