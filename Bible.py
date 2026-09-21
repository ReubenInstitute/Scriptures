import csv
import json
import re
from pathlib import Path
import Hebrew
import HebrewNumbers

ROOT = Path(__file__).parent

BIBLE_JSON = ROOT / "json" / "bible.json"
BOOKS_CSV = ROOT / "csv" / "books.csv"

class Verse:
	def __init__(self, chapter, number):
		self.chapter = chapter
		self.number = number
		self._text = None

	@property
	def words(self):
		# a word joined with a maqaf is two spoken words; what sits between two words is the spacer,
		# a space or a maqaf
		separators = ' ' + Hebrew.MAQAF
		return [[(word, Hebrew.MAQAF if Hebrew.MAQAF in spacer else ' ')
				for word, spacer in re.findall('([^%s]+)([%s]*)' % (separators, separators), line)]
			for line in self.lines]

	@property
	def lines(self):
		return [line.strip() for line in self.text.split('\n') if line.strip()]

	@property
	def text(self):
		if self._text is not None:
			return self._text
		return self.orig_text

	@text.setter
	def text(self, value):
		self._text = value

	@property
	def raw_words(self):
		words = Hebrew.raw_text(self.orig_text)
		words = words.split(' ')
		return words

	@property
	def num_words(self):
		return len(self.raw_words)

	@property
	def raw_letters(self):
		return [l for w in self.raw_words for l in w]

	@property
	def num_letters(self):
		return len(self.raw_letters)

	@property
	def orig_text(self):
		return self.chapter.data[self.number - 1]

	@property
	def bare_text(self):
		c = Hebrew.strip_cantillation(self.orig_text)
		c = Hebrew.strip_hebrew_punctuation(c)
		c = Hebrew.strip_diacritics(c)
		c = Hebrew.strip_punctuation(c)
		return c

	@property
	def hebrew_number(self):
		return HebrewNumbers.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return HebrewNumbers.int_to_gematria(self.number, gershayim=True)

	def __repr__(self):
		return f"Verse({self.chapter.book.number}:{self.chapter.number}:{self.number})"




class Chapter:
	def __init__(self, book, number):
		self.book = book
		self.number = number

	@property
	def next(self):
		chapters = self.book.chapters
		if self.number < len(chapters):
			return chapters[self.number]
		return None

	@property
	def prev(self):
		chapters = self.book.chapters
		if self.number > 1:
			return chapters[self.number - 2]
		return None


	@property
	def verses(self):
		return [Verse(self, i + 1) for i in range(len(self.data))]

	@property
	def data(self):
		return self.book.data[self.number - 1]

	@property
	def hebrew_number(self):
		return HebrewNumbers.int_to_gematria(self.number)

	@property
	def hebrew_fancy_number(self):
		return HebrewNumbers.int_to_gematria(self.number, gershayim=True)

	@property
	def num_words(self):
		return sum([v.num_words for v in self.verses])

	@property
	def num_letters(self):
		return sum([v.num_letters for v in self.verses])

	def __repr__(self):
		return f"Chapter({self.book.number}:{self.number})"

class Book:
	def __init__(self, bible, number):
		self.bible = bible
		self.number = number

	@property
	def hebrew_full_name(self):
		return self.metadata['hebrew_name']

	@property
	def hebrew_name(self):
		return Hebrew.strip_diacritics(self.hebrew_full_name)

	@property
	def latin_name(self):
		return self.metadata['latin_name']

	@property
	def english_name(self):
		return self.metadata['english_name']

	@property
	def slug(self):
		return self.metadata['slug']

	@property
	def chapters(self):
		return [Chapter(self, i + 1) for i in range(len(self.data))]

	@property
	def data(self):
		return self.bible.data[self.number - 1]

	@property
	def metadata(self):
		return self.bible.books_metadata[self.number - 1]

	@property
	def color(self):
		colors = [
			(65, 105, 225),
			(34, 139, 34),
			(178, 34, 34),
			(255, 215, 0),
			(75, 0, 130)
		]
		return colors[self.number - 1] if 1 <= self.number <= 5 else (128, 128, 128)

	def __repr__(self):
		return f"Book({self.number})"

	@property
	def is_megillah(self):
		return self.number in [30, 31, 32, 33, 34]


class Bible:
	def __init__(self):
		with open(BIBLE_JSON, 'r', encoding='utf-8') as f:
			self.data = json.load(f)
		with open(BOOKS_CSV, newline='', encoding='utf-8') as f:
			metadata = list(csv.DictReader(f))
		self.books_metadata = []
		for i in range(len(self.data)):
			if i < len(metadata):
				self.books_metadata.append(metadata[i])

	@property
	def slugs(self):
		return {row['slug']: i for i, row in enumerate(self.books_metadata)}

	@property
	def books(self):
		return [Book(self, i + 1) for i in range(len(self.data))]

	def __getitem__(self, slug):
		idx = self.slugs.get(slug)
		if idx is None:
			raise KeyError(f"No book with slug '{slug}'")
		return self.books[idx]

	def verse(self, book, chapter_number, verse_number):
		chapter = book.chapters[chapter_number - 1]
		verse = chapter.verses[verse_number - 1]
		return verse

	def verses(self, book, start_chapter, start_verse, end_chapter, end_verse):
		verses = []
		if start_chapter == end_chapter:
			chapter = book.chapters[start_chapter - 1]
			for verse_number in range(start_verse, end_verse + 1):
				verses.append(chapter.verses[verse_number - 1])
		else:
			start_chapter_obj = book.chapters[start_chapter - 1]
			for verse_number in range(start_verse, len(start_chapter_obj.verses) + 1):
				verses.append(start_chapter_obj.verses[verse_number - 1])
			for chapter_number in range(start_chapter + 1, end_chapter):
				chapter = book.chapters[chapter_number - 1]
				for verse_number in range(1, len(chapter.verses) + 1):
					verses.append(chapter.verses[verse_number - 1])
			end_chapter_obj = book.chapters[end_chapter - 1]
			for verse_number in range(1, end_verse + 1):
				verses.append(end_chapter_obj.verses[verse_number - 1])
		return verses


if __name__ == "__main__":
	bible = Bible()
	print(bible.books[0].chapters[0].verses[0].bare_text)
#	print(bible.books[0].hebrew_name)
