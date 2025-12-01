import json
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 1. Kasa ve Anahtar
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------
# A. TOOLS (PYTHON FONKSİYONLARI)
# ---------------------------------------------------------
def hava_durumu_getir(sehir):
    print(f"\n[SİSTEM] 🌍 '{sehir}' için internete bağlanılıyor...")
    try:
        url = f"https://wttr.in/{sehir}?format=%C+%t"
        response = requests.get(url)
        if response.status_code == 200:
            veri = response.text.strip()
            return json.dumps({"sehir": sehir, "durum": veri})
        else:
            return json.dumps({"error": "Veri çekilemedi."})
    except Exception as e:
        return json.dumps({"error": str(e)})

# DÜZELTME 1: Fonksiyon adı İngilizce karakter (cikart)
# DÜZELTME 2: Mantık hatası düzeltildi (Toplama yapıyordu, çıkarma yaptık)
def cikart(sayi1, sayi2):
    print(f"\n[HESAP MAKİNESİ] 🧮 {sayi1} - {sayi2} işlemi yapılıyor...")
    return json.dumps({"sonuc": sayi1 - sayi2})

# ---------------------------------------------------------
# B. MENÜ (TOOLS SCHEMA)
# ---------------------------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "hava_durumu_getir",
            "description": "Verilen şehrin anlık hava durumunu öğrenir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sehir": {"type": "string", "description": "Şehir adı"}
                },
                "required": ["sehir"]
            }
        }
    },
    # İKİNCİ TOOL (ÇIKARMA)
    {
        "type": "function",
        "function": {
            "name": "cikart", # <--- DÜZELTME: 'ç' yerine 'c'
            "description": "Matematiksel çıkarma işlemi yapar. Bir sayıdan diğerini çıkartır.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sayi1": {"type": "integer"},
                    "sayi2": {"type": "integer"}
                },
                "required": ["sayi1", "sayi2"]
            }
        }
    }
]

# ---------------------------------------------------------
# C. AJAN DÖNGÜSÜ
# ---------------------------------------------------------
def ajani_calistir(soru):
    print(f"\n🎤 SEN: {soru}")
    
    messages = [
        {"role": "system", "content": "Sen yardımsever bir asistansın."},
        {"role": "user", "content": soru}
    ]

    # 1. TUR
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 2. TUR (KARAR ANI)
    if tool_calls:
        print(f"🤖 AI KARARI: {len(tool_calls)} adet işlem yapılacak.")
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Değişkeni baştan tanımlayalım ki hata almayalım
            function_response = None 

            if function_name == "hava_durumu_getir":
                function_response = hava_durumu_getir(
                    sehir=function_args.get("sehir")
                )
            
            # DÜZELTME: İsim eşleşmesi 'cikart' oldu
            elif function_name == "cikart":
                function_response = cikart(
                    sayi1=function_args.get("sayi1"), 
                    sayi2=function_args.get("sayi2")
                )
            
            # DÜZELTME 3: Değişken adı 'function_response' olarak standartlaştırıldı
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

        print("\n⏳ Sonuçlar AI'ya gönderiliyor...")
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        print(f"\n🤖 FİNAL CEVAP:\n{final_response.choices[0].message.content}")
    else:
        print(f"🤖 CEVAP: {response_message.content}")

# --- TEST ---
if __name__ == "__main__":
    # Test sorusu: Hem hava durumunu hem çıkarmayı test edebilirsin
    ajani_calistir("100'den 45 çıkartırsan kaç kalır?")