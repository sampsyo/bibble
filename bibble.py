import sys
from pybtex.database.input import bibtex
import jinja2
import jinja2.sandbox

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

def _venue(entry):
    f = entry.fields
    if entry.type == 'article':
        venue = f['journal']
        try:
            if f['volume'] and f['number']:
                venue += '{0}({1})'.format(f['volume'], f['number'])
        except KeyError:
            pass
    elif entry.type == 'inproceedings':
        venue = f['booktitle']
        try:
            if f['series']:
                venue += ' ({})'.format(f['series'])
        except KeyError:
            pass
    elif entry.type == 'inbook':
        venue = 'Chapter in {}'.format(f['title'])
    elif entry.type == 'techreport':
        venue = 'Technical report {0}, {1}'.format(f['number'],
                                                   f['institution'])
    elif entry.type == 'phdthesis':
        venue = 'Ph.D. thesis, {}'.format(f['school'])
    else:
        venue = 'Unknown venue (type={})'.format(entry.type)
    return venue

def _title(entry):
    if entry.type == 'inbook':
        title = entry.fields['chapter']
    else:
        title = entry.fields['title']
    return title

def main(bibfile, template):
    # Load the template.
    tenv = jinja2.sandbox.SandboxedEnvironment()
    tenv.filters['author_fmt'] = _author_fmt
    tenv.filters['author_list'] = _author_list
    tenv.filters['title'] = _title
    tenv.filters['venue'] = _venue
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
