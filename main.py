import json # LLM ve Python farklı diller konuşur Python "dict" kullanır, LLM "text" kullanır. JSON bu ikisi arasındaki tercümandır diyebiliriz
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 1. Kasayı Aç (Anahtarı Yükle)
load_dotenv() # .env dosyasını okuyan fonksiyon
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # API key ini getenv() fonksiyonu ile alırız
                                                     # benim pc ile OpenAI sunucuları arasındaki köprüdür, hatı açtık ama şu an herhangi bir veri akışı olmuyor.




# ---------------------------------------------------------
# A. GERÇEK TOOL: İnternetten Hava Durumu Çeken Fonksiyon
# ---------------------------------------------------------
def hava_durumu_getir(sehir):
    """
    wttr.in servisine bağlanır ve gerçek hava durumunu getirir.
    """
    print(f"\n[SİSTEM] 🌍 '{sehir}' için internete bağlanılıyor (wttr.in)...")
    try:
        # format=%C+%t -> Bize "Parçalı Bulutlu +15°C" gibi temiz veri verir.
        url = f"https://wttr.in/{sehir}?format=%C+%t"
        response = requests.get(url)
        if response.status_code == 200:
            veri = response.text.strip()
            print(f"[BAŞARILI] ✅ Gelen Veri: {veri}")
            return json.dumps({"sehir": sehir, "durum": veri}) # bu fonksiyon veriyi metne çevirir çünkü LLM'ler sadece string okuyabılır
        else:
            return json.dumps({"error": "Veri çekilemedi."})
    except Exception as e:
        return json.dumps({"error": str(e)})

# ---------------------------------------------------------
# B. LLM'E TANITILACAK MENÜ (SCHEMA)
# ---------------------------------------------------------
# LLM yukarıda benim yazdığım kodu okuyamaz ona ne yapabileceğini anlatmamız lazım
# Aşağıdaki liste aslında LLM'e verdiğimiz bir "menü" gibidir. Yemek listesi gibi düşün ama burada fonksiyonlar var 
# Bu menüden decsription kısmı, tanımlanan fonksiyonun ne zaman LLM tarafından çağırılacağına karar vermek içindir. 
# mesela bu açıklama kısmına "sadece marstaki hava durumunu getir" diye bir şey yazılsaydı o zaman "ankara" dediğimizde LLM bu aracı kulanamazdı.

tools = [
    {
        "type": "function",
        "function": {
            "name": "hava_durumu_getir", # bu deger yukarıda tanımladıgmız fonksıyon adı ıle tıpatıp aynı olmalı!!
            "description": "Verilen şehrin anlık hava durumunu internetten öğrenir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sehir": {
                        "type": "string",
                        "description": "Şehir adı (örn: Istanbul, Ankara)"
                    }
                },
                "required": ["sehir"]
            }
        }
    }
]

# ---------------------------------------------------------
# C. AJAN DÖNGÜSÜ (BEYİN)
# ---------------------------------------------------------
def ajani_calistir(soru):
    print(f"\n🎤 SEN: {soru}")
    
    messages = [
        {"role": "system", "content": "Sen yardımsever bir asistansın. Hava durumunu öğrendikten sonra mutlaka giyim tavsiyesi ver."},
        {"role": "user", "content": soru}
    ]

    # 1. TUR: LLM Düşünüyor (Tool kullanmalı mıyım?)
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # <-- DİKKAT: En ucuz ve hızlı model!
        messages=messages,
        tools=tools
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 2. TUR: Eğer Tool İstediyse Çalıştır
    if tool_calls:
        print(f"🤖 AI KARARI: {len(tool_calls)} adet sorgu yapılması gerekiyor.")
        
        # Hafızaya AI'nın isteğini ekle
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "hava_durumu_getir":
                # Python fonksiyonunu biz çalıştırıyoruz
                function_response = hava_durumu_getir(
                    sehir=function_args.get("sehir")
                )
                
                # Sonucu hafızaya 'tool' rolüyle ekle
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })

        # 3. TUR: Sonuçlarla Birlikte Final Cevap
        print("\n⏳ Sonuçlar AI'ya gönderiliyor, yorum bekleniyor...")
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        print(f"\n🤖 FİNAL CEVAP:\n{final_response.choices[0].message.content}")
    else:
        print(f"🤖 CEVAP: {response_message.content}")

# --- TEST ETMEK İSTEDİĞİN SORUYU YAZ ---
if __name__ == "__main__":
    ajani_calistir("Arjantin'de mont giyeyim mi?")