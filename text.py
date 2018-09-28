from PIL import Image, ImageDraw, ImageFont

rgbimg = Image.open("image.jpg")

fnt = ImageFont.truetype('/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf', 40)

d = ImageDraw.Draw(rgbimg)

d.text((10, 10), "Hello World!", font=fnt, fill=(255, 255, 0))

rgbimg.save("imagetext.jpg")
