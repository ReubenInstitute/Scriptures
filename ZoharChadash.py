import json
import pandas as pd
import HebrewNumbers
from pathlib import Path

ROOT = Path(__file__).parent

ZOHAR_CHADASH_JSON = "json/zohar-chadash.json"
CHAPTERS_CSV = "csv/zohar-chadash-chapters.csv"

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
	def __init__(self, zohar_chadash, number, **kwargs):
		self.PAGESIZE = 40
		self.zohar_chadash = zohar_chadash
		self.number = number
		for key, value in kwargs.items():
			setattr(self, key, value)

	@property
	def next(self):
		chapters = self.zohar_chadash.chapters
		if self.number < len(chapters):
			return chapters[self.number]  # 0‑based index = number
		return None

	@property
	def prev(self):
		chapters = self.zohar_chadash.chapters
		if self.number > 1:
			return chapters[self.number - 2]
		return None

#class Chapter:
#	def __init__(self, zohar_chadash, number, english_title, hebrew_title):
#		self.zohar_chadash = zohar_chadash
#		self.number = number
#		self.english_title = english_title
#		self.hebrew_title = hebrew_title

	@property
	def data(self):
		return self.zohar_chadash.data[self.number - 1]

	@property
	def verses(self):
		return [Verse(self, i+1) for i in range(len(self.data)) if self.data[i]]

	def __repr__(self):
		return f"Chapter({self.number}: {self.english_title})"





	@property
	def pages(self):
		if len(self.verses) <= self.PAGESIZE - 1:
			numpages = 1
		else:
			remaining = len(self.verses) - (self.PAGESIZE - 1)
			numpages = 1 + (remaining + self.PAGESIZE)
		if numpages == 1:
			return [self.verses]
		else:
			out = [self.verses[:self.PAGESIZE - 1]]
			for page in range(1, numpages):
				start = (page - 1) * self.PAGESIZE
				end = start + self.PAGESIZE
				if end > len(self.verses):
					end = len(self.verses)
				out.append([self.verses[start:end]])
			print (len(out))
			return out


class ZoharChadash:
	def __init__(self):
		with open(ZOHAR_CHADASH_JSON, 'r', encoding='utf-8') as f:
			self.data = json.load(f)
		#chapters_df = pd.read_csv(CHAPTERS_CSV)
		#self._chapter_titles = {}
		#for idx, row in chapters_df.iterrows():
		#	self._chapter_titles[idx] = (row['english_title'], row['hebrew_title'])
		data = pd.read_csv(CHAPTERS_CSV)
		self._metadata = []
		for idx, row in data.iterrows():
			self._metadata.append(row.to_dict())

	@property
	def sections(self):
		return ['בראשית', 'שמות', 'ויקרא', 'במדבר', 'דברים', 'נוספים']

	@property
	def chapters(self):
		result = []
		for i, data in enumerate(self.data):
			#if chapter_data and any(chapter_data):
				# get the metadata for this chapter (if exists)
			metadata = self._metadata[i]# if i < len(self._metadata) else {}
				# pass the metadata as keyword arguments
			result.append(Chapter(self, i + 1, **metadata))
		return result

	@property
	def xchapters(self):
		result = []
		for i, chapter_data in enumerate(self.data):
			if chapter_data and any(chapter_data):
				english_title, hebrew_title = self._chapter_titles.get(i, (f"Chapter {i+1}", ""))
				result.append(Chapter(self, i+1, english_title, hebrew_title))
		return result

	def __repr__(self):
		return f"ZoharChadash({len(self.data)} chapters)"

if __name__ == "__main__":
	zohar_chadash = ZoharChadash()
	print(zohar_chadash)
	if zohar_chadash.chapters:
		chapter = zohar_chadash.chapters[0]
		print(chapter)
		if chapter.verses:
			verse = chapter.verses[0]
			print(verse.text)
