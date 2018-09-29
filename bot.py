import telebot
import time
import networkx as net
import cv2
import numpy as np
from emoji import emojize
import scipy.misc
from point import Point
from mathoperation import MathOperation
from  numericstringparser import NumericStringParser
import mathpix
import segmentationalgorithm
from PIL import Image, ImageDraw, ImageFont



def run(img, t1, t2, message, width, height):
    edges = cv2.Canny(img,t1,t2)
    dilation_kernel = np.ones((5, 5),np.uint8)
    dilation = cv2.dilate(edges, dilation_kernel,iterations = 1)
    
    closing_kernel = np.ones((30, 30),np.uint8)
    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, closing_kernel)
    
    edges_arr = np.asarray(closing)
    edges_arr = np.expand_dims(edges_arr, axis=2)
    
    
    scipy.misc.toimage(dilation, cmin=0.0, cmax=1.0).save('outfile.jpg')
    #send photo to client
    photo = open('outfile.jpg', 'rb')
    bot.send_photo(chat_id=message.chat.id, photo=photo)
    
    #segmentation algorithm
    sums2 = segmentationalgorithm.fireHorizontalGrid(edges_arr, width, height)
    print("sums2: ", sums2)
    if sums2 is None:
        bot.send_message(message.chat.id, "Qualcosa è andato storto. Allontana un po' di più il dispositivo dal foglio!33")
        return
    else:
        mathOperations = segmentationalgorithm.fireVerticalGrid(sums2, edges_arr, width, height)
        if mathOperations is None:
            bot.send_message(message.chat.id, "Qualcosa è andato storto. Allontana un po' di più il dispositivo dal foglio!2")
            return
        else:
            return mathOperations

def wait_for_user_input():
    while True:
        try:
                bot.polling()
        except  Exception:
                time.sleep(15)


    
bot_token = '526035971:AAGJudEYdqnT9LZE-0Rz86PQvyel9agFyNo'
bot = telebot.TeleBot(token=bot_token)
user = bot.get_me()
print("myuser is",user.id)



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Ciao, sono un bot che corregge foto di operazioni matematiche scritte a mano. Inviami un foto con operazioni matematiche del tipo \"23 + 50 = 73\" o \"5 x 4 = 20\" e io ti dirò se sono giuste o meno! Versione 1.0: coreggo solo operazioni piane, non in colonna. A breve ci sarà l'upgrade ;)")        

    
    
    
    
