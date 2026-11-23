"""Testes para a janela de cinco dias do Radar, sem rede."""
import datetime as dt
import unittest
from scripts.collect import recent_article

UTC=dt.timezone.utc

class RetentionTests(unittest.TestCase):
    now=dt.datetime(2026,11,23,12,0,tzinfo=UTC)

    def test_original_datetime_last_120_hours(self):
        self.assertTrue(recent_article({'publishedAt':'2026-11-18T12:00:00Z'},self.now))
        self.assertFalse(recent_article({'publishedAt':'2026-11-18T11:59:59Z'},self.now))
        self.assertFalse(recent_article({'publishedAt':'2026-11-17T15:00:00Z'},self.now))

    def test_google_uses_google_date_not_detection(self):
        item={'via':'Google Notícias','googlePublishedAt':'2026-11-17T14:00:00Z',
              'firstSeenAt':'2026-11-23T11:00:00Z'}
        self.assertFalse(recent_article(item,self.now))
        item['googlePublishedAt']='2026-11-23T09:00:00Z'
        self.assertTrue(recent_article(item,self.now))

    def test_day_only_five_calendar_days(self):
        item={'datePrecision':'day','localDate':'2026-11-19','firstSeenAt':'2026-11-23T08:00:00Z'}
        self.assertTrue(recent_article(item,self.now))
        item['localDate']='2026-11-18'
        self.assertFalse(recent_article(item,self.now))
        item['localDate']='2026-11-24'
        self.assertFalse(recent_article(item,self.now))

    def test_no_publication_date_uses_first_seen(self):
        self.assertTrue(recent_article({'firstSeenAt':'2026-11-22T20:00:00Z'},self.now))
        self.assertFalse(recent_article({'firstSeenAt':'2026-11-17T20:00:00Z'},self.now))

    def test_invalid_and_future(self):
        self.assertFalse(recent_article({},self.now))
        self.assertFalse(recent_article({'publishedAt':'not a date'},self.now))
        self.assertFalse(recent_article({'publishedAt':'2026-11-24T12:00:00Z'},self.now))

if __name__=='__main__':
    unittest.main()
