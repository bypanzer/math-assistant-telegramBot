import telebot
import time
import networkx as net
import cv2
import numpy as np
import scipy.misc
from point import Point
from mathoperation import MathOperation
import segmentationalgorithm

bot_token = '526035971:AAGJudEYdqnT9LZE-0Rz86PQvyel9agFyNo'
bot = telebot.TeleBot(token=bot_token)
user = bot.get_me()
print("myuser is",user.id)
def find_at(msg):
        for text in msg:
                if '@' in text:
                        return text
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
        bot.send_photo(chat_id=message.chat.id, photo='http://i64.tinypic.com/2r3bj0n.jpg')

        
@bot.message_handler(content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, message.text)        
        
        
@bot.message_handler(content_types=['photo'])
def photo(message):
    print("message.photo =", message.photo)
    fileID = message.photo[-1].file_id
    print("fileID =", fileID)
    file_info = bot.get_file(fileID)
    print("file.file_path =", file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)

    #save photo locally
    with open("image.jpg", 'wb') as new_file: #"image.jpg" is chosen 
        new_file.write(downloaded_file)
        
    #canny
    img = cv2.imread('image.jpg',0)
    edges = cv2.Canny(img,200,400)
    edges_arr = np.asarray(edges)
    edges_arr = np.expand_dims(edges_arr, axis=2)
    
    height = message.photo[3].height
    width = message.photo[3].width
    
    
    mathOperations = np.array([])
    
    #calculateHorizontalForegrounds
    foregrounds = segmentationalgorithm.calculateHorizontalForegrounds(edges_arr, width, height)
    
    
    #calculate sums -> [0, 0, 1, 1, 0] became -> [(2, 0), (2, 1), (1, 0)]
    sums = segmentationalgorithm.calculateSum(foregrounds)
    
    
    
    # start fireHorizontalGrid
    #deleteWhiteNoise
    sums = segmentationalgorithm.deleteWhiteNoise(sums, 10, 15)
    
    #mergeConsecutiveEqualsNumbers
    sums2 = segmentationalgorithm.mergeConsecutiveEqualsNumbers(sums)
            
    #deleteBlackNoise
    sums = segmentationalgorithm.deleteBlackNoise(sums2, 16, 15, 5)    
    
    #mergeConsecutiveEqualsNumbers
    sums2 = segmentationalgorithm.mergeConsecutiveEqualsNumbers(sums)
    
    #drawHorzontalLines
    segmentationalgorithm.drawHorizontalLines(sums2, edges_arr, width, height)
    
    # compelte fireHorizontalGrid
###################################################################################





    # start fireVerticalGrid
    start = 0
    stop = 0
    for index in range(sums2.size):
        if sums2[index].y == 1 and start <= height:
            stop = start + sums2[index].x

            foregrounds2 = segmentationalgorithm.calculateVerticalForegrounds(edges_arr, width, start, stop)
            if foregrounds2 is None:
                print("IS NONE")
            sums = segmentationalgorithm.calculateSum(foregrounds2)
            if sums is not None:
                sumsWithWhiteNoise = segmentationalgorithm.deleteWhiteNoise(sums, 5, 15)
                sums22 = segmentationalgorithm.mergeConsecutiveEqualsNumbers(sumsWithWhiteNoise)
                sumsWithBlackNoise = segmentationalgorithm.deleteBlackNoise(sums22, 45, 5, 5)
                sums32 = segmentationalgorithm.mergeConsecutiveEqualsNumbers(sumsWithBlackNoise)
                segmentationalgorithm.drawVerticalLines(sums32, edges_arr, width, height, start, stop, mathOperations)
        start = start + sums2[index].x
    
    # compelte fireVerticalGrid
    
    scipy.misc.toimage(edges, cmin=0.0, cmax=1.0).save('outfile.jpg')
    #send photo to client
    photo = open('outfile.jpg', 'rb')
    bot.send_photo(chat_id=message.chat.id, photo=photo)
    
@bot.message_handler(func=lambda msg: msg.text is not None and '@' in msg.text)
def at_answer(message):
        print(message)
        texts = message.text.split()
        at_text = find_at(texts)
        bot.reply_to(message, 'https://instagram.com/{}'.format(at_text[1:]))
while True:
        try:
                bot.polling()
        except  Exception:
                time.sleep(15)