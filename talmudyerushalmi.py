import json
import csv
import hebrew

from pathlib import Path
DATA_DIR = Path(__file__).resolve().parent

YERUSHALMI_JSON = DATA_DIR / "json" / "yerushalmi.json"
TRACTATES_CSV = DATA_DIR / "csv" / "tractates.csv"

class TalmudYerushalmiVerse:
	def __init__(self, paragraph, number):
		self.paragraph = paragraph
		self.number = number

	@property
	def text(self):
		return self.paragraph.data[self.number - 1]

	@property
	def hebrew_number(self):
		return hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"TalmudYerushalmiVerse({self.paragraph.chapter.tractate.number}:{self.paragraph.chapter.number}:{self.paragraph.number}:{self.number})"

class TalmudYerushalmiParagraph:
	def __init__(self, chapter, number):
		self.chapter = chapter
		self.number = number

	@property
	def data(self):
		return self.chapter.data[self.number - 1]

	@property
	def verses(self):
		return [TalmudYerushalmiVerse(self, i+1) for i in range(len(self.data)) if self.data[i]]

	@property
	def hebrew_number(self):
		return hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"TalmudYerushalmiParagraph({self.chapter.tractate.number}:{self.chapter.number}:{self.number})"

class TalmudYerushalmiChapter:
	def __init__(self, tractate, number):
		self.tractate = tractate
		self.number = number

	@property
	def data(self):
		return self.tractate.data[self.number - 1]

	@property
	def paragraphs(self):
		return [TalmudYerushalmiParagraph(self, i+1) for i in range(len(self.data)) if self.data[i] and any(self.data[i])]

	@property
	def hebrew_number(self):
		return hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"TalmudYerushalmiChapter({self.tractate.number}:{self.number})"

class TalmudYerushalmiTractate:
	def __init__(self, yerushalmi, number, english_name, hebrew_name, hebrew_fullspell_name):
		self.yerushalmi = yerushalmi
		self.number = number
		self.english_name = english_name
		self.hebrew_name = hebrew_name
		self.hebrew_fullspell_name = hebrew_fullspell_name

	@property
	def data(self):
		return self.yerushalmi.data[self.number - 1]

#	@property
#	def hebrew_bare_name(self):
#		return Hebrew.strip_diacritics(self.hebrew_name)

	@property
	def chapters(self):
		return [TalmudYerushalmiChapter(self, i+1) for i in range(len(self.data)) if self.data[i] and any(self.data[i])]

	@property
	def hebrew_number(self):
		return hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"TalmudYerushalmiTractate({self.english_name})"

class YerushalmiTalmud:
	def __init__(self):
		with open(YERUSHALMI_JSON, 'r', encoding='utf-8') as f:
			self.data = json.load(f)
		self._metadata = {}
		with open(TRACTATES_CSV, newline='', encoding='utf-8') as f:
			for i, row in enumerate(csv.DictReader(f)):
				if row.get('yerushalmi') == '1':
					self._metadata[i] = row

	@property
	def tractates(self):
		result = []
		for i, tractate_data in enumerate(self.data):
			if tractate_data and any(tractate_data) and i in self._metadata:
				row = self._metadata[i]
				result.append(TalmudYerushalmiTractate(self, i+1, row['english_name'], row['hebrew_name'], row['hebrew_fullspell_name']))
		return result

	def __repr__(self):
		return f"YerushalmiTalmud({len(self.tractates)} tractates)"

if __name__ == "__main__":
	yerushalmi = YerushalmiTalmud()
	print(yerushalmi)
	if yerushalmi.tractates:
		tractate = yerushalmi.tractates[0]
		print(tractate)
		if tractate.chapters:
			chapter = tractate.chapters[0]
			print(chapter)
			if chapter.paragraphs:
				paragraph = chapter.paragraphs[0]
				print(paragraph)
				if paragraph.verses:
					verse = paragraph.verses[0]
					print(verse.text)
