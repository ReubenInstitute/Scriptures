from .Text import PoemText, Word
import Hebrew
from pathlib import Path
import re
import colorsys

ROOT = Path(__file__).parent

MD_PATH = ROOT / "psalms.md"

class PsalmParagraph:
	def __init__(self, psalm, number):
		self.psalm = psalm
		self.number = number
		self.verses = []

	def __repr__(self):
		return f"PsalmParagraph({self.psalm.number}.{self.number}, {len(self.verses)} verses)"

	@property
	def layout(self):
		return self.psalm.layout[self.number - 1]




	@property
	def slides(self):
		slides = []
		current = []
		for verse in self.verses:
			current.append(verse)
			if verse.text.endswith('$'):
				slides.append(current)
				current = []
		if current:
			slides.append(current)
		return slides



class Psalm(PoemText):
	def __init__(self, psalms, number):
		self.psalms = psalms
		self.number = number
		self.english_title = ""
		self.english_description = ""
		self.hebrew_title = ""
		self.hebrew_description = ""
		self.paragraphs = []
		PoemText.__init__(self, f"psalms/{self.number:03d}.md")
		self.load()

	@property
	def hebrew_number(self):
		return Hebrew.Number(self.number).text

	@property
	def hebrew_fancy_number(self):
		return Hebrew.Number(self.number).fancy_text


	@property
	def previous(self):
		if self.number > 1:
			return self.psalms[self.number - 2]
		return None

	@property
	def next(self):
		if self.number < len(self.psalms):
			return self.psalms[self.number]
		return None


	@property
	def volume(self):
		if self.number <= 41:
			return 1
		elif self.number <= 72:
			return 2
		elif self.number <= 89:
			return 3
		elif self.number <= 106:
			return 4
		else:
			return 5


	@property
	def color(self):
		books = [
			(1,   41, (65, 105, 225)),
			(42,  72, (34, 139, 34)),
			(73,  89, (178, 34, 34)),
			(90, 106, (255, 215, 0)),
			(107, 150, (75, 0, 130))
		]
		for start, end, base_rgb in books:
			if start <= self.number <= end:
				position = (self.number - start) / (end - start)
				lightness_factor = 0.4 + 0.4 * position
				r, g, b = base_rgb
				h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
				l = max(0.0, min(1.0, l * lightness_factor))
				r, g, b = colorsys.hls_to_rgb(h, l, s)
				return (int(r * 255), int(g * 255), int(b * 255))
		return (128, 128, 128)

	def load(self):
		#print(self.psalms.bible.books)
		#exit()
		self.store.reload(self.path)
		book = self.psalms.bible.books[26]
		chapter = book.chapters[self.number - 1]
		verses = chapter.verses
		content = self.read()
		if content:
			verse_index = 0
			self.paragraphs = []
			for i, paragraph_data in enumerate(content):
				paragraph = PsalmParagraph(self, i + 1)
				for verse_data in paragraph_data:
					verse_text = '\n'.join(verse_data[1])
					if verse_index < len(verses):
						verses[verse_index].text = verse_text
						paragraph.verses.append(verses[verse_index])
						verse_index += 1
				if paragraph.verses:
					self.paragraphs.append(paragraph)

	@property
	def layout(self):
		paragraphs = []
		for paragraph in self.paragraphs:
			verses = []
			for verse in paragraph.verses:
				verse_lines = []
				for line_words in verse.words:
					line = [Word(word, verse, spacer) for word, spacer in line_words]
					verse_lines.append(line)
				verses.append(verse_lines)
			paragraphs.append(verses)
		return paragraphs

	@property
	def verses(self):
		all_verses = []
		for paragraph in self.paragraphs:
			all_verses.extend(paragraph.verses)
		return all_verses

	def __repr__(self):
		return f"Psalm({self.number})"
		##, {len(self.paragraphs)} paragraphs, {len(self.verses)} verses)"



class Psalms:
	def __getitem__(self, index):
		return self._items[index]

	def __repr__(self):
		return "Psalms"


	def __iter__(self):
		return iter(self._items)

	def __len__(self):
		return len(self._items)




	def __init__(self, bible):
		self.bible = bible
		self._items = [Psalm(self, i) for i in range(1, 151)]

		md_path = MD_PATH
		content = md_path.read_text(encoding='utf-8')
		parts = content.split('---\n', 1)
		main_content = parts[0]
		paragraphs = main_content.strip().split('\n\n')
		i = 0
		while i < len(paragraphs):
			english = paragraphs[i]
			matches = re.findall(r'\d+', english)
			if matches:
				psalm_num = int(matches[0])
				if '•' in english:
					en_title, en_desc = english.split('•', 1)
					en_title = en_title.strip()
					en_desc = en_desc.strip()
				if i + 1 < len(paragraphs):
					hebrew = paragraphs[i + 1]
					if '•' in hebrew:
						he_title, he_desc = hebrew.split('•', 1)
						he_title = he_title.strip()
						he_desc = he_desc.strip()
						psalm = self._items[psalm_num - 1]
						psalm.english_title = en_title
						psalm.english_description = en_desc
						psalm.hebrew_title = he_title
						psalm.hebrew_description = he_desc
			i += 1