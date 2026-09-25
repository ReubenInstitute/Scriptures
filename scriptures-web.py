#!/usr/bin/env python3
from flask import Flask, send_file
from jinja2 import Template
from Scriptures import Scriptures

app = Flask(__name__)
s = Scriptures()

def enumerate_filter(seq, start=0):
	return enumerate(seq, start=start)

HTML = Template("""
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Scriptures</title>
	<link rel="stylesheet" href="/styles.css">
</head>
<body>
	{{content}}
	<section class="navigation">
		{% for name, url in links %}
			<a href="{{url}}">{{name}}</a> • 
		{% endfor %}
		<a href="/">ראשי</a>
	</section>
	<script type="module" src="/script.js"></script>
</body>
</html>
""")
HTML.environment.filters['enumerate'] = enumerate_filter

def render(content, links=[]):
	return HTML.render(content=content, links=links)

def H(template_string, **kwargs):
	return Template(template_string).render(**kwargs)

@app.route('/')
def index():
	h = H("""
	<ul>
		<li><a href="/bible">תנ"ך</a></li>
		<li><a href="/mishnah">משנה</a></li>
		<li><a href="/bavli">תלמוד בבלי</a></li>
		<li><a href="/yerushalmi">תלמוד ירושלמי</a></li>
		<li><a href="/zohar">זוהר</a></li>
		<li><a href="/zohar-chadash">זוהר חדש</a></li>
		<li><a href="/tikkunei-zohar">תיקוני זוהר</a></li>
	</ul>
	""")
	return render(h)

@app.route('/bible')
def bible():
	books = s.bible.books
	h = H("""
	<h1>תנ"ך</h1>
	<ul>
		{% for book in books %}
		<li><a href="/bible/{{book.number}}">{{book.hebrew_name}}</a></li>
		{% endfor %}
	</ul>
	""", books=books)
	return render(h)

@app.route('/bible/<int:book>')
def bible_book(book):
	book = s.bible.books[book - 1]
	h = H("""
	<h1>{{book.hebrew_name}}</h1>
	<ul>
		{% for chapter in book.chapters %}
		<li><a href="/bible/{{book.number}}/{{chapter.number}}">פרק {{chapter.hebrew_fancy_number}}</a></li>
		{% endfor %}
	</ul>
	""", book=book)
	return render(h, [('תנ"ך', '/bible')])

@app.route('/bible/<int:book>/<int:chapter>')
def bible_chapter(book, chapter):
	book = s.bible.books[book - 1]
	chapter = book.chapters[chapter - 1]
	h = H("""
	<h1>{{book.hebrew_name}} - פרק {{chapter.hebrew_fancy_number}}</h1>
	<section class='scriptures'>
		{% for verse in chapter.verses %}
		<div class="verse"><span class="verse-number">{{verse.hebrew_number}}</span> {{verse.text}}</div>
		{% endfor %}
	</section>
	""", book=book, chapter=chapter)
	return render(h, [('תנ"ך', '/bible'), (book.hebrew_name, f'/bible/{book.number}')])

@app.route('/mishnah')
def mishnah():
	tractates = s.mishnah.tractates
	h = H("""
	<h1>משנה</h1>
	<ul>
		{% for i, tractate in tractates|enumerate(1) %}
		<li><a href="/mishnah/{{i}}">{{tractate.hebrew_name}}</a></li>
		{% endfor %}
	</ul>
	""", tractates=tractates)
	return render(h)

@app.route('/mishnah/<int:tractate>')
def mishnah_tractate(tractate):
	tractate = s.mishnah.tractates[tractate-1]
	h = H("""
	<h1>{{tractate.hebrew_name}}</h1>
	<ul>
		{% for chapter in tractate.chapters %}
		<li><a href="/mishnah/{{tractate.number}}/{{chapter.number}}">פרק {{chapter.hebrew_fancy_number}}</a></li>
		{% endfor %}
	</ul>
	""", tractate=tractate)
	return render(h, [('משנה', '/mishnah')])

@app.route('/mishnah/<int:tractate>/<int:chapter>')
def mishnah_chapter(tractate, chapter):
	tractate = s.mishnah.tractates[tractate-1]
	chapter = tractate.chapters[chapter-1]
	h = H("""
	<h1>{{tractate.hebrew_name}} - פרק {{chapter.hebrew_fancy_number}}</h1>
	<section class='scriptures'>
		{% for mishnaya in chapter.mishnayot %}
		<div class="verse">
			<span class="verse-number">משנה {{mishnaya.hebrew_fancy_number}}</span>
			{{mishnaya.text}}
		</div>
		{% endfor %}
	</section>
	""", tractate=tractate, chapter=chapter)
	return render(h, [('משנה', '/mishnah'), (tractate.hebrew_name, f'/mishnah/{tractate.number}')])

