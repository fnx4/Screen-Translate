import pyautogui
import os
import asyncio
import backend.Translate as tl
import backend.Capture as capture
import backend.JsonHandling as fJson
from backend.LangCode import *
from tkinter import *
from tkinter.tix import *
import tkinter.ttk as ttk
from Mbox import Mbox
dir_path = os.path.dirname(os.path.realpath(__file__))

# ----------------------------------------------------------------
# public func
def searchList(searchFor, theList):
    index = 0
    for lang in theList:
        if lang == searchFor:
            return index
        index += 1

def fillList(dictFrom, listTo, insertFirst, insertSecond = ""):
    for item in dictFrom:
        if item == "Auto-Detect":
            continue
        listTo += [item]

    listTo.sort()
    listTo.insert(0, insertFirst)
    if insertSecond != "":
        listTo.insert(1, insertSecond)

def offSetSettings(widthHeighOff, xyOffsetType, xyOff):
    offSetsGet = []
    x, y, w, h = 0, 0, 0, 0
    if widthHeighOff[0] == "auto":
        w = 60
    else:
        w = widthHeighOff[0]

    if widthHeighOff[1] == "auto":
        h = 60
    else:
        h = widthHeighOff[1]

    #  If offset is set
    if xyOffsetType.lower() != "no offset":
        offsetX = pyautogui.size().width
        offsetY = pyautogui.size().height
        
        # If auto
        if xyOff[0] == "auto":
            if(offsetX > offsetY): # Horizontal
                x = offsetX
            else:
                x = 0
        else: # if set manually
            x = xyOff[0]

        # If auto
        if xyOff[1] == "auto":
            if(offsetY > offsetX): # Vertical
                y = offsetY
            else:
                y = 0
        else: # if set manually
            y = xyOff[1]
    
    offSetsGet.append(x)
    offSetsGet.append(y)
    offSetsGet.append(w)
    offSetsGet.append(h)
    return offSetsGet

def getTheOffset():
    tStatus, settings = fJson.readSetting()

    offSetXY = settings["offSetXY"]
    offSetWH = settings["offSetWH"]
    xyOffSetType = settings["offSetXYType"]
    offSets = offSetSettings(offSetWH, xyOffSetType, offSetXY)

    return offSets

def console():
    print("-" * 80)
    print("Welcome to Screen Translate")
    print("Use The GUI Window to start capturing and translating")
    print("This window is for debugging purposes")

# ----------------------------------------------------------------
# Public var

