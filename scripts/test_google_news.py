"""Testes locais do adaptador Google Notícias, sem chamadas à Internet."""
import datetime as dt
import email.utils
import unittest
from scripts.collect import google_news_ojogo


class GoogleNewsTests(unittest.TestCase):
    source = {"id": "ojogo", "website": "https://www.ojogo.pt/", "name": "O JOGO"}

    def xml(self, publisher="O Jogo"):
        now = email.utils.format_datetime(dt.datetime.now(dt.timezone.utc))
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0"><channel><title>Google Notícias</title><item>
        <title>Notícia de futebol - {publisher}</title>
        <link>https://news.google.com/rss/articles/CBM123</link>
        <pubDate>{now}</pubDate><source url="https://www.ojogo.pt">{publisher}</source>
        </item></channel></rss>"""

    def test_google_timestamp_not_original(self):
        entries = google_news_ojogo(self.source, self.xml())
        self.assertEqual(len(entries), 1)
        item = entries[0]
        self.assertIsNone(item["publishedAt"])
        self.assertEqual(item["datePrecision"], "google")
        self.assertTrue(item["googlePublishedAt"])
        self.assertEqual(item["via"], "Google Notícias")
        self.assertEqual(item["title"], "Notícia de futebol")
        self.assertTrue(item["url"].startswith("https://news.google.com/"))

    def test_other_publication_rejected(self):
        wrong_xml = self.xml("Outro Jornal").replace(
            'source url="https://www.ojogo.pt"',
            'source url="https://outrojornal.pt"'
        )
        with self.assertRaises(ValueError):
            google_news_ojogo(self.source, wrong_xml)


if __name__ == "__main__":
    unittest.main()