@app.route('/bavli')
def bavli():
	tractates = [tractate for tractate in s.talmud.bavli.tractates if tractate is not None]
	h = H("""
	<h1>תלמוד בבלי</h1>
	<ul>
		{% for i, tractate in tractates|enumerate(1) %}
		<li><a href="/bavli/{{i}}">{{tractate.hebrew_name}}</a></li>
		{% endfor %}
	</ul>
	""", tractates=tractates)
	return render(h)

@app.route('/bavli/<int:tractate>')
def bavli_tractate(tractate):
	try:
		tractate = s.talmud.bavli.tractates[tractate-1]
		if tractate is None: return "Tractate not found", 404
	except (IndexError, AttributeError):
		return "Tractate not found", 404
	h = H("""
	<h1>{{tractate.hebrew_name}}</h1>
	<ul>
		{% for page in tractate.pages %}
		<li><a href="/bavli/{{tractate.number}}/{{page.number}}">דף {{page.hebrew_fancy_number}}</a></li>
		{% endfor %}
	</ul>
	""", tractate=tractate)
	return render(h, [('תלמוד בבלי', '/bavli')])

@app.route('/bavli/<int:tractate>/<int:page>')
def bavli_page(tractate, page):
	try:
		tractate = s.talmud.bavli.tractates[tractate-1]
		if tractate is None: return "Tractate not found", 404
		page = tractate.pages[page-1]
	except (IndexError, AttributeError):
		return "Page not found", 404
	h = H("""
	<h1>{{tractate.hebrew_name}} - דף {{page.hebrew_fancy_number}}</h1>
	<section class='scriptures'>
		{% for verse in page.verses %}
		<div class="verse"><span class="verse-number">{{verse.hebrew_number}}</span> {{verse.text}}</div>
		{% endfor %}
	</section>
	""", tractate=tractate, page=page)
	return render(h, [('תלמוד בבלי', '/bavli'), (tractate.hebrew_name, f'/bavli/{tractate.number}')])

@app.route('/yerushalmi')
def yerushalmi():
	tractates = [tractate for tractate in s.talmud.yerushalmi.tractates if tractate is not None]
	h = H("""
	<h1>תלמוד ירושלמי</h1>
	<ul>
		{% for i, tractate in tractates|enumerate(1) %}
		<li><a href="/yerushalmi/{{i}}">{{tractate.hebrew_name}}</a></li>
		{% endfor %}
	</ul>
	""", tractates=tractates)
	return render(h)

@app.route('/yerushalmi/<int:tractate>')
def yerushalmi_tractate(tractate):
	try:
		tractate = s.talmud.yerushalmi.tractates[tractate-1]
		if tractate is None: return "Tractate not found", 404
	except (IndexError, AttributeError):
		return "Tractate not found", 404
	h = H("""
	<h1>{{tractate.hebrew_name}}</h1>
	<ul>
		{% for chapter in tractate.chapters %}
		<li><a href="/yerushalmi/{{tractate.number}}/{{chapter.number}}">פרק {{chapter.hebrew_fancy_number}}</a></li>
		{% endfor %}
	</ul>
	""", tractate=tractate)
	return render(h, [('תלמוד ירושלמי', '/yerushalmi')])

@app.route('/yerushalmi/<int:tractate>/<int:chapter>')
def yerushalmi_chapter(tractate, chapter):
	tractate = s.talmud.yerushalmi.tractates[tractate-1]
	if tractate is None: return "Tractate not found", 404
	chapter = tractate.chapters[chapter-1]
	h = H("""
	<h1>{{tractate.hebrew_name}} - פרק {{chapter.hebrew_number}}</h1>
	<section class='scriptures'>
		{% for paragraph in chapter.paragraphs %}
		{% for verse in paragraph.verses %}
		<div class="verse"><span class="verse-number">{{verse.hebrew_number}}</span> {{verse.text}}</div>
		{% endfor %}
		{% endfor %}
	</section>
	""", tractate=tractate, chapter=chapter)
	return render(h, [('תלמוד ירושלמי', '/yerushalmi'), (tractate.hebrew_name, f'/yerushalmi/{tractate.number}')])

