import json
import pandas as pd
import HebrewNumbers
from pathlib import Path

DATA_DIR = Path("/usr/share/scriptures")

ZOHAR_JSON = DATA_DIR / "zohar.json"
CHAPTERS_CSV = DATA_DIR / "csv" / "zohar-chapters.csv"

class Verse:
	def __init__(self, article, number):
		self.article = article
		self.number = number

	@property
	def text(self):
		return self.article.data[self.number - 1]

	@property
	def hebrew_number(self):
		return HebrewNumbers.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return HebrewNumbers.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"Verse({self.article.chapter.number}:{self.article.number}:{self.number})"



class Article:
	def __init__(self, chapter, number):
		self.chapter = chapter
		self.number = number


	@property
	def next(self):
		# First, try to get the next article in the same chapter
		if self.number < len(self.chapter.articles):
			return self.chapter.articles[self.number]  # since articles are 0-indexed

		# Otherwise, find the next chapter that has at least one article
		chapters = self.chapter.zohar.chapters
		current_idx = self.chapter.number - 1  # chapters are 1-indexed
		for idx in range(current_idx + 1, len(chapters)):
			if chapters[idx].articles:
				return chapters[idx].articles[0]  # first article of that chapter
		return None

	@property
	def prev(self):
		# First, try to get the previous article in the same chapter
		if self.number > 1:
			return self.chapter.articles[self.number - 2]  # index = number-2

		# Otherwise, find the previous chapter that has at least one article
		chapters = self.chapter.zohar.chapters
		current_idx = self.chapter.number - 1
		for idx in range(current_idx - 1, -1, -1):
			if chapters[idx].articles:
				return chapters[idx].articles[-1]  # last article of that chapter
		return None

	@property
	def data(self):
		return self.chapter.data[self.number - 1]

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
		return f"Article({self.chapter.number}:{self.number})"

class Chapter:
	def __init__(self, zohar, number, english_title, hebrew_title, group):
		self.zohar = zohar
		self.number = number
		self.english_title = english_title
		self.hebrew_title = hebrew_title
		self.group = group

	@property
	def data(self):
		return self.zohar.data[self.number - 1]

	@property
	def articles(self):
		return [Article(self, i+1) for i in range(len(self.data)) if self.data[i] and any(self.data[i])]

	def __repr__(self):
		return f"Chapter({self.number}: {self.english_title})"

class Zohar:
	def __init__(self):
		with open(ZOHAR_JSON, 'r', encoding='utf-8') as f:
			self.data = json.load(f)
		chapters_df = pd.read_csv(CHAPTERS_CSV)
		self._chapters_metadata = {}
		for idx, row in chapters_df.iterrows():
			self._chapters_metadata[idx] = (row['english_title'], row['hebrew_title'], row['group'])

	@property
	def sections(self):
		return ['בראשית', 'שמות', 'ויקרא', 'במדבר', 'דברים', 'נוספים']


	@property
	def chapters(self):
		result = []
		for i, chapter_data in enumerate(self.data):
			if chapter_data and any(chapter_data):
				english_title, hebrew_title, group = self._chapters_metadata.get(i)#, (f"Chapter {i+1}", "", ""))
				result.append(Chapter(self, i + 1, english_title, hebrew_title, group))
		return result

if __name__ == "__main__":
	zohar = Zohar()
	print(zohar)
	if zohar.chapters:
		chapter = zohar.chapters[0]
		print(chapter)
		if chapter.articles:
			article = chapter.articles[0]
			print(article)
			if article.verses:
				verse = article.verses[0]
				print(verse.text)