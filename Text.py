from pathlib import Path

ROOT = Path(__file__).parent

class Word:
	def __init__(self, text, verse=None, spacer=' '):
		self.verse = verse
		self.spacer = spacer
		self.full_text = text
		self.text = self.full_text.replace('^', '\u05BD').replace('$', '').replace('ˇ', '').replace('**', '')

	def __repr__(self):
		return f"Word('{self.text}')"


class TextStore:
	_instance = None

	@classmethod
	def get_instance(cls):
		if cls._instance is None:
			cls._instance = TextStore()
		return cls._instance

	def __init__(self):
		self.base = ROOT / "text"
		self._cache = {}
		self.scan()

	def scan(self):
		self._cache.clear()
		if not self.base.exists():
			return
		for f in self.base.glob("**/*.md"):
			path = str(f.relative_to(self.base))
			try:
				content = f.read_text(encoding="utf-8")
				self._cache[path] = content
			except Exception:
				continue

	def get(self, path):
		return self._cache.get(path)

	def reload(self, path):
		f = self.base / path
		if f.exists():
			self._cache[path] = f.read_text(encoding="utf-8")
		elif path in self._cache:
			del self._cache[path]

	def set(self, path, content):
		f = self.base / path
		f.parent.mkdir(parents=True, exist_ok=True)
		f.write_text(content, encoding="utf-8")
		self._cache[path] = content

	def has(self, path):
		return path in self._cache

	def delete(self, path):
		if path in self._cache:
			del self._cache[path]
		f = self.base / path
		if f.exists():
			f.unlink()

class Text:
	def __init__(self, path):
		self.path = path
		self.store = TextStore.get_instance()

	@property
	def markdown(self):
		return self.store.get(self.path) or ""
	
	@markdown.setter
	def markdown(self, content):
		self.store.set(self.path, content)
	
	@markdown.deleter  
	def markdown(self):
		self.store.delete(self.path)

	def read(self):
		content = self.markdown
		if not content:
			return []
		return self.parse(content)

	def write(self, structure):
		content = self.serialize(structure)
		self.markdown = content

	def parse(self, content):
		return [[[[1], [content]]]]

	def serialize(self, structure):
		if structure and structure[0] and structure[0][0]:
			return '\n'.join(structure[0][0][1])
		return ""

	def exists(self):
		return self.store.has(self.path)

class PoemText(Text):
	def __init__(self, path):
		super().__init__(path)

	def parse(self, content):
		result = []
		verse_number = 1
		paragraphs = content.split('\n\n\n')
		for paragraph_content in paragraphs:
			verses = []
			verse_blocks = paragraph_content.split('\n\n')
			for verse_block in verse_blocks:
				lines = []
				for line in verse_block.split('\n'):
					if line.endswith('  '):
						line = line[:-2]
					lines.append(line)
				if any(line.strip() for line in lines):
					verses.append([[verse_number], lines])
					verse_number += 1
			if verses:
				result.append(verses)
		return result

	def serialize(self, structure):
		paragraph_texts = []
		for paragraph in structure:
			verse_texts = []
			for verse in paragraph:
				lines = verse[1]
				marked = [line + '  ' if i < len(lines) - 1 else line
						  for i, line in enumerate(lines)]
				verse_texts.append('\n'.join(marked))
			paragraph_texts.append('\n\n'.join(verse_texts))
		return '\n\n\n'.join(paragraph_texts)

class NarrationText(Text):
	def __init__(self, path):
		super().__init__(path)
		#print (path)

	def parse(self, content):
		result = []
		paragraphs = content.split('\n\n')
		for paragraph_text in paragraphs:
			paragraph = []
			lines = paragraph_text.split('\n')
			current_verse = None
			for line in lines:
				if line.endswith('  '):
					line = line[:-2]
				parts = line.split(' ', 1)
				if len(parts) == 2 and '.' in parts[0]:
					nums = parts[0].split('.')
					if len(nums) == 2 and nums[0].isdigit() and nums[1].isdigit():
						if current_verse:
							paragraph.append(current_verse)
						chapter = int(nums[0])
						verse_number = int(nums[1])
						current_verse = [[chapter, verse_number], [parts[1]]]
						continue
				if current_verse:
					current_verse[1].append(line)
			if current_verse:
				paragraph.append(current_verse)
			if paragraph:
				result.append(paragraph)
		return result

	def serialize(self, structure):
		lines = []
		for paragraph in structure:
			for verse in paragraph:
				lines.append(f"{verse[0][0]}.{verse[0][1]} {verse[1][0]}")
				for line in verse[1][1:]:
					lines.append(line)
			lines.append('')
		if lines and lines[-1] == '':
			lines.pop()
		return '\n'.join(lines)