# ----------------------------------------------------------------------
# Classes
class CaptureUI():
    """Capture Window"""
    root = Tk()
    alwaysOnTop = BooleanVar()
    alwaysOnTop.set(True)
    currOpacity = 0.8

    # Empty for padding purposes
    Label(root, text="").grid(row=0, column=0)
    Label(root, text="").grid(row=0, column=2)
    Label(root, text="").grid(row=0, column=3)
    Label(root, text="").grid(row=0, column=4)
    Label(root, text="").grid(row=0, column=5)
    Label(root, text="").grid(row=0, column=6)

    # Label for opacity slider
    opacityLabel = Label(root, text="Opacity: " + str(currOpacity))
    opacityLabel.grid(row=0, column=7, sticky='w')

    # Show/Hide
    def show(self):
        main_Menu.capUiHidden = False
        self.root.wm_deiconify()
    
    def on_closing(self):
        main_Menu.capUiHidden = True
        self.root.wm_withdraw()

    # Slider function
    root.attributes('-alpha', 0.8)
    def sliderOpac(self, x):
        self.root.attributes('-alpha', x)
        self.opacityLabel.config(text="Opacity: " + str(round(float(x), 2)))
        self.currOpacity = x

        main_Menu.captureOpacityLabel.config(text="Capture UI Opacity: " + str(round(float(x), 2)))

    # Capture the text
    def getTextAndTranslate(self, offSetXY=["auto", "auto"]):
        if(main_Menu.capUiHidden): # If Hidden
            Mbox("Error: You need to generate the capture window", "Please generate the capture window first", 0)
            print("Error Need to generate the capture window! Please generate the capture window first")
            return
        if(main_Menu.CBLangFrom.current()) == (main_Menu.CBLangTo.current()): # If Selected type invalid
            Mbox("Error: Language target is the same as source", "Please choose a different language", 0)
            print("Error Language is the same as source! Please choose a different language")
            return
        if main_Menu.CBLangTo.get() == "Auto-Detect" or main_Menu.CBLangTo.current() == 0 or main_Menu.CBLangFrom.get() == "Auto-Detect" or main_Menu.CBLangFrom.current() == 0: # If Selected type invalid
            Mbox("Error: Invalid Language Selected", "Can't Use Auto Detect in Capture Mode", 0)
            print("Error: Invalid Language Selected! Can't Use Auto Detect in Capture Mode")
            return
        
        # Hide the Capture Window so it can detect the words better
        opacBefore = self.currOpacity
        self.root.attributes('-alpha', 0)
        
        # Get xywh of the screen
        x, y, w, h = self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width(), self.root.winfo_height()

        # Get settings
        tStatus, settings = fJson.readSetting()
        if tStatus == False: # If error its probably file not found, thats why we only handle the file not found error
            if settings[0] == "Setting file is not found":
                self.root.wm_withdraw()  # Hide the capture window

                # Show error
                print("Error: " + settings[0])
                print(settings[1])
                Mbox("Error: " + settings[0], settings[1], 0)
                
                # Set Default
                var1, var2 = fJson.setDefault()
                if var1 : # If successfully set default
                    print("Default setting applied")
                    Mbox("Default setting applied", "Please change your tesseract location in setting if you didn't install tesseract on default C location", 0)
                else: # If error
                    print("Error: " + var2)
                    Mbox("An Error Occured", var2, 0)
                
                self.root.wm_deiconify()  # Show the capture window
                return # Reject
        
        # If tesseract is not found
        if settings['tesseract_loc'] == "" or "tesseract" in settings['tesseract_loc'] == False:
            self.root.wm_withdraw()  # Hide the capture window
            x = Mbox("Error: Tesseract Not Set!", "Please set tesseract_loc in Setting.json.\nYou can set this in setting menu or modify it manually in resource/backend/json/Setting.json", 0)
            self.root.wm_deiconify()  # Show the capture window
            
            return # Reject

        # Store setting to localvar
        offSetXY = settings["offSetXY"]
        offSetWH = settings["offSetWH"]
        xyOffSetType = settings["offSetXYType"]

        offSets = offSetSettings(offSetWH, xyOffSetType, offSetXY)
        x += offSets[0]
        y += offSets[1]
        w += offSets[2]
        h += offSets[3]

        # Capture the screen
        coords = [x, y, w, h]

        language = main_Menu.CBLangFrom.get()
        is_Success, result = capture.captureImg(coords, language, settings['tesseract_loc'], settings['cached'])
        self.root.attributes('-alpha', opacBefore)
        
        print("Area Captured Successfully!") # Debug Print
        print("Coordinates: " + str(coords)) # Debug Print

        if is_Success == False or len(result) == 1:
            print("But Failed to capture any text!")
            Mbox("Error", "Failed to Capture Text!", 0)
        else:
            main_Menu.root.deiconify()

            # Pass it to mainMenu
            main_Menu.textBoxTop.delete(1.0, END)
            main_Menu.textBoxTop.insert(END, result[:-1]) # Delete last character

            # Run the translate function
            main_Menu.translate(main_Menu, result[:-1])

    # ----------------------------------------------------------------------
    def __init__(self):
        self.root.title('Text Capture Area')
        self.root.geometry('500x150')
        self.root.wm_attributes('-topmost', True)
        self.Hidden = False
        
        # Menubar
        def always_on_top():
            if self.alwaysOnTop.get(): # IF ON THEN TURN IT OFF
                self.root.wm_attributes('-topmost', True)
            else: # IF OFF THEN TURN IT ON
                self.root.wm_attributes('-topmost', False)

        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_checkbutton(label="Always on Top", onvalue=True, offvalue=False, variable=self.alwaysOnTop, command=always_on_top)
        menubar.add_cascade(label="Options", menu=filemenu)

        # Add to self.root
        self.root.config(menu=menubar)

        # Button
        captureBtn = Button(self.root, text="Capture And Translate", command=self.getTextAndTranslate)
        captureBtn.grid(row=0, column=1, sticky='e')

        # opacity slider # the slider will be added to main menu not here
        opacitySlider = ttk.Scale(self.root, from_=0.01, to=1.0, value=self.currOpacity, orient=HORIZONTAL, command=self.sliderOpac)
        opacitySlider.grid(row=0, column=4, sticky='e')

        # On Close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

