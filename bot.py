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
    
    
    scipy.misc.toimage(closing, cmin=0.0, cmax=1.0).save('outfile.jpg')
    #send photo to client
    photo = open('outfile.jpg', 'rb')
    bot.send_photo(chat_id=message.chat.id, photo=photo)
    
    #segmentation algorithm
    sums2 = segmentationalgorithm.fireHorizontalGrid(edges_arr, width, height)
    if sums2 is None:
        bot.send_message(message.chat.id, "Qualcosa è andato storto. Allontana un po' di più il dispositivo dal foglio!2")
        return
    else:
        mathOperations = segmentationalgorithm.fireVerticalGrid(sums2, edges_arr, width, height)
        if mathOperations is None:
            bot.send_message(message.chat.id, "Qualcosa è andato storto. Allontana un po' di più il dispositivo dal foglio!3")
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
    bot.send_message(message.chat.id, "Ciao, sono un bot che corregge foto di operazioni matematiche scritte a mano.")        

    
    
    
    
@bot.message_handler(content_types=['photo'])
def photo(message):
    
    bot.send_message(message.chat.id, "Sto correggendo...")
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
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
    mathOperations = run(img, t1_adjust, t2_adjust, message, width, height)
    
    if mathOperations is None:
        return
    
    
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
            bot.send_message(message.chat.id, "Qualcosa è andato storto. Allontana un po' di più il dispositivo dal foglio!4")
            return
    
    
    
    
    
    
    
    
    #recognize characters
    mathOperations = mathpix.recognize(total_operation, mathOperations)
    print(mathOperations)
   
    




    
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
            
            if "\\frac" in str(mathOperations[index].operation):
                mathOperations[index].operation = str(mathOperations[index].operation).replace("frac", "")
                mathOperations[index].operation = str(mathOperations[index].operation).replace("\\", "")
                if "=" not in str(mathOperations[index].operation):
                    if "+" in str(mathOperations[index].operation):
                        mathOperations[index].operation = str(mathOperations[index].operation).replace("}", "+", 1)
                        plus_equals = str(mathOperations[index].operation).replace('+', 'X', 1).find('+') #find second + in string
                        mathOperations[index].operation = str(mathOperations[index].operation)[:plus_equals] + '=' +str(mathOperations[index].operation)[plus_equals + 1:]
                    if "-" in str(mathOperations[index].operation):
                        mathOperations[index].operation = str(mathOperations[index].operation).replace("}", "-", 1)
                        plus_equals = str(mathOperations[index].operation).replace('-', 'X', 1).find('-') #find second + in string
                        mathOperations[index].operation = str(mathOperations[index].operation)[:plus_equals] + '=' +str(mathOperations[index].operation)[plus_equals + 1:]
                    if "*" in str(mathOperations[index].operation):
                        mathOperations[index].operation = str(mathOperations[index].operation).replace("}", "*", 1)
                        plus_equals = str(mathOperations[index].operation).replace('*', 'X', 1).find('*') #find second + in string
                        mathOperations[index].operation = str(mathOperations[index].operation)[:plus_equals] + '=' +str(mathOperations[index].operation)[plus_equals + 1:]
                    if "/" in str(mathOperations[index].operation):
                        mathOperations[index].operation = str(mathOperations[index].operation).replace("}", "/", 1)
                        plus_equals = str(mathOperations[index].operation).replace('/', 'X', 1).find('/') #find second + in string
                        mathOperations[index].operation = str(mathOperations[index].operation)[:plus_equals] + '=' +str(mathOperations[index].operation)[plus_equals + 1:]
                        
                    mathOperations[index].operation = str(mathOperations[index].operation).replace("{", "")
                    mathOperations[index].operation = str(mathOperations[index].operation).replace("}", "")
                    print("i would like to watch this: ", mathOperations[index].operation )
            #else: hadle this case if occours ' { { 21 } { 36 } + } { 57= }'
                
            if str(mathOperations[index].operation).count('=') == 0:
                second_comma = str(mathOperations[index].operation).replace(',', 'X', 1).find(',') #find second comma in string
                mathOperations[index].operation = str(mathOperations[index].operation)[:second_comma] + '=' +str(mathOperations[index].operation)[second_comma + 1:] #add equals sign     
                if "+" not in str(mathOperations[index].operation) or "*" not in str(mathOperations[index].operation) or "/" not in str(mathOperations[index].operation) or "-" not in str(mathOperations[index].operation):
                    mathOperations[index].operation = str(mathOperations[index].operation).replace(",", "-", 1) #TODO: test this else
                #same of overlying code but cleaner
                #s = str(mathOperations[index].operation)
                #index22 = s.replace(',', 'X', 1).find(',')
                #mathOperations[index].operation = s[:index22] +  '=' + s[index22+1:]        
                
            
            
    
    
    
    
    
    #check if is present some letters in operations
    mathOperations = np.array([])    
    for index in range(newMathOperations.size):
        if "y" not in str(newMathOperations[index].operation) or "a" not in str(newMathOperations[index].operation) or "t" not in str(newMathOperations[index].operation):
            if "=" in str(newMathOperations[index].operation):
                mathOperations = np.append(mathOperations, newMathOperations[index])
    

    #parsing for in column operation
    for index in range(mathOperations.size):
        if "'" in str(mathOperations[index].operation):
            mathOperations[index].operation = str(mathOperations[index].operation).replace("'", "")
        if "," in str(mathOperations[index].operation):
            mathOperations[index].operation = str(mathOperations[index].operation).replace(",", "")
        if "[" in str(mathOperations[index].operation):
            mathOperations[index].operation = str(mathOperations[index].operation).replace("[", "")
        if "]" in str(mathOperations[index].operation):
            mathOperations[index].operation = str(mathOperations[index].operation).replace("]", "")
        
        if " " in str(mathOperations[index].operation):
            mathOperations[index].operation = str(mathOperations[index].operation).replace(" ", "")
        
        if "\\$" in str(mathOperations[index].operation): #if $ is present, is likely being a 9
            mathOperations[index].operation = str(mathOperations[index].operation).replace("$", "9")
            mathOperations[index].operation = str(mathOperations[index].operation).replace("\\", "")
        if str(mathOperations[index].operation).count('=') > 1: #if more than one equals sign is present
            if "+" in str(mathOperations[index].operation) or "*" in str(mathOperations[index].operation) or "/" in str(mathOperations[index].operation) or "-" in str(mathOperations[index].operation):# case: '900 +', '16 =', '916 ='
                    second_equals = str(mathOperations[index].operation).replace('=', 'X', 1).find('=') #find second equals in string
                    mathOperations[index].operation = str(mathOperations[index].operation)[:second_equals] + '' +str(mathOperations[index].operation)[second_equals + 1:]    
            else:
                mathOperations[index].operation = str(mathOperations[index].operation).replace("=", "-", 1) #TODO: test this else
            
        if "\\hline" in str(mathOperations[index].operation):
            mathOperations[index].operation = str(mathOperations[index].operation).replace("hline", "")
            mathOperations[index].operation = str(mathOperations[index].operation).replace("\\", "")
        if "n" in str(mathOperations[index].operation):
            mathOperations[index].operation = str(mathOperations[index].operation).replace("n", "4") #if n is present, is likely being a 4
            
    #print(mathOperations)
    
    
    #################TODO############
    #need to test more and handle 2160', '1100', '2242

    
    
    
    
    #evaluate correctness
    nsp = NumericStringParser()
    newMathOp = np.array([])
    for index in range(mathOperations.size):
        splitOperation =  str(mathOperations[index].operation).split("=")
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
        bot.send_message(message.chat.id, "Qualcosa è andato storto. Allontana un po' di più il dispositivo dal foglio!444")
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
                
                