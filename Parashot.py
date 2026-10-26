from .Text import NarrationText, Word
import csv
from pathlib import Path
import colorsys
import Hebrew

ROOT = Path(__file__).parent

PARASHOT_CSV = ROOT / "csv" / "parashot.csv"
EPISODES_CSV = ROOT / "csv" / "episodes.csv"
MD_PATH = ROOT / "parashot.md"

def read_csv_rows(path):
	with open(path, newline='', encoding='utf-8') as f:
		return list(csv.DictReader(f))

class ParashahParagraph:
	def __init__(self, episode, number):
		self.episode = episode
		self.number = number
		self.verses = []

	@property
	def layout(self):
		return self.episode.layout[self.number - 1]


	def slides(self):
		slides = []
		current = []
		for verse in self.verses:
			# If the verse text starts with '$', close current slide and start new
			if verse.text.startswith('$'):
				if current:
					slides.append(current)
				current = []
				# Remove the '$' from the verse's text for the slide
				verse.text = verse.text[1:]  # strip the leading marker
			current.append(verse)
		if current:
			slides.append(current)
		return slides

	def __repr__(self):
		return f"ParashahParagraph({self.episode.parashah.number}.{self.episode.number}.{self.number}, {len(self.verses)} verses)"

class ParashahEpisode():
	def __init__(self, parashah, number, start_verse, end_verse, metadata=None):
		self.parashah = parashah
		self.number = number
		self.start_verse = start_verse
		self.end_verse = end_verse
		self.english_title = metadata.get('english_title', '') if metadata else ''
		self.hebrew_title = metadata.get('hebrew_title', '') if metadata else ''
		self.paragraphs = []
		#self.overlay = EpisodeOverlay(self)
		self.load()

	def load(self):
		start_chapter, start_verse = map(int, self.start_verse.split('.'))
		end_chapter, end_verse = map(int, self.end_verse.split('.'))
		self.verses = self.parashah.parashot.bible.verses(
			self.parashah.book,#.number,
			start_chapter, start_verse,
			end_chapter, end_verse
		)
		#print(self.paragraphs)
		self.paragraphs = []


	@property
	def color(self):
		parashah_color = self.parashah.color
		total_episodes = len(self.parashah.episodes)
		episode_index = self.parashah.episodes.index(self)
		r, g, b = parashah_color
		hue_shift = (episode_index / total_episodes) * 30 - 15
		h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
		h = (h + hue_shift/360) % 1.0
		r, g, b = colorsys.hls_to_rgb(h, l, s)
		return (int(r*255), int(g*255), int(b*255))

	@property
	def hebrew_number(self):
		return Hebrew.Number(self.number).text

	@property
	def hebrew_fancy_number(self):
		return Hebrew.Number(self.number).fancy_text


	@property
	def layout(self):
		original = []
		for paragraph in self.paragraphs:
			lines = []
			for verse in paragraph.verses:
				for line_words in verse.words:
					line = [Word(word, verse, spacer) for word, spacer in line_words]
					lines.append(line)
			original.append(lines)
		layout = []
		for paragraph in original:
			new_paragraph = []
			if not paragraph:
				continue
			current_merged_line = paragraph[0]
			for i in range(1, len(paragraph)):
				line = paragraph[i]
				prev_line_words = paragraph[i-1]
				if line[0].verse.number == prev_line_words[0].verse.number:
					new_paragraph.append(current_merged_line)
					current_merged_line = line
				else:
					current_merged_line.extend(line)
			if current_merged_line:
				new_paragraph.append(current_merged_line)
			layout.append(new_paragraph)
		return layout


	@property
	def vlayout(self):
		"""Vertical layout: split paragraphs at verses starting with '$' and build lines."""
		layout = []
		for paragraph in self.paragraphs:
			# Split paragraph.verses into groups where a verse starts with '$'
			groups = []
			current = []
			for verse in paragraph.verses:
				if verse.text.startswith('$'):
					if current:
						groups.append(current)
					current = []
				current.append(verse)
			if current:
				groups.append(current)
	
			# For each group, build lines and merge lines from the same verse
			for verses in groups:
				lines = []
				for verse in verses:
					for line_words in verse.words:
						line = [Word(word, verse, spacer) for word, spacer in line_words]
						lines.append(line)
				# Merge consecutive lines that belong to the same verse
				merged = []
				if not lines:
					continue
				current_line = lines[0]
				for i in range(1, len(lines)):
					next_line = lines[i]
					if next_line[0].verse.number == current_line[0].verse.number:
						merged.append(current_line)
						current_line = next_line
					else:
						current_line.extend(next_line)
				merged.append(current_line)
				layout.append(merged)
		return layout


	def __repr__(self):
		return f"ParashahEpisode({self.parashah.number}.{self.number}, {self.start_verse}-{self.end_verse})"

























