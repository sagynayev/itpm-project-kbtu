from django.test import SimpleTestCase

from pdd.management.commands.sync_adilet import AdiletRulesParser


SAMPLE = """
<h3 id="a">Правила дорожного движения</h3>
<h3 id="b">Глава 13. Проезд перекрестков</h3>
<p id="z100">100. Первый официальный пункт.</p>
<span class="note">Сноска от 03.11.2026.</span>
<p id="z101">1) вложенное условие;</p>
<h3>Основные положения по допуску транспортных средств к эксплуатации</h3>
<p id="z999">Этот текст не относится к ПДД.</p>
"""


class AdiletRulesParserTests(SimpleTestCase):
    def test_extracts_only_pdd_section_and_keeps_parent_point(self):
        parser = AdiletRulesParser()
        parser.feed(SAMPLE)

        self.assertEqual(len(parser.rows), 2)
        self.assertEqual(parser.rows[0]["article_number"], "100")
        self.assertEqual(parser.rows[1]["article_number"], "100")
        self.assertEqual(parser.rows[1]["paragraph"], "z101")
        self.assertEqual(parser.effective_date().isoformat(), "2026-11-03")