# ----------------------------------------------------------------------
class SettingUI():
    """Setting Window"""
    root = Tk()

    def show(self):
        self.root.wm_deiconify()

    def on_closing(self):
        self.root.wm_withdraw()

    def checkBtnX():
        offSets = getTheOffset()

        if main_Menu.setting.root.getvar(name="checkVarOffSetX") == "1":
            main_Menu.setting.spinnerOffSetX.config(state=DISABLED)
            main_Menu.setting.spinValOffSetX.set(str(offSets[0]))
        else:
            main_Menu.setting.spinnerOffSetX.config(state=NORMAL)

    def checkBtnY():
        offSets = getTheOffset()

        if main_Menu.setting.root.getvar(name="checkVarOffSetY") == "1":
            main_Menu.setting.spinnerOffSetY.config(state=DISABLED)
            main_Menu.setting.spinValOffSetY.set(str(offSets[1]))
        else:
            main_Menu.setting.spinnerOffSetY.config(state=NORMAL)

    def checkBtnW():
        offSets = getTheOffset()

        if main_Menu.setting.root.getvar(name="checkVarOffSetW") == "1":
            main_Menu.setting.spinnerOffSetW.config(state=DISABLED)
            main_Menu.setting.spinValOffSetW.set(str(offSets[2]))
        else:
            main_Menu.setting.spinnerOffSetW.config(state=NORMAL)

    def checkBtnH():
        offSets = getTheOffset()

        if main_Menu.setting.root.getvar(name="checkVarOffSetH") == "1":
            main_Menu.setting.spinnerOffSetH.config(state=DISABLED)
            main_Menu.setting.spinValOffSetH.set(str(offSets[3]))
        else:
            main_Menu.setting.spinnerOffSetH.config(state=NORMAL)

    def screenShotAndOpenLayout(self = ""):
        
        pass

    def restoreDefault(self = ""):

        pass

    def saveSettings(self = ""):
        
        pass
        
    def CBOffSetChange(self, event = ""):
        offSets = getTheOffset()
        xyOffSetType = self.CBOffSetChoice.get()

        # Check offset or not
        if xyOffSetType == "No Offset":
            # Select auto
            self.checkAutoOffSetX.select()
            self.checkAutoOffSetY.select()
            # Disable spinner and the selector, also set stuff in spinner to 0
            self.checkAutoOffSetX.config(state=DISABLED)
            self.checkAutoOffSetY.config(state=DISABLED)
            self.spinnerOffSetX.config(state=DISABLED)
            self.spinValOffSetX.set("0")
            self.spinnerOffSetY.config(state=DISABLED)
            self.spinValOffSetY.set("0")
        else:
            # Disselect auto
            self.checkAutoOffSetX.select()
            self.checkAutoOffSetY.select()
            # Make checbtn clickable, but set auto which means spin is disabled
            self.checkAutoOffSetX.config(state=NORMAL)
            self.checkAutoOffSetY.config(state=NORMAL)
            self.spinValOffSetX.set(str(offSets[0]))
            self.spinValOffSetY.set(str(offSets[1]))
            self.spinnerOffSetX.config(state=DISABLED)
            self.spinnerOffSetY.config(state=DISABLED)

    # Frames
    firstFrame = Frame(root)
    firstFrame.pack(side=TOP, fill=X, expand=False)
    firstFrameContent = Frame(root)
    firstFrameContent.pack(side=TOP, fill=X, expand=False)

    secondFrame = Frame(root)
    secondFrame.pack(side=TOP, fill=X, expand=False)
    secondFrameContent0 = Frame(root)
    secondFrameContent0.pack(side=TOP, fill=X, expand=False)
    secondFrameContent1 = Frame(root)
    secondFrameContent1.pack(side=TOP, fill=X, expand=False)
    secondFrameContent2 = Frame(root)
    secondFrameContent2.pack(side=TOP, fill=X, expand=False)
    secondFrameContent3 = Frame(root)
    secondFrameContent3.pack(side=TOP, fill=X, expand=False)
    secondFrameContent4 = Frame(root)
    secondFrameContent4.pack(side=TOP, fill=X, expand=False)

    thirdFrame = Frame(root)
    thirdFrame.pack(side=TOP, fill=X, expand=False)
    thirdFrameContent = Frame(root)
    thirdFrameContent.pack(side=TOP, fill=X, expand=False)

    fourthFrame = Frame(root)
    fourthFrame.pack(side=TOP, fill=X, expand=False)
    fourthFrameContent = Frame(root)
    fourthFrameContent.pack(side=TOP, fill=X, expand=False)

    bottomFrame = Frame(root)
    bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=False)

    # First Frame
    labelImg = Label(firstFrame, text="Image Setting")
    checkVarCache = BooleanVar(root, name="checkVarCache", value=True) # So its not error
    checkBTNCache = Checkbutton(firstFrameContent, text="Cached", variable=checkVarCache)
    btnOpenCacheFolder = Button(firstFrameContent, text="Open Cache Folder", command=lambda: os.startfile(dir_path + r"\backend\img_cache"))

    # Second Frame
    labelMonitor = Label(secondFrame, text="Monitor Capture Offset")
    checkVarOffSetX = BooleanVar(root, name="checkVarOffSetX", value=True)
    checkVarOffSetY = BooleanVar(root, name="checkVarOffSetY", value=True)
    checkVarOffSetW = BooleanVar(root, name="checkVarOffSetW", value=True)
    checkVarOffSetH = BooleanVar(root, name="checkVarOffSetH", value=True)
    CBOffSetChoice = ttk.Combobox(secondFrameContent0, values=["No Offset", "Custom Offset"], state="readonly")

    labelCBOffsetNot = Label(secondFrameContent0, text="Capture XY Offset :")
    labelOffSetX = Label(secondFrameContent2, text="Offset X :")
    labelOffSetY = Label(secondFrameContent3, text="Offset Y :")
    labelOffSetW = Label(secondFrameContent2, text="Offset W :")
    labelOffSetH = Label(secondFrameContent3, text="Offset H :")

    checkAutoOffSetX = Checkbutton(secondFrameContent1, text="Auto Offset X", variable=checkVarOffSetX, command=checkBtnX)
    checkAutoOffSetY = Checkbutton(secondFrameContent1, text="Auto Offset Y", variable=checkVarOffSetY, command=checkBtnY)
    checkAutoOffSetW = Checkbutton(secondFrameContent1, text="Auto Offset W", variable=checkVarOffSetW, command=checkBtnW)
    checkAutoOffSetH = Checkbutton(secondFrameContent1, text="Auto Offset H", variable=checkVarOffSetH, command=checkBtnH)

    spinValOffSetX = StringVar(root)
    spinValOffSetY = StringVar(root)
    spinValOffSetW = StringVar(root)
    spinValOffSetH = StringVar(root)

    spinnerOffSetX = Spinbox(secondFrameContent2, from_=0, to=100000, width=20, textvariable=spinValOffSetX)
    spinnerOffSetY = Spinbox(secondFrameContent3, from_=0, to=100000, width=20, textvariable=spinValOffSetY)
    spinnerOffSetW = Spinbox(secondFrameContent2, from_=0, to=100000, width=20, textvariable=spinValOffSetW)
    spinnerOffSetH = Spinbox(secondFrameContent3, from_=0, to=100000, width=20, textvariable=spinValOffSetH)

    buttonCheckMonitorLayout = Button(secondFrameContent4, text="Click to get A Screenshot of How The Program See Your Monitor")

    # Third frame
    engines = engineList
    optGoogle = []
    fillList(google_Lang, optGoogle, "Auto-Detect")
    optDeepl = []
    fillList(deepl_Lang, optDeepl, "Auto-Detect")
    langOpt = optGoogle

    labelTl = Label(thirdFrame, text="Translation")
    CBDefaultEngine = ttk.Combobox(thirdFrameContent, values=engines, state="readonly")
    CBDefaultFrom = ttk.Combobox(thirdFrameContent, values=langOpt, state="readonly")
    CBDefaultTo = ttk.Combobox(thirdFrameContent, values=langOpt, state="readonly")
    labelDefaultEngine = Label(thirdFrameContent, text="Default Engine :")
    labelDefaultFrom = Label(thirdFrameContent, text="Default From :")
    labelDefaultTo = Label(thirdFrameContent, text="Default To :")

    # Fourth frame
    labelTesseract = Label(fourthFrame, text="Tesseract")
    labelTesseractPath = Label(fourthFrameContent, text="Tesseract Path :")
    textBoxTesseractPath = Text(fourthFrameContent, width=50, height=1)

    # Bottom Frame
    btnRestoreDefault = Button(bottomFrame, text="Restore Default", command=restoreDefault)
    btnSave = Button(bottomFrame, text="Save Settings", command=saveSettings)

    # ----------------------------------------------------------------------
    def __init__(self):
        self.root.title("Setting")
        self.root.geometry("750x420")
        self.root.wm_attributes('-topmost', False) # Default False
        # self.root.wm_withdraw()

        # Get settings on startup
        tStatus, settings = fJson.readSetting()
        if tStatus == False: # If error its probably file not found, thats why we only handle the file not found error
            if settings[0] == "Setting file is not found":
                self.root.wm_withdraw()  # Hide setting

                # Show error
                print("Error: " + settings[0])
                print(settings[1])
                Mbox("Error: " + settings[0], settings[1], 0)
                
                settings = fJson.default_Setting

                # Set Default
                var1, var2 = fJson.setDefault()
                if var1 : # If successfully set default
                    print("Default setting applied")
                    Mbox("Default setting applied", "Please change your tesseract location in setting if you didn't install tesseract on default C location", 0)
                else: # If error
                    print("Error: " + var2)
                    Mbox("An Error Occured", var2, 0)
                
                self.root.wm_deiconify()  # Show setting
        
        # If tesseract is not found
        if settings['tesseract_loc'] == "" or "tesseract" in settings['tesseract_loc'] == False:
            x = Mbox("Error: Tesseract Not Set!", "Please set tesseract_loc in Setting.json.\nYou can set this in setting menu or modify it manually in resource/backend/json/Setting.json", 0)
        
        # Cache checkbox
        if settings['cached'] == True:
            self.root.setvar(name="checkVarCache", value=True)
            self.checkBTNCache.select()
        else:
            self.root.setvar(name="checkVarCache", value=False)
            self.checkBTNCache.deselect()

        # Store setting to localvar
        offSetXY = settings["offSetXY"]
        offSetWH = settings["offSetWH"]
        xyOffSetType = settings["offSetXYType"]

        offSets = offSetSettings(offSetWH, xyOffSetType, offSetXY)
        x = offSets[0]
        y = offSets[1]
        w = offSets[2]
        h = offSets[3]

        if xyOffSetType == "No Offset":
            self.CBOffSetChoice.current(0)
            self.checkAutoOffSetX.config(state=DISABLED)
            self.checkAutoOffSetY.config(state=DISABLED)
            self.spinnerOffSetX.config(state=DISABLED)
            self.spinValOffSetX.set("0")
            self.spinnerOffSetY.config(state=DISABLED)
            self.spinValOffSetY.set("0")

            self.checkAutoOffSetX.deselect()
            self.root.setvar(name="checkVarOffSetX", value=False)
            self.checkAutoOffSetY.deselect()
            self.root.setvar(name="checkVarOffSetY", value=False)

        elif xyOffSetType == "Custom Offset":
            self.CBOffSetChoice.current(1)
            self.spinValOffSetX.set(str(x))
            self.spinValOffSetY.set(str(y))

            if offSetXY[0] == "auto":
                self.checkAutoOffSetX.select()
                self.root.setvar(name="checkVarOffSetX", value=True)
                self.spinnerOffSetX.config(state=DISABLED)
            else:
                self.checkAutoOffSetX.deselect()
                self.root.setvar(name="checkVarOffSetX", value=False)
                self.spinnerOffSetX.config(state=NORMAL)

            if offSetXY[1] == "auto":
                self.checkAutoOffSetY.select()
                self.root.setvar(name="checkVarOffSetY", value=True)
                self.spinnerOffSetY.config(state=DISABLED)
            else:
                self.checkAutoOffSetY.deselect()
                self.root.setvar(name="checkVarOffSetY", value=False)
                self.spinnerOffSetY.config(state=NORMAL)
        else:
            self.CBOffSetChoice.current(0)
            print("Error: Invalid Offset Type")
            Mbox("Error: Invalid Offset Type", "Please do not modify the setting manually if you don't know what you are doing", 0)
        
        # W H
        self.spinValOffSetW.set(str(w))
        self.spinValOffSetH.set(str(h))

        if(settings["offSetWH"][0] == "auto"):
            self.checkAutoOffSetW.select()
            self.root.setvar(name="checkVarOffSetW", value=True)
            self.spinnerOffSetW.config(state=DISABLED)
        else:
            self.checkAutoOffSetW.deselect()
            self.root.setvar(name="checkVarOffSetW", value=False)
            self.spinnerOffSetW.config(state=NORMAL)
        
        if(settings["offSetWH"][1] == "auto"):
            self.checkAutoOffSetH.select()
            self.root.setvar(name="checkVarOffSetH", value=True)
            self.spinnerOffSetH.config(state=DISABLED)
        else:
            self.checkAutoOffSetH.deselect()
            self.root.setvar(name="checkVarOffSetH", value=False)
            self.spinnerOffSetH.config(state=NORMAL)

        # Init element
        # 1
        self.labelImg.pack(side=LEFT, padx=5, pady=5, fill=X)
        self.checkBTNCache.pack(side=LEFT, padx=5, pady=5)
        self.btnOpenCacheFolder.pack(side=LEFT, padx=5, pady=5)

        # 2
        self.labelMonitor.pack(side=LEFT, fill=X, padx=5, pady=5)

        self.labelCBOffsetNot.pack(side=LEFT, padx=5, pady=5)
        self.CBOffSetChoice.pack(side=LEFT, padx=5, pady=5)
        self.CBOffSetChoice.bind("<<ComboboxSelected>>", self.CBOffSetChange)

        self.checkAutoOffSetX.pack(side=LEFT, padx=5, pady=5)
        self.checkAutoOffSetY.pack(side=LEFT, padx=5, pady=5)
        self.checkAutoOffSetW.pack(side=LEFT, padx=5, pady=5)
        self.checkAutoOffSetH.pack(side=LEFT, padx=5, pady=5)

        self.labelOffSetX.pack(side=LEFT, padx=5, pady=5)
        self.spinnerOffSetX.pack(side=LEFT, padx=5, pady=5)
        self.labelOffSetY.pack(side=LEFT, padx=5, pady=5)
        self.spinnerOffSetY.pack(side=LEFT, padx=5, pady=5)

        self.labelOffSetW.pack(side=LEFT, padx=5, pady=5)
        self.spinnerOffSetW.pack(side=LEFT, padx=5, pady=5)
        self.labelOffSetH.pack(side=LEFT, padx=5, pady=5)
        self.spinnerOffSetH.pack(side=LEFT, padx=8, pady=5)
        
        self.buttonCheckMonitorLayout.pack(side=LEFT, padx=30, pady=5)

        # 3
        self.labelTl.pack(side=LEFT, padx=5, pady=5, fill=X)

        self.labelDefaultEngine.pack(side=LEFT, padx=5, pady=5)
        self.CBDefaultEngine.pack(side=LEFT, padx=5, pady=5)

        self.labelDefaultFrom.pack(side=LEFT, padx=5, pady=5)
        self.CBDefaultFrom.pack(side=LEFT, padx=5, pady=5)

        self.labelDefaultTo.pack(side=LEFT, padx=5, pady=5)
        self.CBDefaultTo.pack(side=LEFT, padx=5, pady=5)
        
        # 4
        self.labelTesseract.pack(side=LEFT, padx=5, pady=5, fill=X)
        self.labelTesseractPath.pack(side=LEFT, padx=5, pady=5)
        self.textBoxTesseractPath.pack(side=LEFT, padx=5, pady=5)

        # Bottom Frame
        self.btnSave.pack(side=RIGHT, padx=5, pady=5)
        self.btnRestoreDefault.pack(side=RIGHT, padx=5, pady=5)
        
        # On Close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

