import os
print("Siber Kalkan Devrede Loglar Taranıyor...")
sabika_kaydi = {}

with open("gercek_sunucu.log", "r", encoding="utf-8") as dosya:
    
    
    satirlar = dosya.readlines()

    
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

        komut = f'netsh advfirewall firewall add rule name="SiberKalkan_Ban_{ip}" dir=in action=block remoteip={ip}'
        os.system(komut)
        print(f"[-KİLİT-] {ip} Windows Güvenlik Duvarında Kkalıcı olarak BANLANDI!\n")

