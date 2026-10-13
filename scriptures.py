from .bible import Bible
from .mishnah import Mishnah
from .talmudbavli import TalmudBavli
from .talmudyerushalmi import YerushalmiTalmud
from .zohar import Zohar
from .zoharchadash import ZoharChadash
from .zohartikkunim import ZoharTikkunim

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
