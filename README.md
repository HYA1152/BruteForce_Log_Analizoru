# SSH Brute-Force Log Analizörü

SSH sunucu loglarında kaba kuvvet (brute-force) şifre denemelerini tespit eden küçük bir Python aracı. Log dosyasını satır satır okuyup her IP adresi için başarısız giriş denemelerini sayar ve şüpheli IP'leri raporlar.

Proje iki betikten oluşur:

| Dosya | Görevi |
| --- | --- |
| `log_uretici.py` | Gerçek bir `/var/log/auth.log` dosyasına benzeyen **simüle** bir log üretir: 5 saldırgan IP'nin şifre denemeleri, normal kullanıcıların girişleri ve bir hesabın ele geçirildiği senaryo |
| `analiz.py` | Log dosyasını inceler, şüpheli IP'leri ekrana ve `engellenecek_ipler.txt` dosyasına yazar |

## Nasıl karar veriyor?

Normal bir kullanıcı şifresini arada bir yanlış yazar ama hemen ardından doğru girer. Saldırgan ise **art arda** onlarca yanlış şifre dener. Bu yüzden araç her IP için art arda başarısız deneme serisini takip eder. Seri eşiği (varsayılan 5) geçerse IP şüpheli sayılır.

Ayrıca bir IP uzun bir deneme serisinin ardından **başarılı giriş** yaptıysa bunu ayrıca `KRİTİK` olarak işaretler, çünkü bu durumda hesap ele geçirilmiş olabilir.

## Kullanım

Python 3.8+ yeterli, ek paket gerekmez.

```bash
python log_uretici.py              # sunucu.log dosyasına 2000 satırlık örnek log yazar
python analiz.py                   # sunucu.log dosyasını inceler
python analiz.py baska.log --esik 10
```

Örnek çıktı:

```
--- KIRMIZI BÜLTEN RAPORU (eşik: art arda 5 başarısız deneme) ---
TEHLİKE! 45.22.19.88      -> 267 başarısız deneme, en uzun seri 212 (denenen: admin, guest, oracle, postgres, root)
   !!! KRİTİK: Bu IP denemelerden sonra 'test' hesabıyla GİRİŞ YAPTI. Hesap ele geçirilmiş olabilir!
TEHLİKE! 194.28.112.11    -> 250 başarısız deneme, en uzun seri 250 (denenen: admin, guest, oracle, postgres, root)
...
5 şüpheli IP 'engellenecek_ipler.txt' dosyasına yazıldı.
```

## Güvenlik notları

- Araç **hiçbir IP'yi kendisi engellemez**. İlk sürümde şüpheli IP'ler `netsh` komutuyla otomatik olarak güvenlik duvarına ekleniyordu. Bu iki sebeple kaldırıldı:
  1. Log içindeki IP alanı doğrudan komuta ekleniyordu. Log dosyasına özel hazırlanmış bir satır sokulursa **komut enjeksiyonu** yapılabilirdi.
  2. Eşik hatası yüzünden normal kullanıcılar da engelleniyordu.
- Logdaki her IP `ipaddress` modülüyle doğrulanır, geçersiz değerler yok sayılır.
- Engelleme kararı, `engellenecek_ipler.txt` listesi kontrol edildikten sonra elle verilmelidir.

## Testler

```bash
python -m unittest -v
```

## Sonraki adımlar

- Zaman penceresine göre tespit (ör. 1 dakikada 10'dan fazla deneme)
- Gerçek `auth.log` dosyasıyla deneme
- Sonuçları CSV/JSON olarak dışa aktarma
