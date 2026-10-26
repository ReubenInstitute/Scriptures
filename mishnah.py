import json
import csv
import Hebrew
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

MISHNAH_JSON = DATA_DIR / "json" / "mishnah.json"
TRACTATES_CSV = DATA_DIR / "csv" / "tractates.csv"
ORDERS_CSV = DATA_DIR / "csv" / "orders.csv"

class MishnahOrder:
	def __init__(self, mishnah, number, **metadata):
		self.mishnah = mishnah
		self.number = number
		self.latin_name = ""
		self.hebrew_name = ""
		self.hebrew_fullspell_name = ""
		for key in metadata:
			if hasattr(self, key):
				setattr(self, key, metadata[key])

	@property
	def tractates(self):
		return [tractate for tractate in self.mishnah.tractates if tractate.order == self]

	def __repr__(self):
		return f"MishnahOrder({self.number}: {self.latin_name})"

class MishnahMishnaya:
	def __init__(self, chapter, number):
		self.chapter = chapter
		self.number = number

	@property
	def text(self):
		return self.chapter.data[self.number - 1]

	@property
	def hebrew_number(self):
		return Hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return Hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"MishnahMishnaya({self.chapter.tractate.english_name}:{self.chapter.number}:{self.number})"







class MishnahChapter:
	def __init__(self, tractate, number):
		self.tractate = tractate
		self.number = number


	@property
	def next(self):
		if self.number < len(self.tractate.chapters):
			return self.tractate.chapters[self.number]  # 0‑based index = number
		return None

	@property
	def prev(self):
		if self.number > 1:
			return self.tractate.chapters[self.number - 2]
		return None



	@property
	def data(self):
		return self.tractate.data[self.number - 1]

	@property
	def mishnayot(self):
		return [MishnahMishnaya(self, i+1) for i in range(len(self.data)) if self.data[i]]

	@property
	def hebrew_number(self):
		return Hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return Hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"MishnahChapter({self.tractate.english_name}:{self.number})"





class MishnahTractate:
	def __init__(self, mishnah, number, **metadata):
		self.mishnah = mishnah
		self.number = number
		self.english_name = ""
		self.hebrew_name = ""
		self.hebrew_fullspell_name = ""
		self.order_number = None
		for key in metadata:
			setattr(self, key, metadata[key])
		print (self.path)
		self.order = self.mishnah.orders[self.order_number - 1]

	@property
	def data(self):
		return self.mishnah.data[self.number - 1]

	@property
	def chapters(self):
		return [MishnahChapter(self, i+1) for i in range(len(self.data)) if self.data[i]]

	@property
	def hebrew_number(self):
		return Hebrew.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return Hebrew.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"MishnahTractate({self.english_name})"

class Mishnah:
	def __init__(self):
		with open(MISHNAH_JSON, 'r', encoding='utf-8') as f:
			self.data = json.load(f)
		with open(TRACTATES_CSV, newline='', encoding='utf-8') as f:
			self._tractate_data = list(csv.DictReader(f))

		self.orders = []
		with open(ORDERS_CSV, newline='', encoding='utf-8') as f:
			data = list(csv.DictReader(f))
		for idx, row in enumerate(data):
			number = idx + 1
			order = MishnahOrder(self, number, **row)
			self.orders.append(order)

	@property
	def tractates(self):
		result = []
		for i, row in enumerate(self._tractate_data):
			if i < len(self.data) and self.data[i]:
				metadata = dict(row)
				metadata['order_number'] = int(metadata['order_number'])
				tractate = MishnahTractate(self, i+1, **metadata)
				result.append(tractate)
		return result

	def __repr__(self):
		return f"Mishnah({len(self.tractates)} tractates)"

if __name__ == "__main__":
	mishnah = Mishnah()
	order = mishnah.orders[0]
	tractate = order.tractates[0]
	print(tractate)
	chapter = tractate.chapters[0]
	print(chapter)
	mishnaya = chapter.mishnayot[0]
	print(mishnaya.text)