@app.route('/zohar')
def zohar():
	chapters = s.zohar.main.chapters
	h = H("""
	<h1>זוהר</h1>
	<ul>
		{% for i, chapter in chapters|enumerate(1) %}
		<li><a href="/zohar/{{i}}">{{chapter.hebrew_title}}</a></li>
		{% endfor %}
	</ul>
	""", chapters=chapters)
	return render(h)

@app.route('/zohar/<int:chapter>')
def zohar_chapter(chapter):
	chapter = s.zohar.main.chapters[chapter-1]
	h = H("""
	<h1>{{chapter.hebrew_title}}</h1>
	<ul>
		{% for i, article in chapter.articles|enumerate(1) %}
		<li><a href="/zohar/{{chapter.number}}/{{i}}">מאמר {{article.hebrew_fancy_number}}</a></li>
		{% endfor %}
	</ul>
	""", chapter=chapter)
	return render(h, [('זוהר', '/zohar')])

@app.route('/zohar/<int:chapter>/<int:article>')
def zohar_article(chapter, article):
	chapter = s.zohar.main.chapters[chapter-1]
	article = chapter.articles[article-1]
	h = H("""
	<h1>{{chapter.hebrew_title}} - מאמר {{article.hebrew_fancy_number}}</h1>
	<section class='scriptures'>
		{% for i, verse in article.verses|enumerate(1) %}
		<div class="verse"><span class="verse-number">{{verse.hebrew_number}}</span> {{verse.text}}</div>
		{% endfor %}
	</section>
	""", chapter=chapter, article=article)
	return render(h, [('זוהר', '/zohar'), (chapter.hebrew_title, f'/zohar/{chapter.number}')])

@app.route('/zohar-chadash')
def zohar_chadash():
	chapters = s.zohar.chadash.chapters
	h = H("""
	<h1>זוהר חדש</h1>
	<ul>
		{% for i, chapter in chapters|enumerate(1) %}
		<li><a href="/zohar-chadash/{{i}}">{{chapter.hebrew_title}}</a></li>
		{% endfor %}
	</ul>
	""", chapters=chapters)
	return render(h)

@app.route('/zohar-chadash/<int:chapter>')
def zohar_chadash_chapter(chapter):
	chapter = s.zohar.chadash.chapters[chapter-1]
	h = H("""
	<h1>{{chapter.hebrew_title}}</h1>
	<section class='scriptures'>
		{% for verse in chapter.verses %}
		<div class="verse"><span class="verse-number">{{verse.hebrew_number}}</span> {{verse.text}}</div>
		{% endfor %}
	</section>
	""", chapter=chapter)
	return render(h, [('זוהר חדש', '/zohar-chadash')])

@app.route('/tikkunei-zohar')
def tikkunei_zohar():
	chapters = s.zohar.tikkunim.chapters
	h = H("""
	<h1>תיקוני זוהר</h1>
	<ul>
		{% for chapter in chapters %}
		<li><a href="/tikkunei-zohar/{{chapter.number}}">תיקון {{chapter.hebrew_fancy_number}}</a></li>
		{% endfor %}
	</ul>
	""", chapters=chapters)
	return render(h)

@app.route('/tikkunei-zohar/<int:chapter>')
def tikkunei_zohar_chapter(chapter):
	chapter = s.zohar.tikkunim.chapters[chapter-1]
	h = H("""
	<h1>תיקון {{chapter.hebrew_fancy_number}}</h1>
	<section class='scriptures'>
		{% for verse in chapter.verses %}
		<div class="verse"><span class="verse-number">{{verse.hebrew_number}}</span> {{verse.text}}</div>
		{% endfor %}
	</section>
	""", chapter=chapter)
	return render(h, [('תיקוני זוהר', '/tikkunei-zohar')])

@app.route('/fonts/<path:filename>')
def serve_font(filename):
	try:
		return send_file(f"/usr/share/fonts/reubeninstitute/{filename}")
	except FileNotFoundError:
		return "File not found", 404

@app.route('/<path:filename>')
def serve_file(filename):
	try:
		return send_file(f"{filename}")
	except FileNotFoundError:
		return "File not found", 404

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="Reuben Institute scriptures web viewer")
	parser.add_argument('--host', default='127.0.0.1', help="interface to bind (default: 127.0.0.1)")
	parser.add_argument('--port', type=int, default=5000, help="port to bind (default: 5000)")
	args = parser.parse_args()
	app.run(host=args.host, port=args.port, debug=True)