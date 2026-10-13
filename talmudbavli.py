import json
import csv
import hebrew
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

BAVLI_JSON = DATA_DIR / "json" / "bavli.json"
TRACTATES_CSV = DATA_DIR / "csv" / "tractates.csv"

class TalmudBavliVerse:
	def __init__(self, page, number):
		self.page = page
		self.number = number

	@property
	def text(self):
		return self.page.data[self.number - 1]

	@property
	def hebrew_number(self):
		return hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"TalmudBavliVerse({self.page.tractate.number}:{self.page.number}:{self.number})"

class TalmudBavliPage:
	def __init__(self, tractate, number):
		self.tractate = tractate
		self.number = number

	@property
	def data(self):
		return self.tractate.data[self.number - 1]

	@property
	def verses(self):
		return [TalmudBavliVerse(self, i+1) for i in range(len(self.data)) if self.data[i]]

	@property
	def hebrew_number(self):
		return hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"TalmudBavliPage({self.tractate.number}:{self.number})"

class TalmudBavliTractate:
	def __init__(self, talmud, number, english_name, hebrew_name, hebrew_fullspell_name):
		self.talmud = talmud
		self.number = number
		self.english_name = english_name
		self.hebrew_name = hebrew_name
		self.hebrew_fullspell_name = hebrew_fullspell_name

#	@property
#	def hebrew_bare_name(self):
#		return Hebrew.strip_diacritics(self.hebrew_name)

	@property
	def data(self):
		return self.talmud.data[self.number - 1]

	@property
	def pages(self):
		return [TalmudBavliPage(self, i+1) for i in range(len(self.data)) if self.data[i] and any(self.data[i])]

	@property
	def hebrew_number(self):
		return hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"TalmudBavliTractate({self.english_name})"

class TalmudBavli:
	def __init__(self):
		with open(BAVLI_JSON, 'r', encoding='utf-8') as f:
			self.data = json.load(f)
		self._metadata = {}
		with open(TRACTATES_CSV, newline='', encoding='utf-8') as f:
			for i, row in enumerate(csv.DictReader(f)):
				self._metadata[i] = row

	@property
	def tractates(self):
		result = []
		for i, tractate_data in enumerate(self.data):
			row = self._metadata[i]
			if tractate_data and any(tractate_data) and i in self._metadata and row.get('bavli') == '1':
				result.append(TalmudBavliTractate(self, i+1, row['english_name'], row['hebrew_name'], row['hebrew_fullspell_name']))
		return result

	def __repr__(self):
		return f"TalmudBavli({len(self.tractates)} tractates)"

if __name__ == "__main__":
	bavli = TalmudBavli()
	print(bavli)
	if bavli.tractates:
		tractate = bavli.tractates[0]
		print(tractate)
		if tractate.pages:
			page = tractate.pages[0]
			print(page)
			if page.verses:
				verse = page.verses[0]
				print(verse.text)
