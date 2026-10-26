#!/usr/bin/env python3
import json
import csv
from pathlib import Path
import requests
from urllib.parse import quote
import time
import re
import html
import unicodedata
import argparse
import shutil
import sys

ROOT = Path(__file__).resolve().parent
DOWNLOAD_FOLDER = ROOT / "download"
JSON_FOLDER = ROOT / "json"
CSV_FOLDER = ROOT / "csv"


def read_csv_rows(path):
	with open(path, newline='', encoding='utf-8') as f:
		return list(csv.DictReader(f))


class Source:
	URL_FUCKUPS = {
		"https://www.sefaria.org.il/download/version/Mishnah%20Avot%20-%20he%20-%20Mishnah,%20ed.%20Romm,%20Vilna%201913.json":
			"https://www.sefaria.org.il/download/version/Pirkei%20Avot%20-%20he%20-%20Mishnah,%20ed.%20Romm,%20Vilna%201913.json",
		"https://www.sefaria.org.il/download/version/Mishnah%20Tohorot%20-%20he%20-%20Mishnah,%20ed.%20Romm,%20Vilna%201913.json":
			"https://www.sefaria.org.il/download/version/Mishnah%20Tahorot%20-%20he%20-%20Mishnah,%20ed.%20Romm,%20Vilna%201913.json",
		"https://www.sefaria.org.il/download/version/Mishnah%20Taanit%20-%20he%20-%20Mishnah,%20ed.%20Romm,%20Vilna%201913.json":
			"https://www.sefaria.org.il/download/version/Mishnah%20Ta'anit%20-%20he%20-%20Mishnah,%20ed.%20Romm,%20Vilna%201913.json",
		"https://www.sefaria.org.il/download/version/Zohar.json":
			"https://www.sefaria.org.il/download/version/Zohar%20-%20he%20-%20Vocalized%20Zohar,%20Israel%202013.json",
		"https://www.sefaria.org.il/download/version/Zohar%20Chadash.json":
			"https://www.sefaria.org.il/download/version/Zohar%20Chadash%20-%20he%20-%20Zohar%20Chadash.json",
		"https://www.sefaria.org.il/download/version/Tikkunei%20Zohar.json":
			"https://www.sefaria.org.il/download/version/Tikkunei%20Zohar%20-%20he%20-%20Tikkunei%20Zohar%20-%20Vocalized.json"
	}

	@classmethod
	def download(cls):
		DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
		print("📁 Checking for missing source files...")
		books_df = read_csv_rows(CSV_FOLDER / "books.csv")
		tractates_df = read_csv_rows(CSV_FOLDER / "tractates.csv")
		missing_files = []
		bible_template = "https://www.sefaria.org.il/download/version/{NAME}%20-%20he%20-%20Miqra%20according%20to%20the%20Masorah.json"
		for row in books_df:
			default_url = bible_template.format(NAME=quote(row['latin_name']))
			final_url = cls.URL_FUCKUPS.get(default_url, default_url)
			filename = f"bible_{row['latin_name'].lower().replace(' ', '_')}.json"
			cache_file = DOWNLOAD_FOLDER / filename
			if not cache_file.exists():
				missing_files.append((row['latin_name'], final_url, filename))

		mishnah_template = "https://www.sefaria.org.il/download/version/Mishnah%20{NAME}%20-%20he%20-%20Mishnah,%20ed.%20Romm,%20Vilna%201913.json"
		for row in tractates_df:
			default_url = mishnah_template.format(NAME=quote(row['english_name']))
			final_url = cls.URL_FUCKUPS.get(default_url, default_url)
			filename = f"mishnah_{row['english_name'].lower().replace(' ', '_')}.json"
			cache_file = DOWNLOAD_FOLDER / filename
			if not cache_file.exists():
				missing_files.append((f"Mishnah {row['english_name']}", final_url, filename))

		bavli_template = "https://www.sefaria.org.il/download/version/{NAME}%20-%20he%20-%20William%20Davidson%20Edition%20-%20Vocalized%20Aramaic.json"
		bavli_df = [row for row in tractates_df if row.get('bavli') == '1']
		for row in bavli_df:
			default_url = bavli_template.format(NAME=quote(row['english_name']))
			final_url = cls.URL_FUCKUPS.get(default_url, default_url)
			filename = f"bavli_{row['english_name'].lower().replace(' ', '_')}.json"
			cache_file = DOWNLOAD_FOLDER / filename
			if not cache_file.exists():
				missing_files.append((f"Bavli {row['english_name']}", final_url, filename))

		yerushalmi_template = "https://www.sefaria.org.il/download/version/Jerusalem%20Talmud%20{NAME}%20-%20he%20-%20Venice%20Edition.json"
		yerushalmi_df = [row for row in tractates_df if row.get('yerushalmi') == '1']
		for row in yerushalmi_df:
			default_url = yerushalmi_template.format(NAME=quote(row['english_name']))
			final_url = cls.URL_FUCKUPS.get(default_url, default_url)
			filename = f"yerushalmi_{row['english_name'].lower().replace(' ', '_')}.json"
			cache_file = DOWNLOAD_FOLDER / filename
			if not cache_file.exists():
				missing_files.append((f"Yerushalmi {row['english_name']}", final_url, filename))

		zohar_configs = [
			('Zohar', cls.URL_FUCKUPS['https://www.sefaria.org.il/download/version/Zohar.json'], 'zohar_zohar.json'),
			('Zohar Chadash', cls.URL_FUCKUPS['https://www.sefaria.org.il/download/version/Zohar%20Chadash.json'], 'zohar_zohar_chadash.json'),
			('Tikkunei Zohar', cls.URL_FUCKUPS['https://www.sefaria.org.il/download/version/Tikkunei%20Zohar.json'], 'zohar_tikkunei_zohar.json')
		]
		for name, url, filename in zohar_configs:
			cache_file = DOWNLOAD_FOLDER / filename
			if not cache_file.exists():
				missing_files.append((name, url, filename))

		if missing_files:
			print(f"⚠️  Downloading {len(missing_files)} missing files...")
			for i, (name, url, filename) in enumerate(missing_files):
				try:
					response = requests.get(url, timeout=30)
					if response.status_code == 200:
						with open(DOWNLOAD_FOLDER / filename, 'w', encoding='utf-8') as f:
							json.dump(response.json(), f, ensure_ascii=False, indent=2)
						print(f"✅ [{i+1}/{len(missing_files)}] Downloaded: {name}")
					else:
						print(f"❌ Failed to download {name}: HTTP {response.status_code}")
				except Exception as e:
					print(f"❌ Error downloading {name}: {e}")
				time.sleep(0.5)
		else:
			print("✅ All source files are present in cache!")
		return len(missing_files)

	@classmethod
	def build(cls):
		cls.download()
		JSON_FOLDER.mkdir(parents=True, exist_ok=True)
		print("\n" + "=" * 40)
		print("🔄 CONVERTING ALL TEXTS")
		print("=" * 40)
		cls.build_bible()
		cls.build_mishnah()
		cls.build_bavli()
		cls.build_yerushalmi()
		cls.build_zohar()
		cls.build_zohar_chadash()
		cls.build_tikkunei_zohar()
		cls.verify()
		print("\n" + "=" * 60)
		print("🎉 BUILD COMPLETE!")
		print("=" * 60)

	@classmethod
	def build_bible(cls):
		print("📖 Converting Bible...")
		books_df = read_csv_rows(CSV_FOLDER / "books.csv")
		bible_data = []
		for row in books_df:
			filename = DOWNLOAD_FOLDER / f"bible_{row['latin_name'].lower().replace(' ', '_')}.json"
			if filename.exists():
				with open(filename, 'r', encoding='utf-8') as f:
					book_json = json.load(f)
				book_text = book_json.get('text', [])
				cleaned_book = []
				for chapter in book_text:
					cleaned_chapter = []
					for verse in chapter:
						cleaned_verse = cls.clean_bible_text(verse)
						cleaned_chapter.append(cleaned_verse)
					cleaned_book.append(cleaned_chapter)
				bible_data.append(cleaned_book)
			else:
				bible_data.append([])
				print(f"⚠️  Missing Bible book: {row['latin_name']}")
		with open(JSON_FOLDER / 'bible.json', 'w', encoding='utf-8') as f:
			json.dump(bible_data, f, ensure_ascii=False, indent=2)
		print(f"✅ Bible: {len(bible_data)} books (cleaned)")
		return bible_data

	@classmethod
	def build_mishnah(cls):
		print("📖 Converting Mishnah...")
		tractates_df = read_csv_rows(CSV_FOLDER / "tractates.csv")
		mishnah_data = []
		for row in tractates_df:
			filename = DOWNLOAD_FOLDER / f"mishnah_{row['english_name'].lower().replace(' ', '_')}.json"
			if filename.exists():
				with open(filename, 'r', encoding='utf-8') as f:
					tractate_json = json.load(f)
				tractate_text = tractate_json.get('text', [])
				mishnah_data.append(tractate_text)
			else:
				mishnah_data.append([])
		with open(JSON_FOLDER / 'mishnah.json', 'w', encoding='utf-8') as f:
			json.dump(mishnah_data, f, ensure_ascii=False, indent=2)
		print(f"✅ Mishnah: {len(mishnah_data)} tractates")
		return mishnah_data

	@classmethod
	def build_bavli(cls):
		print("📖 Converting Talmud Bavli (page-based)...")
		tractates_df = read_csv_rows(CSV_FOLDER / "tractates.csv")
		bavli_data = []
		for row in tractates_df:
			if row.get('bavli') == '1':
				filename = DOWNLOAD_FOLDER / f"bavli_{row['english_name'].lower().replace(' ', '_')}.json"
				if filename.exists():
					with open(filename, 'r', encoding='utf-8') as f:
						tractate_json = json.load(f)
					text_data = tractate_json.get('text', [])
					cleaned_text = [page for page in text_data if page and isinstance(page, list)]
					bavli_data.append(cleaned_text)
				else:
					bavli_data.append([])
			else:
				bavli_data.append([])
		bavli_data = cls.fix_bavli(bavli_data)
		for tractate in bavli_data:
			for page in tractate:
				for i, verse_text in enumerate(page):
					page[i] = cls.clean_bavli_text(verse_text)
		with open(JSON_FOLDER / 'bavli.json', 'w', encoding='utf-8') as f:
			json.dump(bavli_data, f, ensure_ascii=False, indent=2)
		bavli_count = sum(1 for tractate in bavli_data if tractate)
		total_pages = sum(len(tractate) for tractate in bavli_data)
		print(f"✅ Talmud Bavli: {bavli_count} tractates, {total_pages} total pages")
		return bavli_data

	@classmethod
	def build_yerushalmi(cls):
		print("📖 Converting Talmud Yerushalmi (chapter-based)...")
		tractates_df = read_csv_rows(CSV_FOLDER / "tractates.csv")
		yerushalmi_data = []
		for row in tractates_df:
			if row.get('yerushalmi') == '1':
				filename = DOWNLOAD_FOLDER / f"yerushalmi_{row['english_name'].lower().replace(' ', '_')}.json"
				if filename.exists():
					with open(filename, 'r', encoding='utf-8') as f:
						tractate_json = json.load(f)
					text_data = tractate_json.get('text', [])
					cleaned_text = []
					for chapter in text_data:
						if chapter and isinstance(chapter, list):
							cleaned_halakhot = [halakha for halakha in chapter if halakha]
							if cleaned_halakhot:
								cleaned_text.append(cleaned_halakhot)
					yerushalmi_data.append(cleaned_text)
				else:
					yerushalmi_data.append([])
			else:
				yerushalmi_data.append([])
		with open(JSON_FOLDER / 'yerushalmi.json', 'w', encoding='utf-8') as f:
			json.dump(yerushalmi_data, f, ensure_ascii=False, indent=2)
		yerushalmi_count = sum(1 for tractate in yerushalmi_data if tractate)
		total_chapters = sum(len(tractate) for tractate in yerushalmi_data)
		print(f"✅ Talmud Yerushalmi: {yerushalmi_count} tractates, {total_chapters} total chapters")
		return yerushalmi_data


	@classmethod
	def build_zohar(cls):
		print("🔮 Converting Zohar...")
		zohar_file = DOWNLOAD_FOLDER / "zohar_zohar.json"
		if zohar_file.exists():
			with open(zohar_file, 'r', encoding='utf-8') as f:
				zohar_data = json.load(f)
			zohar_text = zohar_data.get('text', {})
			zohar_converted = []
			for section_name, episodes in zohar_text.items():
				if section_name == 'Addenda' and isinstance(episodes, dict):
					# Addenda should be treated as ONE section with multiple episodes
					episode_list = []
					for key, verses in episodes.items():
						if isinstance(verses, list):
							episode_list.append(verses)
						else:
							episode_list.append([verses])
					zohar_converted.append(episode_list)  # ← ONE section for ALL Addenda
				elif isinstance(episodes, list):
					zohar_converted.append(episodes)
			with open(JSON_FOLDER / 'zohar.json', 'w', encoding='utf-8') as f:
				json.dump(zohar_converted, f, ensure_ascii=False, indent=2)
		else:
			zohar_converted = []
			print("⚠️  Missing Zohar source file")
		print(f"✅ Zohar: {len(zohar_converted)} sections")
		return zohar_converted

	@classmethod
	def build_zohar_chadash(cls):
		print("🔮 Converting Zohar Chadash...")
		zohar_chadash_file = DOWNLOAD_FOLDER / "zohar_zohar_chadash.json"
		if zohar_chadash_file.exists():
			with open(zohar_chadash_file, 'r', encoding='utf-8') as f:
				zohar_chadash_data = json.load(f)
			zohar_chadash_text = zohar_chadash_data.get('text', {})
			zohar_chadash_converted = []
			for section_name, verses in zohar_chadash_text.items():
				if isinstance(verses, list):
					zohar_chadash_converted.append(verses)
				else:
					zohar_chadash_converted.append([verses])
			with open(JSON_FOLDER / 'zohar-chadash.json', 'w', encoding='utf-8') as f:
				json.dump(zohar_chadash_converted, f, ensure_ascii=False, indent=2)
		else:
			zohar_chadash_converted = []
			print("⚠️  Missing Zohar Chadash source file")
		print(f"✅ Zohar Chadash: {len(zohar_chadash_converted)} sections")
		return zohar_chadash_converted

	@classmethod
	def build_tikkunei_zohar(cls):
		print("🔮 Converting Tikkunei Zohar...")
		tikkunei_file = DOWNLOAD_FOLDER / "zohar_tikkunei_zohar.json"
		if tikkunei_file.exists():
			with open(tikkunei_file, 'r', encoding='utf-8') as f:
				tikkunei_data = json.load(f)
			tikkunei_text = tikkunei_data.get('text', [])
			tikkunei_converted = [chapter for chapter in tikkunei_text if chapter]
			with open(JSON_FOLDER / 'zohar-tikkunim.json', 'w', encoding='utf-8') as f:
				json.dump(tikkunei_converted, f, ensure_ascii=False, indent=2)
		else:
			tikkunei_converted = []
			print("⚠️  Missing Tikkunei Zohar source file")
		print(f"✅ Tikkunei Zohar: {len(tikkunei_converted)} chapters")
		return tikkunei_converted

	@classmethod
	def verify(cls):
		print("\n🔍 Verifying conversions...")
		books_df = read_csv_rows(CSV_FOLDER / "books.csv")
		with open(JSON_FOLDER / 'bible.json', 'r', encoding='utf-8') as f:
			bible_data = json.load(f)
		assert len(bible_data) == len(books_df), f"Bible book count mismatch: {len(bible_data)} vs {len(books_df)}"
		print("✅ Bible books verified")
		tractates_df = read_csv_rows(CSV_FOLDER / "tractates.csv")
		with open(JSON_FOLDER / 'mishnah.json', 'r', encoding='utf-8') as f:
			mishnah_data = json.load(f)
		assert len(mishnah_data) == len(tractates_df), f"Mishnah tractate count mismatch"
		print("✅ Mishnah tractates verified")
		zohar_chapters_df = read_csv_rows(CSV_FOLDER / "zohar-chapters.csv")
		with open(JSON_FOLDER / 'zohar.json', 'r', encoding='utf-8') as f:
			zohar_data = json.load(f)
		assert len(zohar_data) == len(zohar_chapters_df), f"Zohar section count mismatch"
		print("✅ Zohar sections verified")
		zohar_chadash_chapters_df = read_csv_rows(CSV_FOLDER / "zohar-chadash-chapters.csv")
		with open(JSON_FOLDER / 'zohar-chadash.json', 'r', encoding='utf-8') as f:
			zohar_chadash_data = json.load(f)
		assert len(zohar_chadash_data) == len(zohar_chadash_chapters_df), f"Zohar Chadash section count mismatch"
		print("✅ Zohar Chadash sections verified")
		print("🎉 All conversions verified successfully!")

	@staticmethod
	def clean_bible_text(text):
		if not text or not isinstance(text, str):
			return text
		footnote_pattern = r'<sup class="footnote-marker">\*</sup><i class="footnote">\([^)]*\)</i>'
		text = re.sub(footnote_pattern, '', text)
		text = re.sub(r'<sup>(?!\*</sup>)[^<]*</sup>', '', text)

		def extract_content(match):
			span_content = match.group(1)
			qere_match = re.search(r'\[([^\]]*)\]', span_content)
			if qere_match:
				return qere_match.group(1)
			ktiv_match = re.search(r'\(([^)]*)\)', span_content)
			if ktiv_match:
				return ktiv_match.group(1)
			return span_content

		text = re.sub(r'<span class="mam-kq[^"]*">(.*?)</span>', extract_content, text)
		text = text.replace('{פ}', '').replace('{ס}', '')
		text = re.sub(r'<[^>]+>', '', text)
		text = re.sub(r'[\[\]()]', '', text)
		text = html.unescape(text)
		text = re.sub(r'\s+', ' ', text).strip()
		return text

	@staticmethod
	def fix_bavli(data):
		data[42][54][9] = data[42][54][9].replace(')', '', 1)
		data[42][184][11] = data[42][184][11].replace('[', '', 1)
		return data

	@staticmethod
	def clean_bavli_text(text):
		if not text or not isinstance(text, str): 
			return text
		text = text.replace('`', '')
		text = text.replace('–', '-').replace('—', '-')
		text = text.replace('׳', "'")
		text = text.replace('״', '"')
		text = text.replace('...', '…')
		text = unicodedata.normalize('NFD', text)
		text = text.replace('\u200d', '').replace('\u200e', '')
		text = text.replace('\t', ' ')
		text = text.replace('\n', '')
		text = re.sub(r'<[^>]+>', '', text)
		return text

def main():
	parser = argparse.ArgumentParser(
		description="Build the Scriptures JSON database from Sefaria sources.")
	parser.add_argument(
		"command",
		choices=["download", "build"],
		help="run 'download' to fetch source JSONs into the repo‑download folder, "
			 "or 'build' to convert them into the repo‑json folder.")
	args = parser.parse_args()

	if args.command == "download":
		Source.download()
	elif args.command == "build":
		Source.build()

if __name__ == "__main__":
	main()