@bot.message_handler(content_types=['photo'])
def photo(message):
    
    bot.send_message(message.chat.id, "Sto correggendo...")
    
    print("message.photo =", message.photo)
    fileID = message.photo[-1].file_id
    print("fileID =", fileID)
    file_info = bot.get_file(fileID)
    print("file.file_path =", file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)

    someOperationHasNotBeenReadProperly = False
    t1 = 225
    t2 = 350
    t1_adjust = 580
    t2_adjust = 680
    height = message.photo[3].height
    width = message.photo[3].width
    total_operation = 0
    
    
    
    
    
    #save photo locally
    with open("image.jpg", 'wb') as new_file: #"image.jpg" is chosen 
        new_file.write(downloaded_file)
    img = cv2.imread('image.jpg',0)
    
    
    
    
    #run algorithm
    mathOperations = run(img, t1, t2, message, width, height)
    
    
    
    
    #crop all operations from original image
    for index in range(mathOperations.size):
        if mathOperations[index].operation == "undefined":
            rgbimg = Image.open("image.jpg")
            crop = rgbimg.crop((mathOperations[index].x, mathOperations[index].y, mathOperations[index].x + mathOperations[index].width, mathOperations[index].y + mathOperations[index].height))
            crop.save("croppedImage/cropped" + str(index) + ".jpg")
    try:
        total_operation = index + 1
    except:
        
        #re run algorithm with adjusted canny threshold
        mathOperations = run(img, t1_adjust, t2_adjust, message, width, height)
        
        
        #crop all operations from original image
        #setResultFromMathpix()
        for index in range(mathOperations.size):
            if mathOperations[index].operation == "undefined":
                rgbimg = Image.open("image.jpg")
                crop = rgbimg.crop((mathOperations[index].x, mathOperations[index].y, mathOperations[index].x + mathOperations[index].width, mathOperations[index].y + mathOperations[index].height))
                crop.save("croppedImage/cropped" + str(index) + ".jpg")
        try:
            total_operation = index + 1
        except:
            bot.send_message(message.chat.id, "Qualcosa è andato storto. Allontana un po' di più il dispositivo dal foglio!20090")
            return
    
    
    
    
    
    
    
    
    #recognize characters
    mathOperations = mathpix.recognize(total_operation, mathOperations)
   






    
    #parse operations
    newMathOperations = np.array([])
    for index in range(mathOperations.size):
        if len(mathOperations[index].operation) != 0:
            newMathOperations = np.append(newMathOperations, mathOperations[index])
            #replace \\div and \\times if present
            if "\\times" in str(mathOperations[index].operation):
                mathOperations[index].operation = str(mathOperations[index].operation).replace("times", "*")
                mathOperations[index].operation = str(mathOperations[index].operation).replace("\\", "")
            if "\\div" in str(mathOperations[index].operation):
                mathOperations[index].operation = str(mathOperations[index].operation).replace("div", "/")
                mathOperations[index].operation = str(mathOperations[index].operation).replace("\\", "")
            if "x" in str(mathOperations[index].operation):
                mathOperations[index].operation = str(mathOperations[index].operation).replace("x", "*")
            if "div" in str(mathOperations[index].operation):
                mathOperations[index].operation = str(mathOperations[index].operation).replace("div", "/")
            if ":" in str(mathOperations[index].operation):
                mathOperations[index].operation = str(mathOperations[index].operation).replace(":", "/")
    
    
    
    
    
    
    
    #check if is present some letters in operations
    mathOperations = np.array([])    
    for index in range(newMathOperations.size):
        if "y" not in str(newMathOperations[index].operation) or "a" not in str(newMathOperations[index].operation) or "t" not in str(newMathOperations[index].operation):
            if "=" in str(newMathOperations[index].operation):
                mathOperations = np.append(mathOperations, newMathOperations[index])
    

    
    
    
    
    
    
    #delete spaces
    for index in range(mathOperations.size):
        mathOperations[index].operation = str(mathOperations[index].operation).replace(" ", "")
    
    
    print(mathOperations)
    
    
    
    
    
    
    #evaluate correctness
    nsp = NumericStringParser()
    newMathOp = np.array([])
    for index in range(mathOperations.size):
        splitOperation = str(mathOperations[index].operation).replace("[", "")
        splitOperation = splitOperation.replace("]", "")
        splitOperation = splitOperation.replace("'", "")
        splitOperation =  splitOperation.split("=")
        try:
            evaluation = nsp.eval(str(splitOperation[0]))
            moreOperationInOne = int(splitOperation[1])
        except:
            mathOperations[index].operation = "todelete"
        if mathOperations[index].operation != "todelete":
            newMathOp = np.append(newMathOp, mathOperations[index])
            if int(evaluation) == int(splitOperation[1]):
                mathOperations[index].isCorrect = True
            else:
                mathOperations[index].isCorrect = False
        else:
            if not someOperationHasNotBeenReadProperly: 
                someOperationHasNotBeenReadProperly = True
     
    mathOperations = newMathOp
    print(mathOperations)
    if mathOperations.size == 0:
        bot.send_message(message.chat.id, "Qualcosa è andato storto. Allontana un po' di più il dispositivo dal foglio!")
        return
    
    
    
    
    
    
    
    
    #draw result
    rgbimg = Image.open("image.jpg")
    fnt = ImageFont.truetype('/usr/share/fonts/truetype/roboto/hinted/Roboto-Bold.ttf', 40)
    d = ImageDraw.Draw(rgbimg)
    
    for index in range(mathOperations.size):
        if mathOperations[index].isCorrect:
            d.text((mathOperations[index].x, mathOperations[index].y - 40), "OK", font=fnt, fill=(0, 255, 0))
        else:
            d.text((mathOperations[index].x, mathOperations[index].y - 40), "NO", font=fnt, fill=(255, 0, 0))
    
    rgbimg.save("correctImage.jpg")
           
        
        
        
        
        
        
        
    
    #send photo to client
    photo = open('correctImage.jpg', 'rb')
    bot.send_photo(chat_id=message.chat.id, photo=photo)
    
    
    
    
    
    
    #send photo to client
    photo = open('outfile.jpg', 'rb')
    bot.send_photo(chat_id=message.chat.id, photo=photo)
    
    
    
    
    
    
    
    #send message of someOperationHasNotBeenReadProperly
    if someOperationHasNotBeenReadProperly:
        bot.send_message(message.chat.id, "E' probabile che qualche operazione non sia stata letta correttamente. Allontana un po' di più il dispositivo.")
    
    
    
    
    
    
    #send operations to client
    for index in range(mathOperations.size):
        splitOperation = str(mathOperations[index].operation).replace("[", "")
        splitOperation = splitOperation.replace("]", "")
        splitOperation = splitOperation.replace("'", "")
        if mathOperations[index].isCorrect:
            bot.send_message(message.chat.id, splitOperation + emojize(" Correct :white_check_mark:", use_aliases=True))
        else:
            bot.send_message(message.chat.id, splitOperation + emojize(" Wrong :x:", use_aliases=True))    

            
wait_for_user_input()            
                
                