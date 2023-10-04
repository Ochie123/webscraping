from PIL import Image
import pytesseract


pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
print(pytesseract.image_to_string(Image.open('/Users/patrick/Desktop/webscrapingd/UtahValley_logo-small.png')))
