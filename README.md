bibble
======

A real quick experiment to make a better BibTeX-to-HTML (or BibTeX-to-whatever)
converter using [Pybtex][] and [Jinja2][].

Install in a virtualenv:

    $ virtualenv venv
    $ . venv/bin/activate
    (venv)$ pip install -e .

Give `bibble` the name of a BibTeX file and a template. A sample template is
included.

    (venv)$ bibble citations.bib simple.html > citations.html

[Pybtex]: http://pybtex.sourceforge.net/
[Jinja2]: http://jinja.pocoo.org/
