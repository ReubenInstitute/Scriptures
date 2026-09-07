import json
import pandas as pd
import HebrewNumbers
import Hebrew
from pathlib import Path

ROOT = Path(__file__).parent

MISHNAH_JSON = "json/mishnah.json"
TRACTATES_CSV = "csv/tractates.csv"
ORDERS_CSV = "csv/orders.csv"

class Order:
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
		return f"Order({self.number}: {self.latin_name})"

class Mishnaya:
	def __init__(self, chapter, number):
		self.chapter = chapter
		self.number = number

	@property
	def text(self):
		return self.chapter.data[self.number - 1]

	@property
	def hebrew_number(self):
		return HebrewNumbers.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return HebrewNumbers.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"Mishnaya({self.chapter.tractate.english_name}:{self.chapter.number}:{self.number})"







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
		return [Mishnaya(self, i+1) for i in range(len(self.data)) if self.data[i]]

	@property
	def hebrew_number(self):
		return HebrewNumbers.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return HebrewNumbers.int_to_gematria(self.number, gershayim=True)

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
		return HebrewNumbers.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return HebrewNumbers.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"MishnahTractate({self.english_name})"

class Mishnah:
	def __init__(self):
		with open(MISHNAH_JSON, 'r', encoding='utf-8') as f:
			self.data = json.load(f)
		self._tractate_data = pd.read_csv(TRACTATES_CSV)

		self.orders = []
		data = pd.read_csv(ORDERS_CSV)
		for idx, row in data.iterrows():
			number = idx + 1
			order = Order(self, number, **row.to_dict())
			self.orders.append(order)

	@property
	def tractates(self):
		result = []
		for i, row in self._tractate_data.iterrows():
			if i < len(self.data) and self.data[i]:
				tractate = MishnahTractate(self, i+1, **row.to_dict())
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
