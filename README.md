#  hava_durumu_getir fonksiyonunun içini değiştirerek önceki haliyle karşılaştırmalar yaptım:

**Eski hava_durumu_getir fonksiyonu:** wttr.in servisine bağlanıp gerçek hava durumunu getiriyordu

**Yeni hava_durumu_getir fonksiyonu:** şimdi sahte bir veri return ettim bu fonksiyonda şu şekilde
                                     json.dumps({"sehir": sehir, "durum": "Gökten ateş topları yağıyor ve yerler lavla kaplı. Sıcaklık 800 derece."})

---

**OUTPUT:** 

🎤 SEN: İstanbul'da hava nasıl? Bu hafta sonu tura çıkalım mı?

🤖 AI KARARI: 1 adet sorgu yapılması gerekiyor.

[SİSTEM] Istanbul için sahte veri üretiliyor...

⏳ Sonuçlar AI'ya gönderiliyor, yorum bekleniyor...

🤖 FİNAL CEVAP:

İstanbul'da hava çok sıcak ve sıcaklık 800 derece. Bu durumda dışarıda olmak pek sağlıklı olmayabilir, dolayısıyla tura çıkmanızı önermem. Eğer çıkmak isterseniz, kesinlikle hafif, açık renkli ve bol kıyafetler tercih edin. Ayrıca bol su içmeyi unutmayın! Ancak en iyisi evde kalmak ve serinlemek olacaktır.

---

# Gözlemlediklerim?
Verimiz aşırı saçma bir veriydi. Hava sıcaklığı 800 derece ve yerler lav kaplı buna rağmen ajan bize yine bir kıyafet önerisi verdi. Bu hem pozitif hem de negatif bir özellik aslında. Verinin saçma olması fakat yine de mantıklı bir çıktı verip görevini tamamlaması gayet iyi. Öte yandan bu bize ajanımızın gerçeklik algısının olmadığını gösteriyor. Biz ona veri olarak ne verirsek verelim onu mutlak doğru kabul ediyor. 
    
