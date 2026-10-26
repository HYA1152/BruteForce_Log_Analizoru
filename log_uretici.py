"""SSH brute-force saldırısı içeren örnek (simüle) bir sunucu logu üretir.

Gerçek bir Linux sunucusundaki /var/log/auth.log satırlarına benzer satırlar yazar:
    Mar 31 13:15:42 sunucu sshd[2481]: Failed password for root from 185.15.54.22 port 52344 ssh2
    Mar 31 13:15:47 sunucu sshd[2490]: Accepted password for yigit from 10.0.0.5 port 50122 ssh2

Kullanım:
    python log_uretici.py                      # sunucu.log dosyasına 2000 satır yazar
    python log_uretici.py --satir 10000 --cikti test.log --tohum 42
"""
import argparse
import random
from datetime import datetime, timedelta

# Saldırgan IP'ler: çok sayıda başarısız deneme yaparlar
SUPHELI_IPLER = ["185.15.54.22", "218.10.43.99", "194.28.112.11", "45.22.19.88", "103.44.11.2"]

# Saldırganların denediği yaygın kullanıcı adları
DENENEN_KULLANICILAR = ["root", "admin", "test", "oracle", "ubuntu", "postgres", "user", "guest"]

# Gerçek kullanıcılar ve kendi IP'leri (arada bir şifreyi yanlış yazabilirler)
NORMAL_KULLANICILAR = {
    "yigit": "10.0.0.5",
    "ayse": "10.0.0.12",
    "mehmet": "192.168.1.20",
    "deploy": "192.168.1.35",
}


# Senaryo: saldırganlardan biri sonunda zayıf şifreli "test" hesabına giriyor
ELE_GECEN_HESAP = ("test", "45.22.19.88")


def satir_yaz(zaman, durum, kullanici, ip):
    pid = random.randint(1000, 9999)
    port = random.randint(40000, 65000)
    return (f"{zaman.strftime('%b %d %H:%M:%S')} sunucu sshd[{pid}]: "
            f"{durum} password for {kullanici} from {ip} port {port} ssh2\n")


def log_uret(satir_sayisi, saldiri_orani=0.6):
    """Satırları zaman sırasına göre üretip liste olarak döndürür."""
    satirlar = []
    zaman = datetime(2026, 3, 31, 13, 0, 0)

    ele_gecirme_ani = int(satir_sayisi * 0.8)

    for i in range(satir_sayisi):
        zaman += timedelta(seconds=random.randint(1, 4))

        if i == ele_gecirme_ani:
            kullanici, ip = ELE_GECEN_HESAP
            satirlar.append(satir_yaz(zaman, "Accepted", kullanici, ip))
        elif random.random() < saldiri_orani:
            # Brute-force: saldırgan sürekli yanlış şifre dener
            ip = random.choice(SUPHELI_IPLER)
            kullanici = random.choice(DENENEN_KULLANICILAR)
            satirlar.append(satir_yaz(zaman, "Failed", kullanici, ip))
        else:
            # Normal kullanıcı: çoğunlukla başarılı giriş, nadiren yanlış şifre
            kullanici, ip = random.choice(list(NORMAL_KULLANICILAR.items()))
            durum = "Failed" if random.random() < 0.05 else "Accepted"
            satirlar.append(satir_yaz(zaman, durum, kullanici, ip))

    return satirlar


def main():
    parser = argparse.ArgumentParser(description="Simüle SSH brute-force logu üretir.")
    parser.add_argument("--satir", type=int, default=2000, help="Üretilecek satır sayısı (varsayılan: 2000)")
    parser.add_argument("--cikti", default="sunucu.log", help="Yazılacak dosya (varsayılan: sunucu.log)")
    parser.add_argument("--tohum", type=int, default=None, help="Aynı logu tekrar üretmek için rastgelelik tohumu")
    args = parser.parse_args()

    if args.tohum is not None:
        random.seed(args.tohum)

    print("Siber saldırı simülasyonu başlatılıyor, log dosyası oluşturuluyor...")
    satirlar = log_uret(args.satir)
    with open(args.cikti, "w", encoding="utf-8") as dosya:
        dosya.writelines(satirlar)
    print(f"Simülasyon tamamlandı. '{args.cikti}' dosyasına {len(satirlar)} satır yazıldı.")


if __name__ == "__main__":
    main()
