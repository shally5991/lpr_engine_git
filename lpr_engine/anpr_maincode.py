import cv2,easyocr,re,time
import _thread,boto3
import re,easyocr,imutils,time,os
from imutils import paths
import matplotlib.pyplot as plt
from PIL import Image
import requests 
from io import BytesIO
# import threading

class Giroux_main:   
    def __init__(self):
        self.post_url='http://localhost:1234/api/ml/check_in'
        self.put_url='http://localhost:1234/api/ml/check_out/'

    # def extract_plate(self,img):
    #     plate_img = img.copy()
    #     plate_cascade = cv2.CascadeClassifier(os.path.join(os.getcwd()+'/NumberPlateHaarCascade.xml'))# change for aws s3 bucket
    #     plate_rect = plate_cascade.detectMultiScale(plate_img, scaleFactor = 1.9, minNeighbors = 7)
    #     #plate_rect=plate_rect.max(axis=0).reshape(1,-1)
    #     #print(plate_rect)
    #     if len(plate_rect)>0:
    #         for (x,y,w,h) in plate_rect:
    #             a,b = (int(0.02*img.shape[0]), int(0.025*img.shape[1]))    
    #             plate = plate_img[y:y+h+5, x:x+w,:]
    #             cv2.rectangle(plate_img, (x,y), (x+w,y+h), (51,51,255), 3)
    #         return plate_img, plate ,x,y # returning the processed image.
    #     return img, []
    def save_plate(self,plate_img):
        plate_img=cv2.cvtColor(plate_img,cv2.COLOR_BGR2RGB)
        # Creates an image memory from an object exporting the array interface 
        plate= Image.fromarray(plate_img)
        #x, y = plate.size
        #x2, y2 = x-round(x/1.5), y-round(y/1.5)
        #plate = plate.resize((x2,y2),Image.Resampling.LANCZOS)
        return plate
             

    def anpr(self,img_ori):
        reader = easyocr.Reader(['en'])
        result = reader.readtext(img_ori)
        print(result)
        text_data=list(filter(lambda i:len(i[1])>8,result))
        print( "text_data :: " , text_data)
        
        for txt in text_data:
            x,y=txt[0][0],txt[0][2]
            acc=txt[-1]
            txt=txt[1]
            clean_text=''.join(re.findall(r'\w',txt))
            # MIF2KE9228
            if re.search(r'^[a-z,A-Z]{3}[0-9]{1,2}[a-z,A-Z]{1,3}[0-9]{4}$',clean_text):
                text=clean_text.upper()  
                n_img=img_ori[x[1]:y[1],x[0]:y[0],:]
                print("n_img :: ", n_img)
                
                plate_img=self.save_plate(n_img)
                plate_img.show()
                cv2.imshow('frame', n_img)                
                return text,plate_img
        return None,None
anpr_model=Giroux_main()
def entry_monitor(entry):
        old_text=''
        lst=[]
        cam=cv2.VideoCapture(entry)
        while 1:
            img_result,img_ori=cam.read()
            if not img_result:
                break
            
            # anpr_model.anpr(img_ori)
            plate_text,plate_image=anpr_model.anpr(img_ori) 

            if plate_text:
                if plate_text!=old_text:
                    old_text=plate_text
                    lst.append(plate_text)
                    buf = BytesIO()
                    plate_image.save(buf, format='JPEG')
                    buf.name = 'test.jpeg'
                    image_file_descriptor = buf.getvalue()
                    files = {'plateImage': ('test.jpeg',image_file_descriptor,'image/jpeg')}




                    plate_data={'cameraid':'sdfs89769','plate':plate_text,'time_in':time.ctime()}
                    res1=requests.post(anpr_model.post_url,data=plate_data,files=files)

                    
                    # print("plate_data :: ", plate_data)
            # if cv2.waitKey(1) == ord('q'):
            #     break
            # cv2.imshow("Original Image", img_ori)

            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break
            
        cam.release()
        # print(lst)
     
def exit_monitor(exit):
        old_text=''
        cam=cv2.VideoCapture(exit)
        while 1:
            img_result,img_ori=cam.read()
            if not img_result:
                break
            plate_text,plate_image=anpr_model.anpr(img_ori) 
            if plate_text:
                if plate_text!=old_text:
                    old_text=plate_text
                    plate_data={'cameraid':'out_cam','time_out':time.ctime()}
                    res1=requests.put(anpr_model.put_url+plate_text,data=plate_data)
                    print(res1)
        cam.release()
url='video2.mp4'
entry_monitor(url) 
exit_monitor(url)
# entry_monitor(url) 
# exit_monitor(url)
# entry_monitor(url) 
# exit_monitor(url)
# entry_monitor(url) 
# exit_monitor(url)
# entry_monitor(url) 
# exit_monitor(url)

#def giroux_ml_engine(entry,exit):
#    t1 = threading.Thread(target=entry_monitor, args=(entry,))
#    t2 = threading.Thread(target=exit_monitor, args=(exit,))
#    t1.start()
#    t2.start()
#    t1.join()
#    t2.join()
