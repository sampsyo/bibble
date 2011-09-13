import sys
from pybtex.database.input import bibtex
import jinja2

def _author_fmt(author):
    return u' '.join(author.first() + author.middle() + author.last())

def _andlist(ss, sep=', ', seplast=', and ', septwo=' and '):
    if len(ss) <= 1:
        return ''.join(ss)
    elif len(ss) == 2:
        return septwo.join(ss)
    else:
        return sep.join(ss[:-1]) + seplast + ss[-1]

def _author_list(authors):
    return _andlist(map(_author_fmt, authors))

def main(bibfile, template):
    # Load the template.
    tenv = jinja2.Environment()
    tenv.filters['author_fmt'] = _author_fmt
    tenv.filters['author_list'] = _author_list
    with open(template) as f:
        tmpl = tenv.from_string(f.read())

    # Parse the BibTeX file.
    with open(bibfile) as f:
        db = bibtex.Parser().parse_stream(f)

    # Render the template.
    out = tmpl.render(entries=db.entries.values())
    print out

if __name__ == '__main__':
    main(*sys.argv[1:])
