import cv2
import pytesseract
from pytesseract import Output
import re
import requests
from bs4 import BeautifulSoup as bs
from time import sleep
 
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
te=""


def filter_text(text):
    license_plate=""
    for x in text.strip():
        new_text= re.findall("[A-Z, 0-9]",x)
        if new_text: license_plate+=new_text[0]
    if license_plate.startswith("NL"):
        return license_plate.replace(license_plate[0:2], "")
    else:
        return license_plate
        
        
def get_data_from_website(licence_plate):
    response= requests.post("https://finnik.nl/kenteken/{}/gratis#basisgegevens".format(licence_plate))
    soup= bs(response.content, "html.parser")
    labels= soup.select("div", {"class":"label"})
    specifications = ["Merk", "Model", "Bouwjaar", "Kleur", "Brandstof","Voertuigsoort"]
    print("Auto specifications:")
    for x in labels:
        label= x.text.strip()
        if label in specifications:
            value = x.find_next_sibling().text.strip()
            print("{}: {}".format(label,value))
    
    
    





while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
 
    d = pytesseract.image_to_data(frame, output_type=Output.DICT)
    n_boxes = len(d['text'])
    #print(n_boxes)
    
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            (text, x, y, w, h) = (d['text'][i], d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            # don't show empty text
            if text and text.strip() != "":
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                frame = cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                te+=text
                
 
    # Display the resulting frame

    if len(te)==8: #Nederlandse kentekens bestaan uit 8 karakters inclusief min (-) tekens
        get_data_from_website(filter_text(te))
        break
    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
print(te)
print(filter_text(te))
#get_data_from_website(filter_text(te))
