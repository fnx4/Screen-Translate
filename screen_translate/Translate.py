import requests
from screen_translate.Mbox import Mbox
from screen_translate.LangCode import *

# ----------------------------------------------------------------
# Imports Library
# Google Translate
try:
    from deep_translator import GoogleTranslator
except ConnectionError as e:
    print("Error: No Internet Connection. Please Restart With Internet Connected", str(e))
    Mbox("Error: No Internet Connection", str(e), 2)
except Exception as e:
    print("Error", str(e))
    Mbox("Error", str(e), 2)

# ----------------------------------------------------------------
# MyMemory Translate
try:
    from deep_translator import MyMemoryTranslator
except ConnectionError as e:
    print("Error: No Internet Connection. Please Restart With Internet Connected", str(e))
    Mbox("Error: No Internet Connection", str(e), 2)
except Exception as e:
    print("Error", str(e))
    Mbox("Error", str(e), 2)

# ----------------------------------------------------------------
# Pons
try:
    from deep_translator import PonsTranslator
except ConnectionError as e:
    print("Error: No Internet Connection. Please Restart With Internet Connected", str(e))
    Mbox("Error: No Internet Connection", str(e), 2)
except Exception as e:
    print("Error", str(e))
    Mbox("Error", str(e), 2)

__all__ = ["google_tl", "memory_tl", "pons_tl", "libre_tl"]


# ----------------------------------------------------------------
# TL Functions
# Google
def google_tl(text, to_lang, from_lang="auto", oldMethod = False):
    """Translate Using Google Translate

    Args:
        text ([str]): Text to translate
        to_lang ([type]): Language to translate
        from_lang (str, optional): [Language From]. Defaults to "auto".

    Returns:
        [type]: Translation result
    """
    is_Success = False
    result = ""
    # --- Get lang code --- 
    try:
        to_LanguageCode_Google = google_Lang[to_lang]
        from_LanguageCode_Google =  google_Lang[from_lang]
    except KeyError as e:
        print("Error: " + str(e))
        return is_Success, "Error Language Code Undefined"
    # --- Translate ---
    try:
        if not oldMethod:
            result = GoogleTranslator(source=from_LanguageCode_Google, target=to_LanguageCode_Google).translate(text.strip())
        else:
            url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl={}&tl={}&dt=t&q={}'.format(from_LanguageCode_Google, to_LanguageCode_Google, text.replace('\n', ' ').replace(' ', '%20').strip())
            result = requests.get(url).json()[0][0][0]        
        
        is_Success = True
    except Exception as e:
        print(str(e))
        result = str(e)
        Mbox("Error", str(e), 2)
    finally:
        print("-" * 50)
        print("Query: " + text.strip())
        print("-" * 50)
        print("Translation Get: "+ result)
        return is_Success, result

# My Mermory
def memory_tl(text, to_lang, from_lang="auto"):
    """Translate Using MyMemoryTranslator

    Args:
        text ([str]): Text to translate
        to_lang ([type]): Language to translate
        from_lang (str, optional): [Language From]. Defaults to "auto".

    Returns:
        [type]: Translation result
    """
    is_Success = False
    result = ""
    # --- Get lang code --- 
    try:
        to_LanguageCode_Memory = myMemory_Lang[to_lang]
        from_LanguageCode_Memory =  myMemory_Lang[from_lang]
    except KeyError as e:
        print("Error: " + str(e))
        return is_Success, "Error Language Code Undefined"
    # --- Translate ---
    try:
        result = MyMemoryTranslator(source=from_LanguageCode_Memory, target=to_LanguageCode_Memory).translate(text.strip())
        is_Success = True
    except Exception as e:
        print(str(e))
        result = str(e)
        Mbox("Error", str(e), 2)
    finally:
        print("-" * 50)
        print("Query: " + text.strip())
        print("-" * 50)
        print("Translation Get: "+ result)
        return is_Success, result

# PonsTranslator
def pons_tl(text, to_lang, from_lang):
    """Translate Using PONS

    Args:
        text ([str]): Text to translate
        to_lang ([type]): Language to translate
        from_lang (str, optional): [Language From]. Defaults to "auto".

    Returns:
        [type]: Translation result
    """
    is_Success = False
    result = ""
    # --- Get lang code --- 
    try:
        to_LanguageCode_Pons = pons_Lang[to_lang]
        from_LanguageCode_Pons =  pons_Lang[from_lang]
    except KeyError as e:
        print("Error: " + str(e))
        return is_Success, "Error Language Code Undefined"
    # --- Translate ---
    try:
        result = PonsTranslator(source=from_LanguageCode_Pons, target=to_LanguageCode_Pons).translate(text.strip())
        is_Success = True
    except Exception as e:
        print(str(e))
        result = str(e)
        Mbox("Error", str(e), 2)
    finally:
        print("-" * 50)
        print("Query: " + text.strip())
        print("-" * 50)
        print("Translation Get: "+ result)
        return is_Success, result

# LibreTranslator
def libre_tl(text, to_lang, from_lang, host="localhost", port="5000"):
    """Translate Using LibreTranslate
        Args:
            text ([str]): Text to translate
            to_lang ([type]): Language to translate
            from_lang (str, optional): [Language From]. Defaults to "auto".
            host ([str]): Server hostname
            port ([str]): Server port

        Returns:
            [type]: Translation result
    """
    is_Success = False
    result = ""
    # --- Get lang code ---
    try:
        to_LanguageCode_Libre = libre_Lang[to_lang]
        from_LanguageCode_Libre = libre_Lang[from_lang]
    except KeyError as e:
        print("Error: " + str(e))
        return is_Success, "Error Language Code Undefined"
    # --- Translate ---
    try:
        request = {
            "q": text,
            "source": from_LanguageCode_Libre,
            "target": to_LanguageCode_Libre,
            "format": "text"
        }
        adr = "http://" + host + ":" + port + "/translate"
        response = requests.post(adr, request).json()
        if "error" in response:
            result = response["error"]
        else:
            result = response["translatedText"]
            is_Success = True
    except Exception as e:
        print(str(e))
        result = str(e)
        Mbox("Error", str(e), 2)
    finally:
        print("-" * 50)
        print("Query: " + text.strip())
        print("-" * 50)
        print("Translation Get: " + result)
        return is_Success, result
