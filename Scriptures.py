from Bible import Bible
from Mishnah import Mishnah
from TalmudBavli import TalmudBavli
from TalmudYerushalmi import YerushalmiTalmud
from Zohar import Zohar
from ZoharChadash import ZoharChadash
from ZoharTikkunim import ZoharTikkunim

class TalmudContainer:
	pass

class ZoharContainer:
	pass

class Scriptures:
	def __init__(self):
		self.bible = Bible()
		self.mishnah = Mishnah()
		self.talmud = TalmudContainer()
		self.talmud.bavli = TalmudBavli()
		self.talmud.yerushalmi = YerushalmiTalmud()
		self.zohar = ZoharContainer()
		self.zohar.main = Zohar()
		self.zohar.chadash = ZoharChadash()
		self.zohar.tikkunim = ZoharTikkunim()
