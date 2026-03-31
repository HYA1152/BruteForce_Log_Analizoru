import random

supheli_ipler = ["185.15.54.22","218.10.43.99","194.28.112.11","45.22.19.88","103.44.11.2"]

normal_ipler = [f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}" for _ in range(200)]

print("Siber Saldırı Similasyonu başlatılıyor.  log dosyası oluşturuluyor...")

with open("gercek_sunucu.log", "w", encoding="utf-8") as dosya:
    for i in range(10000):
        if random.random()< 0.15:
            hedef_ip = random.choice(supheli_ipler)
        else:
            hedef_ip = random.choice(normal_ipler)  


        satir = f"[2026-03-31 13:15:{random.randint(10, 59)}] [CRITICAL_WARNING] SSH Brute-Force attempt detected from IP: {hedef_ip}\n"
        dosya.write(satir)
print("Simülasyon tamamlandı. 'gercek_sunucu.log' dosyasına 10.000 adet kayıt başarıyla yazıldı.")      
            
