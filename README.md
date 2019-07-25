bibble
======

A tool that turns a BibTeX file into a webpage through a template of your
choice.

You provide:
- A BibTeX file (`mypapers.bib`)
- A template (such as `simple.html` in this repository)

Then run:

    bibble mypapers.bib simple.html > mypapers.html

## Installation

Bibble is a plain Python program that you can install in a virtualenv:

```shell
$ python3 -m venv venv
$ . venv/bin/activate
(venv)$ pip install -U https://github.com/sampsyo/bibble/
# ...
(venv)$ bibble mypapers.bib simple.html > mypapers.html
```

## Template Format

See `simple.html` for a full example. Your template file is a plain old
[Jinja2][] template that has access to your bibliographic entries via a
variable called `entries`:

```html+django
<ul>
  {% for entry in entries %}
    <li>
        {{ entry.persons['author']|author_list }}.
        {{ entry|title }}.
        {{ entry.fields['month'] }}
        {{ entry.fields['year'] }}.
    </li>
  {% endfor %}
</ul>
```

Bibble provides several convenience functions such as `author_list` via
Jinja2's filter mechanism. See `simple.html` to see them all used.

## How it Works

Bibble parses a BibTeX file with [Pybtex][] and sends the result through the
[Jinja2][] templating engine.

It turns out you can generate formats _other than HTML_ just as easily by
writing your own template for a different format.

[Pybtex]: http://pybtex.sourceforge.net/
[Jinja2]: http://jinja.pocoo.org/
