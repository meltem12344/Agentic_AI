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
    {
        "type": "function",
        "function": {
            "name": "cikart",
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
# C. AJAN DÖNGÜSÜ (GÜNCELLENDİ: ARTIK HAFIZAYI DIŞARIDAN ALIYOR)
# ---------------------------------------------------------
# Artık 'messages' listesini parametre olarak alıyoruz!
def ajani_calistir(soru, chat_gecmisi):
    
    # 1. Kullanıcının sorusunu hafızaya ekle
    chat_gecmisi.append({"role": "user", "content": soru})

    # 2. İLK TUR
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat_gecmisi, # Güncel hafızayı gönderiyoruz
        tools=tools
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 3. KARAR ANI
    if tool_calls:
        print(f"🤖 AI KARARI: {len(tool_calls)} adet işlem yapılacak.")
        chat_gecmisi.append(response_message) # Modelin isteğini hafızaya kaydet

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_response = None

            if function_name == "hava_durumu_getir":
                function_response = hava_durumu_getir(sehir=function_args.get("sehir"))
            elif function_name == "cikart":
                function_response = cikart(sayi1=function_args.get("sayi1"), sayi2=function_args.get("sayi2"))
            
            # Sonucu hafızaya ekle
            chat_gecmisi.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

        print("\n⏳ Sonuçlar AI'ya gönderiliyor...")
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_gecmisi,
        )
        ai_cevabi = final_response.choices[0].message.content
        print(f"\n🤖 AJAN: {ai_cevabi}")
        
        # FİNAL CEVABI DA HAFIZAYA EKLE (Kritik Nokta!)
        chat_gecmisi.append({"role": "assistant", "content": ai_cevabi})
        
    else:
        # Eğer tool kullanmadıysa direkt cevabı yaz ve kaydet
        ai_cevabi = response_message.content
        print(f"\n🤖 AJAN: {ai_cevabi}")
        chat_gecmisi.append({"role": "assistant", "content": ai_cevabi})

# ---------------------------------------------------------
# D. SONSUZ DÖNGÜ (CHAT LOOP)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("--- AJAN BAŞLATILDI (Çıkmak için 'çık' yazın) ---")
    
    # 1. HAFIZA BURADA BAŞLIYOR (Döngünün Dışında!)
    # Böylece döngü her döndüğünde sıfırlanmıyor.
    hafiza = [
        {"role": "system", "content": "Sen yardımsever bir asistansın. Sohbeti hatırla."}
    ]

    while True:
        # 2. Kullanıcıdan girdi al
        kullanici_girdisi = input("\nSEN: ")
        
        # 3. Çıkış kontrolü
        if kullanici_girdisi.lower() in ["çık", "exit", "kapat"]:
            print("Görüşürüz! 👋")
            break
            
        # 4. Ajanı mevcut hafıza ile çağır
        # Dikkat: 'hafiza' listesi her turda büyüyerek geri gelecek
        ajani_calistir(kullanici_girdisi, hafiza)
