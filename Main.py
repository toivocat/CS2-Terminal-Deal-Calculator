from PIL import Image
import pyautogui
import keyboard
from steam_community_market import Market
from PytesseractImplementation import ImageReader, OS
import numpy as np
import difflib
import re
import ui_server


market = Market("USD")
WearList = ["Minimal Wear", "Factory New", "Field-Tested", "Well-Worn", "Battle-Scarred"]
SkinList = ["Driver Gloves | Garden", "Driver Gloves | Wave Chaser", "Driver Gloves | Brocade Crane", "Driver Gloves | Brocade Flowers",
            "Driver Gloves | Hand Sweaters", "Driver Gloves | Dragon Fists", "Driver Gloves | Plum Quill", "Driver Gloves | Seigaiha",
            "Specialist Gloves | Cloud Chaser", "Specialist Gloves | Pillow Punchers", "Specialist Gloves | Lime Polycam",
            "Specialist Gloves | Blackbook", "Specialist Gloves | Big Swell", "Specialist Gloves | Sunburst",
            "Specialist Gloves | Chocolate Chesterfield", "Sport Gloves | Ultra Violent", "Sport Gloves | Occult", "Sport Gloves | Frosty",
            "Sport Gloves | Violet Beadwork", "Sport Gloves | Red Racer", "Sport Gloves | Blaze", "Sport Gloves | Creme Pinstripe",
            "AWP | Queen's Gambit", "Glock-18 | Fully Tuned", "AK-47 | Crane Flight", "P90 | Deathgaze", "P250 | Kintsugi",
            "M4A1-S | Electrum", "Desert Eagle | Firebreathing", "Galil AR | Galigator", "MP7 | Amberline", "MP9 | Urban Sovereign",
            "USP-S | Silent Shot", "M4A4 | Zubastick", "Five-SeveN | Dark Polymer", "PP-Bizon | RMX", "M249 | Bock Blocks",
            "UMP-45 | Fragment", "Sawed-Off | Fusion", "AK-47 | The Oligarch", "M4A4 | Full Throttle", "AWP | Ice Coaled",
            "MP7 | Smoking Kills", "Glock-18 | Mirror Mosaic", "M4A1-S | Liquidation", "MAC-10 | Cat Fight", "Dual Berettas | Angel Eyes",
            "Nova | Ocular", "UMP-45 | Continuum", "MP9 | Broken Record", "MP5-SD | Focus", "AUG | Trigger Discipline", "P2000 | Red Wing",
            "P250 | Bullfrog", "MAG-7 | MAGnitude", "SCAR-20 | Caged"]

def autocorrect(text, ACList):
    llist = [item.lower() for item in ACList]
    match = difflib.get_close_matches(text.lower(), llist, n=1, cutoff=0.35)
    if match:
        return ACList[llist.index(match[0])]
    return text

def BlackAndWhiteImage(image:str, result:str, value:int):
    img = Image.open(image).convert("L")
    img_array = np.array(img)
    img_array = np.where(img_array > value, 255, 0).astype(np.uint8)
    result_img = Image.fromarray(img_array)
    result_img.save(result)

# RUNNING THE TEXT RECOGNITION (and just about everything else)
def ScreenshotAndRecognition():
    ui_server.update(status="scanning")

    # Screenshot & scale down
    screenshot = pyautogui.screenshot()
    scaled = screenshot.resize((1920, 1080), Image.Resampling.LANCZOS) # MIGHT NEED TO CHANGE
    scaled.save("screenshot.png")

    # Make the cropped sections of the image
    # Name
    image = Image.open("screenshot.png")
    CroppedName = image.crop((770, 219, 1160, 243))
    CroppedName.save("croppedName.png")
    # Wear
    CroppedWear = image.crop((769, 784, 988, 814))
    CroppedWear.save("croppedWear.png")
    # Price
    CroppedPrice = image.crop((282, 952, 546, 1001))
    CroppedPrice.save("croppedPrice.png")

    # Make the wear and price more readable
    BlackAndWhiteImage("croppedWear.png", "wearResult.png", 100)
    BlackAndWhiteImage("croppedPrice.png", "priceResult.png", 75)

    # Read the image
    ir = ImageReader(OS.Windows)
    NameText = ir.extract_text("croppedName.png", lang="eng") # CHANGE TO ACTUAL SCREENSHOT NAME LATER
    WearText = ir.extract_text("wearResult.png", lang="eng") # CHANGE TO ACTUAL SCREENSHOT NAME LATER
    PriceText = ir.extract_text("priceResult.png", lang="eng")

    # Autocorrect
    Wear = autocorrect(WearText, WearList)
    Name = autocorrect(NameText, SkinList)
    Price = re.sub(r'[^0-9.-]', '', PriceText)

    print("Name: "+Name)

    # Print results for name & wear
    print("Name: "+Name)
    print("Wear: " + Wear)
    print("Offered Price: $"+Price)

    # Gets Item Price
    price = market.get_lowest_price(f"{Name} ({Wear})", 730)
    print("Market Price: $"+str(price))

    ui_server.update(
        name=Name,
        wear=Wear,
        offered_price=Price,
        market_price=str(price),
        status="done"
    )

keyboard.add_hotkey("F6", ScreenshotAndRecognition)
ui_server.start()

print("Press Ctrl+Alt+Esc to exit program...")
keyboard.wait("ctrl+alt+esc")
