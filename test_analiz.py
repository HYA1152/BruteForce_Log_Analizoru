"""analiz.py için testler. Çalıştırmak için: python -m unittest -v"""
import random
import unittest

from analiz import satiri_coz, loglari_incele, supheli_ipler
from log_uretici import log_uret, SUPHELI_IPLER, ELE_GECEN_HESAP


def satir(durum, kullanici, ip):
    return f"Mar 31 13:15:42 sunucu sshd[2481]: {durum} password for {kullanici} from {ip} port 52344 ssh2"


class SatirCozmeTest(unittest.TestCase):
    def test_basarisiz_satir(self):
        self.assertEqual(satiri_coz(satir("Failed", "root", "185.15.54.22")),
                         ("Failed", "root", "185.15.54.22"))

    def test_invalid_user_satiri(self):
        s = "Mar 31 13:15:42 sunucu sshd[1]: Failed password for invalid user oracle from 45.22.19.88 port 1 ssh2"
        self.assertEqual(satiri_coz(s), ("Failed", "oracle", "45.22.19.88"))

    def test_ilgisiz_ve_bos_satir(self):
        self.assertIsNone(satiri_coz("Mar 31 13:15:42 sunucu CRON[99]: session opened"))
        self.assertIsNone(satiri_coz(""))

    def test_gecersiz_ip_yok_sayilir(self):
        # Log dosyasına sızdırılmış komut içeren sahte bir IP işlenmemeli
        self.assertIsNone(satiri_coz(satir("Failed", "root", "1.2.3.4;shutdown")))
        self.assertIsNone(satiri_coz(satir("Failed", "root", "999.1.1.1")))

    def test_ipv6(self):
        self.assertEqual(satiri_coz(satir("Failed", "root", "2001:db8::1"))[2], "2001:db8::1")


class TespitTest(unittest.TestCase):
    def test_ara_sira_sifre_yanlis_yazan_kullanici_supheli_degil(self):
        # 10 kez yanlış ama her seferinde ardından doğru giriş: brute-force değil
        satirlar = []
        for _ in range(10):
            satirlar += [satir("Failed", "yigit", "10.0.0.5"), satir("Accepted", "yigit", "10.0.0.5")]
        kayit = loglari_incele(satirlar, esik=5)
        self.assertEqual(kayit["10.0.0.5"]["toplam"], 10)
        self.assertEqual(supheli_ipler(kayit, 5), [])

    def test_art_arda_deneme_supheli(self):
        satirlar = [satir("Failed", "root", "185.15.54.22")] * 6
        kayit = loglari_incele(satirlar, esik=5)
        self.assertEqual([ip for ip, _ in supheli_ipler(kayit, 5)], ["185.15.54.22"])

    def test_esigin_altinda_kalan_supheli_degil(self):
        satirlar = [satir("Failed", "root", "185.15.54.22")] * 4
        self.assertEqual(supheli_ipler(loglari_incele(satirlar, 5), 5), [])

    def test_denemeler_sonrasi_basarili_giris_kritik(self):
        satirlar = [satir("Failed", "admin", "45.22.19.88")] * 8 + [satir("Accepted", "test", "45.22.19.88")]
        kayit = loglari_incele(satirlar, esik=5)
        self.assertEqual(kayit["45.22.19.88"]["ele_gecen"], "test")

    def test_uretilen_logda_sadece_saldirganlar_yakalanir(self):
        random.seed(7)
        kayit = loglari_incele(log_uret(5000), esik=5)
        bulunan = {ip for ip, _ in supheli_ipler(kayit, 5)}
        self.assertEqual(bulunan, set(SUPHELI_IPLER))
        self.assertEqual(kayit[ELE_GECEN_HESAP[1]]["ele_gecen"], ELE_GECEN_HESAP[0])


if __name__ == "__main__":
    unittest.main()
