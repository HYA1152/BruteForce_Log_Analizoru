print("Siber Kalkan Devrede Loglar Taranıyor...")
sabika_kaydi = {}
# 'sunucu.log' dosyasını okumak için açıyoruz ('r' harfi read yani oku demek)
with open("sunucu.log", "r") as dosya:
    
    # Dosyanın içindeki tüm satırları okuyup 'satirlar' diye bir torbaya atıyoruz
    satirlar = dosya.readlines()

    # Torbadaki her bir satırı tek tek çıkarıp ekrana basıyoruz
    for satir in satirlar:
       kelimeler = satir.split()
       ip_adresi = kelimeler[-1]
       
       if ip_adresi in sabika_kaydi:
           sabika_kaydi[ip_adresi] = sabika_kaydi[ip_adresi] + 1

       else:
           sabika_kaydi[ip_adresi] = 1
print("Sabıka kayıtları:", sabika_kaydi)   

print("\n--- KIRMIZI BÜLTEN RAPORU ---")

for ip, sayi in sabika_kaydi.items():

    if sayi > 2:
        print("TEHLİKE! Bu IP acilen yasaklanmalı:", ip, "-> Tam", sayi, "kere saldırdı!" ) 

