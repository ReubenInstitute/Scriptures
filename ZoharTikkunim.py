import json
import HebrewNumbers
from pathlib import Path

DATA_DIR = Path("/usr/share/scriptures")

ZOHAR_TIKKUNIM_JSON = DATA_DIR / "zohar-tikkunim.json"

class Verse:
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
		return f"Verse({self.chapter.number}:{self.number})"

class Chapter:
	def __init__(self, zohar_tikkunim, number):
		self.zohar_tikkunim = zohar_tikkunim
		self.number = number

	@property
	def data(self):
		return self.zohar_tikkunim.data[self.number - 1]

	@property
	def verses(self):
		return [Verse(self, i+1) for i in range(len(self.data)) if self.data[i]]

	@property
	def hebrew_number(self):
		return HebrewNumbers.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return HebrewNumbers.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"Chapter({self.number})"

class ZoharTikkunim:
	def __init__(self):
		with open(ZOHAR_TIKKUNIM_JSON, 'r', encoding='utf-8') as f:
			self.data = json.load(f)

	@property
	def chapters(self):
		return [Chapter(self, i+1) for i, chapter_data in enumerate(self.data)
				if chapter_data and any(chapter_data)]

	def __repr__(self):
		return f"ZoharTikkunim({len(self.data)} chapters)"

if __name__ == "__main__":
	zt = ZoharTikkunim()
	print(zt)
	if zt.chapters:
		chapter = zt.chapters[0]
		print(chapter)
		if chapter.verses:
			verse = chapter.verses[0]
			print(verse.text)