class Parashah(NarrationText):
	def __init__(self, parashot, metadata):
		self.parashot = parashot
		self.metadata = metadata
		self.number = int(metadata['number'])
		self.english_name = metadata['english_name']
		self.hebrew_full_name = metadata['hebrew_name']
		self.hebrew_name = Hebrew.strip_diacritics(self.hebrew_full_name)
		self.book = parashot.bible.books[int(metadata['book']) - 1]
		NarrationText.__init__(self, f"parashot/{self.number:02d}.md")
		self.english_title = ""
		self.english_description = ""
		self.hebrew_title = ""
		self.hebrew_description = ""
		self.episodes = []
		self.load()


	@property
	def color(self):
		book_color = self.book.color
		parashot_in_book = [p for p in self.parashot._items if p.book.number == self.book.number]
		total_parashot_in_book = len(parashot_in_book)
		parashah_index = [p.number for p in parashot_in_book].index(self.number)
		progress = parashah_index / (total_parashot_in_book - 1) if total_parashot_in_book > 1 else 0.5
		r, g, b = book_color
		lightness = 0.4 + (0.4 * progress)
		h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
		l = max(0, min(1, l * lightness))
		r, g, b = colorsys.hls_to_rgb(h, l, s)
		return (int(r*255), int(g*255), int(b*255))

	def pdf(self):
		ParashahBookletPDF(self).generate()

	def load(self):
		episodes = read_csv_rows(EPISODES_CSV)
		parashah_episodes = [row for row in episodes if int(row['parashah']) == self.number]
		if len(parashah_episodes) > 0:
			self.episodes = []
			for row in parashah_episodes:
				start_verse = f"{int(row['start_chapter'])}.{int(row['start_verse'])}"
				end_verse = f"{int(row['end_chapter'])}.{int(row['end_verse'])}"
				episode = ParashahEpisode(self, int(row['number']), start_verse, end_verse, row)
				self.episodes.append(episode)
		else:
			default_metadata = {'english_title': self.english_name, 'hebrew_title': self.hebrew_name}
			self.episodes = [ParashahEpisode(self, 1, self.metadata['start_verse'], self.metadata['end_verse'], default_metadata)]

		content = self.read()
		if content:
			verse_index = 0
			episode_index = 0
			for paragraph_data in content:
				while (episode_index < len(self.episodes) and
						verse_index >= len(self.episodes[episode_index].verses)):
					episode_index += 1
					verse_index = 0
				if episode_index >= len(self.episodes):
					break
				episode = self.episodes[episode_index]
				paragraph = ParashahParagraph(episode, len(episode.paragraphs) + 1)
				paragraph_appended = False

				for verse_entry in paragraph_data:
					# a markdown paragraph can span an episode boundary: once the
					# current episode's verses are exhausted, close it off and
					# continue the same markdown paragraph as a new one on the
					# next episode.
					while (episode_index < len(self.episodes) and
							verse_index >= len(self.episodes[episode_index].verses)):
						if paragraph.verses and not paragraph_appended:
							episode.paragraphs.append(paragraph)
							paragraph_appended = True
						episode_index += 1
						verse_index = 0
						if episode_index >= len(self.episodes):
							break
						episode = self.episodes[episode_index]
						paragraph = ParashahParagraph(episode, len(episode.paragraphs) + 1)
						paragraph_appended = False
					if episode_index >= len(self.episodes):
						break

					lines = verse_entry[1]
					episode.verses[verse_index].text = '\n'.join(lines)
					paragraph.verses.append(episode.verses[verse_index])
					verse_index += 1

				if paragraph.verses and not paragraph_appended:
					episode.paragraphs.append(paragraph)
				if episode_index >= len(self.episodes):
					break
		else:
			#print ("NO")
			#print (content)
			#exit()
			for episode in self.episodes:
				paragraph = ParashahParagraph(episode, 1)
				paragraph.verses = episode.verses
				episode.paragraphs = [paragraph]

	@property
	def markdown(self):
		return super().markdown

	@markdown.setter
	def markdown(self, content):
		super(Parashah, self.__class__).markdown.fset(self, content)

	@markdown.deleter
	def markdown(self):
		super(Parashah, self.__class__).markdown.fdel(self)

	@property
	def verses(self):
		verses = []
		for episode in self.episodes:
			for paragraph in episode.paragraphs:
				verses.extend(paragraph.verses)
		return verses

	def __getitem__(self, index):
		return self.episodes[index]

	def __len__(self):
		return len(self.episodes)

	def __repr__(self):
		return f"Parashah({self.number}: {self.english_name})"


#	@property
#	def layout(self):
#		#return [line for episode in self.episodes for line in episode.layout]
#		return [layout for episode in self.episodes for layout in episode.layout]

	@property
	def paragraphs(self):
		return [paragraph for episode in self.episodes for paragraph in episode.paragraphs]

#	@property
#	def slug(self):
#		return self.english_name.lower()



class Parashot:
	def __init__(self, bible):
		self.bible = bible
		self._items = []
		self.load()

	def load(self):
		print ("HERE")
		print (PARASHOT_CSV)
		#PARASHOT_CSV = "db/parashot.csv"
		parashot_rows = read_csv_rows(PARASHOT_CSV)
		self._items = []
		for row in parashot_rows:
			start_verse = f"{int(row['start_chapter'])}.{int(row['start_verse'])}"
			end_verse = f"{int(row['end_chapter'])}.{int(row['end_verse'])}"
			metadata = {
				'number': row['number'],
				'english_name': row['english_name'],
				'hebrew_name': row['hebrew_name'],
				'book': row['book'],
				'start_verse': start_verse,
				'end_verse': end_verse
			}
			parashah = Parashah(self, metadata)
			self._items.append(parashah)

		print ("HERE2")
		md_path = MD_PATH
		content = md_path.read_text(encoding='utf-8')
		paragraphs = content.strip().split('\n\n')
		i = 0
		while i < len(paragraphs):
			english = paragraphs[i]
			hebrew = paragraphs[i + 1]
			en_title, en_desc = english.split('•', 1)
			he_title, he_desc = hebrew.split('•', 1)
			parashah_index = i // 2
			self._items[parashah_index].english_title = en_title.strip()
			self._items[parashah_index].english_description = en_desc.strip()
			self._items[parashah_index].hebrew_title = he_title.strip()
			self._items[parashah_index].hebrew_description = he_desc.strip()
			i += 2

	def __getitem__(self, key):
		if isinstance(key, str):
			return next(p for p in self._items if p.english_name.lower() == key.lower())
		return self._items[key]