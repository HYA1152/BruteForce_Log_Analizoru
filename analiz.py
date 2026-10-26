"""SSH loglarında brute-force (kaba kuvvet) şifre denemelerini tespit eder.

Mantık: Normal bir kullanıcı şifresini arada bir yanlış yazar ama hemen ardından
doğru girer. Saldırgan ise ARD ARDA onlarca yanlış şifre dener. Bu yüzden her IP için
"art arda başarısız deneme" serisini takip ediyoruz; seri eşiği aşarsa IP şüphelidir.

Bu betik hiçbir IP'yi kendisi engellemez: şüpheli IP'leri bir dosyaya yazar,
kararı ve engellemeyi sistem yöneticisi kontrol ederek yapar.

Kullanım:
    python analiz.py                               # sunucu.log, eşik 5
    python analiz.py baska.log --esik 10
"""
import argparse
import ipaddress
import re
import sys

# Örnek satır:
# Mar 31 13:15:42 sunucu sshd[2481]: Failed password for invalid user admin from 185.15.54.22 port 52344 ssh2
SSH_KALIBI = re.compile(
    r"(?P<durum>Failed|Accepted) password for (?:invalid user )?(?P<kullanici>\S+) "
    r"from (?P<ip>\S+)"
)


def satiri_coz(satir):
    """Bir log satırından (durum, kullanıcı, ip) çıkarır. Uymayan satırda None döner."""
    eslesme = SSH_KALIBI.search(satir)
    if not eslesme:
        return None

    ip = eslesme.group("ip")
    try:
        # Geçerli bir IP değilse (ör. "1.2.3.4;del") satırı yok say
        ipaddress.ip_address(ip)
    except ValueError:
        return None

    return eslesme.group("durum"), eslesme.group("kullanici"), ip


def loglari_incele(satirlar, esik):
    """Log satırlarını tek tek okuyup her IP için istatistik çıkarır.

    Dönen sözlükte her IP için:
        toplam  -> toplam başarısız deneme
        en_uzun -> en uzun art arda başarısız deneme serisi
        denenen -> denenen kullanıcı adları
        ele_gecen -> eşiği aşan bir seriden SONRA başarılı giriş yapılan hesap (varsa)
    """
    sabika_kaydi = {}
    seri = {}   # ip -> şu anki art arda başarısız deneme sayısı

    for satir in satirlar:
        sonuc = satiri_coz(satir)
        if sonuc is None:
            continue
        durum, kullanici, ip = sonuc

        kayit = sabika_kaydi.setdefault(ip, {"toplam": 0, "en_uzun": 0, "denenen": set(), "ele_gecen": None})

        if durum == "Failed":
            kayit["toplam"] += 1
            kayit["denenen"].add(kullanici)
            seri[ip] = seri.get(ip, 0) + 1
            kayit["en_uzun"] = max(kayit["en_uzun"], seri[ip])
        else:  # Accepted
            if seri.get(ip, 0) >= esik:
                kayit["ele_gecen"] = kullanici
            seri[ip] = 0

    return sabika_kaydi


def supheli_ipler(sabika_kaydi, esik):
    """En uzun serisi eşiği aşan IP'leri, en çok deneme yapandan başlayarak sıralar."""
    supheliler = [(ip, k) for ip, k in sabika_kaydi.items() if k["en_uzun"] >= esik]
    return sorted(supheliler, key=lambda x: x[1]["toplam"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="SSH loglarında brute-force tespiti.")
    parser.add_argument("dosya", nargs="?", default="sunucu.log", help="İncelenecek log dosyası (varsayılan: sunucu.log)")
    parser.add_argument("--esik", type=int, default=5, help="Şüpheli sayılmak için art arda en az kaç başarısız deneme (varsayılan: 5)")
    parser.add_argument("--rapor", default="engellenecek_ipler.txt", help="Şüpheli IP'lerin yazılacağı dosya")
    args = parser.parse_args()

    print("Siber Kalkan devrede, loglar taranıyor...")
    try:
        with open(args.dosya, "r", encoding="utf-8", errors="replace") as dosya:
            sabika_kaydi = loglari_incele(dosya, args.esik)
    except FileNotFoundError:
        print(f"HATA: '{args.dosya}' bulunamadı. Önce 'python log_uretici.py' ile örnek log üretebilirsin.")
        sys.exit(1)

    toplam = sum(k["toplam"] for k in sabika_kaydi.values())
    print(f"Toplam {toplam} başarısız giriş denemesi, {len(sabika_kaydi)} farklı IP incelendi.")

    supheliler = supheli_ipler(sabika_kaydi, args.esik)

    print(f"\n--- KIRMIZI BÜLTEN RAPORU (eşik: art arda {args.esik} başarısız deneme) ---")
    if not supheliler:
        print("Eşiği aşan IP yok.")
    for ip, k in supheliler:
        denenen = ", ".join(sorted(k["denenen"])[:5])
        print(f"TEHLİKE! {ip:<16} -> {k['toplam']} başarısız deneme, en uzun seri {k['en_uzun']} "
              f"(denenen: {denenen})")
        if k["ele_gecen"]:
            print(f"   !!! KRİTİK: Bu IP denemelerden sonra '{k['ele_gecen']}' hesabıyla GİRİŞ YAPTI. "
                  f"Hesap ele geçirilmiş olabilir!")

    with open(args.rapor, "w", encoding="utf-8") as rapor:
        for ip, _ in supheliler:
            rapor.write(f"{ip}\n")
    print(f"\n{len(supheliler)} şüpheli IP '{args.rapor}' dosyasına yazıldı.")
    print("Not: Engelleme otomatik yapılmaz. Listeyi kontrol edip güvenlik duvarına elle ekleyin.")


if __name__ == "__main__":
    main()