# ----------------------------------------------------------------------
class main_Menu():
    """Main Menu Window"""
    console()

    # --- Functions ---
    async def getDeeplTl(self, text, langTo, langFrom):
        """Get the translated text from deepl.com"""
        TBottom = self.textBoxBottom

        isSuccess, translateResult = await tl.deepl_tl(text, langTo, langFrom)
        if(isSuccess):
            TBottom.delete(1.0, END)
            TBottom.insert(1.0, translateResult)
        else:
            Mbox("Error: Translation Failed", translateResult, 0)

    # Translate
    def translate(self, textOutside = ""):
        """Translate the text"""
        # Get language
        langFromObj = self.CBLangFrom
        langToObj = self.CBLangTo
        langFrom = self.CBLangFrom.get()
        langTo = self.CBLangTo.get()

        # Get the engine from the combobox
        engine = self.CBTranslateEngine.get()

        # Get Textbox
        TBBot = self.textBoxBottom

        if(langFromObj.current()) == (langToObj.current()):
            Mbox("Error: Language target is the same as source", "Please choose a different language", 0)
            print("Error Language is the same as source! Please choose a different language")
            return
        if langToObj.get() == "Auto-Detect" or langToObj.current() == 0:
            Mbox("Error: Invalid Language Selected", "Please choose a valid language", 0)
            print("Error: Invalid Language Selected! Please choose a valid language")
            return

        # Get the text from the textbox
        if textOutside == "":
            text = self.textBoxTop.get(1.0, END)
        else:
            text = textOutside

        if(len(text) < 2):
            Mbox("Error: No text entered", "Please enter some text", 0)
            print("Error: No text entered! Please enter some text")
            return

        # Translate
        if engine == "Google Translate":
            isSuccess, translateResult = tl.google_tl(text, langTo, langFrom)
            if(isSuccess):
                TBBot.delete(1.0, END)
                TBBot.insert(1.0, translateResult)
            else:
                Mbox("Error: Translation Failed", translateResult, 0)
        elif engine == "Deepl":
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.getDeeplTl(text, langTo, langFrom, TBBot))
        else:
            Mbox("Error: Engine Not Set!", "Please Please select a correct engine", 0)
            print("Please select a correct engine")

    # On Close
    def on_closing(self):
        exit(0)
    
    # Open History Window
    def open_History(self):
        self.setting.show()

    # Open Capture Window
    def open_capture_screen(self):
        self.capture_UI.show()

    def swapTl(self):
        # Get Before
        topBefore = self.textBoxTop.get(1.0, END)
        botBefore = self.textBoxBottom.get(1.0, END)
        # Delete
        self.textBoxTop.delete(1.0, END)
        self.textBoxBottom.delete(1.0, END)
        # Insert
        if len(topBefore) > 1:
            self.textBoxBottom.insert(1.0, topBefore[:-1])
        if len(botBefore) > 1:
            self.textBoxTop.insert(1.0, botBefore[:-1])

        # The Comboboxes
        x, y = self.CBLangFrom.current(), self.CBLangTo.current()
        self.CBLangFrom.current(y)
        self.CBLangTo.current(x) 

    # Clear TB
    def clearTB(self):
        self.textBoxTop.delete(1.0, END)
        self.textBoxBottom.delete(1.0, END)

    def tbChange(self, event = ""):
        # Get the engine from the combobox
        curr_Engine = self.CBTranslateEngine.get()

        # Translate
        if curr_Engine == "Google Translate":
            self.langOpt = self.optGoogle
            self.CBLangFrom['values'] = self.optGoogle
            self.CBLangFrom.current(0)
            self.CBLangTo['values'] = self.optGoogle
            self.CBLangTo.current(searchList("English", self.optDeepl))
        elif curr_Engine == "Deepl":
            self.langOpt = self.optDeepl
            self.CBLangFrom['values'] = self.optDeepl
            self.CBLangFrom.current(0)
            self.CBLangTo['values'] = self.optDeepl
            self.CBLangTo.current(searchList("English", self.optDeepl))

    # --- Declarations and Layout ---
    # Call the other frame
    capture_UI = CaptureUI()
    setting = SettingUI()

    root = Tk()
    alwaysOnTop = False
    capUiHidden = False

    # Frame
    topFrame1 = Frame(root)
    topFrame1.pack(side=TOP, fill=X, expand=False)

    topFrame2 = Frame(root)
    topFrame2.pack(side=TOP, fill=BOTH, expand=True)

    bottomFrame1 = Frame(root)
    bottomFrame1.pack(side=TOP, fill=X, expand=False)

    bottomFrame2 = Frame(root)
    bottomFrame2.pack(side=BOTTOM, fill=BOTH, expand=True)

    # Capture Opacity topFrame1
    captureOpacitySlider = ttk.Scale(topFrame1, from_=0.01, to=1.0, value=capture_UI.currOpacity, orient=HORIZONTAL, command=capture_UI.sliderOpac)
    captureOpacityLabel = Label(topFrame1, text="Capture UI Opacity: " + str(capture_UI.currOpacity))

    engines = engineList
    optGoogle = []
    fillList(google_Lang, optGoogle, "Auto-Detect")
    optDeepl = []
    fillList(deepl_Lang, optDeepl, "Auto-Detect")
    langOpt = optGoogle # Will be overwritten in innit

    labelEngines = Label(bottomFrame1, text="TL Engine:")
    CBTranslateEngine = ttk.Combobox(bottomFrame1, values=engines, state="readonly")

    labelLangFrom = Label(bottomFrame1, text="From:")
    CBLangFrom = ttk.Combobox(bottomFrame1, values=langOpt, state="readonly")

    labelLangTo = Label(bottomFrame1, text="To:")
    CBLangTo = ttk.Combobox(bottomFrame1, values=langOpt, state="readonly")

    translateOnly_Btn = Button()
    captureNTranslate_Btn = Button()
    clearBtn = Button()
    swapBtn = Button()

    # Translation Textbox topFrame2 & bottomFrame2
    textBoxTop = Text(topFrame2, height = 5, width = 100, font=("Segoe UI", 10), yscrollcommand=True)
    textBoxBottom = Text(bottomFrame2, height = 5, width = 100, font=("Segoe UI", 10), yscrollcommand=True)

    # ----------------------------------------------------------------------
    def __init__(self):
        self.root.title("Screen Translate - Main Menu")
        self.root.geometry("900x300")
        self.root.wm_attributes('-topmost', False) # Default False
        tStatus, settings = fJson.readSetting()
        if tStatus == False: # If error its probably file not found, thats why we only handle the file not found error
            if settings[0] == "Setting file is not found":
                # Show error
                print("Error: " + settings[0])
                print(settings[1])
                Mbox("Error: " + settings[0], settings[1], 0)

                # Set setting value to default, so program can run
                settings = fJson.default_Setting

                # Set Default
                var1, var2 = fJson.setDefault()
                if var1 : # If successfully set default
                    print("Default setting applied")
                    Mbox("Default setting applied", "Please change your tesseract location in setting if you didn't install tesseract on default C location", 0)
                else: # If error
                    print("Error: " + var2)
                    Mbox("An Error Occured", var2, 0)

        elif settings['tesseract_loc'] == "" or "tesseract" in settings['tesseract_loc'] == False:
            Mbox("Error: Tesseract Not Set!", "Please set tesseract_loc in Setting.json.\nYou can set this in setting menu or modify it manually in resource/backend/json/Setting.json", 0)
        
        # Menubar
        def always_on_top():
            if self.alwaysOnTop:
                self.root.wm_attributes('-topmost', False)
                self.alwaysOnTop = False
            else:
                self.root.wm_attributes('-topmost', True)
                self.alwaysOnTop = True

        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_checkbutton(label="Always on Top", command=always_on_top)
        filemenu.add_separator()
        filemenu.add_command(label="Exit Application", command=self.root.quit)
        menubar.add_cascade(label="Options", menu=filemenu)

        filemenu2 = Menu(menubar, tearoff=0)
        filemenu2.add_command(label="History", command=self.open_History) # Open History Window
        filemenu2.add_command(label="Setting") # Open Setting Window
        menubar.add_cascade(label="View", menu=filemenu2)

        filemenu3 = Menu(menubar, tearoff=0)
        filemenu3.add_command(label="Capture Window", command=self.open_capture_screen) # Open Capture Screen Window
        menubar.add_cascade(label="Generate", menu=filemenu3)

        filemenu4 = Menu(menubar, tearoff=0)
        filemenu4.add_command(label="Tutorials") # Open Mbox Tutorials
        filemenu4.add_command(label="FAQ") # Open Mbox Tutorials
        filemenu4.add_separator()
        filemenu4.add_command(label="About") # Open Mbox About
        menubar.add_cascade(label="Help", menu=filemenu4)

        # Add to self.root
        self.root.config(menu=menubar)

        # topFrame1
        translateOnly_Btn = Button(self.topFrame1, text="Translate", command=self.translate)
        captureNTranslate_Btn = Button(self.topFrame1, text="Capture And Translate", command=self.capture_UI.getTextAndTranslate)
        translateOnly_Btn.pack(side=LEFT, padx=5, pady=5)
        captureNTranslate_Btn.pack(side=LEFT, padx=5, pady=5)

        # topFrame1
        self.captureOpacitySlider.pack(side=LEFT, padx=5, pady=5)
        self.captureOpacityLabel.pack(side=LEFT, padx=5, pady=5)

        # bottomFrame1
        self.labelEngines.pack(side=LEFT, padx=5, pady=5)
        self.CBTranslateEngine.current(searchList(settings['default_Engine'], self.engines))
        self.CBTranslateEngine.pack(side=LEFT, padx=5, pady=5)
        self.CBTranslateEngine.bind("<<ComboboxSelected>>", self.tbChange)

        self.tbChange() # Update the cb

        self.labelLangFrom.pack(side=LEFT, padx=5, pady=5)
        self.CBLangFrom.current(searchList(settings['default_FromOnOpen'], self.langOpt))
        self.CBLangFrom.pack(side=LEFT, padx=5, pady=5)

        self.labelLangTo.pack(side=LEFT, padx=5, pady=5)
        self.CBLangTo.current(searchList(settings['default_ToOnOpen'], self.langOpt)) # Default to English
        self.CBLangTo.pack(side=LEFT, padx=5, pady=5)

        # Button bottomFrame1
        self.clearBtn = Button(self.bottomFrame1, text="Clear", command=self.clearTB)
        self.swapBtn = Button(self.bottomFrame1, text="Swap", command=self.swapTl)
        self.swapBtn.pack(side=LEFT, padx=5, pady=5)
        self.clearBtn.pack(side=LEFT, padx=5, pady=5)

        # Translation Textbox topFrame2 bottomFrame
        self.textBoxTop.pack(padx=5, pady=5, fill=BOTH, expand=True)
        self.textBoxBottom.pack(padx=5, pady=5, fill=BOTH, expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

main_Menu()
main_Menu.root.mainloop()