#!/usr/bin/env python3
"""Main functionality for bibble."""

# pylint doesn't like our concise variable names; yolo
# pylint: disable=invalid-name

import re
from calendar import month_name

import click
from pybtex.database.input import bibtex
import jinja2
import jinja2.sandbox


MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


def _author_fmt(author):
    """Format an author's full name."""
    return u' '.join(author.first() + author.middle() + author.last())


def _andlist(ss, sep=', ', seplast=', and ', septwo=' and '):
    """Comma-separate a list of strings according to English rules.

    Enforces the Oxford comma.
    """
    if len(ss) <= 1:
        return ''.join(ss)
    if len(ss) == 2:
        return septwo.join(ss)
    return sep.join(ss[:-1]) + seplast + ss[-1]


def _author_list(authors):
    """Format a list of authors."""
    return _andlist(list(map(_author_fmt, authors)))


def _venue_type(entry):
    """Expand a venue type to a longer English description."""
    venuetype = ''
    if entry.type == 'inbook':
        venuetype = 'Chapter in '
    elif entry.type == 'techreport':
        venuetype = 'Technical Report '
    elif entry.type == 'phdthesis':
        venuetype = 'Ph.D. thesis, {}'.format(entry.fields['school'])
    elif entry.type == 'mastersthesis':
        venuetype = 'Master\'s thesis, {}'.format(entry.fields['school'])
    return venuetype


def _venue(entry):
    """Format an entry's venue data."""
    f = entry.fields
    venue = ''
    if entry.type == 'article':
        venue = f['journal']
        try:
            if f['volume'] and f['number']:
                venue += ' {0}({1})'.format(f['volume'], f['number'])
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
        venue = f['title']
    elif entry.type == 'techreport':
        venue = '{0}, {1}'.format(f['number'], f['institution'])
    elif entry.type == 'phdthesis' or entry.type == 'mastersthesis':
        venue = ''
    else:
        venue = 'Unknown venue (type={})'.format(entry.type)

    # remove curlies from venues -- useful in TeX, not here
    venue = venue.replace('{','').replace('}','')
    return venue


def _title(entry):
    """Format a title field for HTML display."""
    if entry.type == 'inbook':
        title = entry.fields['chapter']
    else:
        title = entry.fields['title']

    # remove curlies from titles -- useful in TeX, not here
    title = title.replace('{', '').replace('}', '')
    return title


def _main_url(entry):
    """Get an entry's URL field (url or ee)."""
    urlfields = ('url', 'ee')
    for f in urlfields:
        if f in entry.fields:
            return entry.fields[f]
    return None


def _extra_urls(entry):
    """Gather an entry's "*_url" fields into a dictionary.

    Returns a dict of URL types to URLs, e.g.
       { 'nytimes': 'http://nytimes.com/story/about/research.html',
          ... }
    """
    urls = {}
    for k, v in entry.fields.items():
        k = k.lower()
        if not k.endswith('_url'):
            continue
        k = k[:-4]
        urltype = k.replace('_', ' ')
        urls[urltype] = v
    return urls


def _month_match(mon):
    """Turn a month specifier (name or number) into a month name."""
    if re.match('^[0-9]+$', mon):
        return int(mon)
    return MONTHS[mon.lower()[:3]]


def _month_name(monthnum):
    """Turn a month number into a month name."""
    try:
        return month_name[int(monthnum)]
    except (ValueError, KeyError):
        return ''


def _sortkey(entry):
    """Generate a sorting key for an entry based on its date."""
    e = entry.fields
    year = '{:04d}'.format(int(e['year']))
    try:
        monthnum = _month_match(e['month'])
        year += '{:02d}'.format(monthnum)
    except KeyError:
        year += '00'
    return year


@click.command()
@click.argument('bibfile', metavar='BIBFILE.bib', type=click.File('r'))
@click.argument('template', metavar='TEMPLATE.html', type=click.File('r'))
@click.option('-o', '--output', type=click.File('w'))
def main(bibfile, template, output):
    # pylint: disable=unused-argument
    """Render a BibTeX .bib file to HTML using an HTML template."""
    tenv = jinja2.sandbox.SandboxedEnvironment()
    tenv.filters['author_fmt'] = _author_fmt
    tenv.filters['author_list'] = _author_list
    tenv.filters['title'] = _title
    tenv.filters['venue_type'] = _venue_type
    tenv.filters['venue'] = _venue
    tenv.filters['main_url'] = _main_url
    tenv.filters['extra_urls'] = _extra_urls
    tenv.filters['monthname'] = _month_name
    tmpl = tenv.from_string(template.read())

    # Parse the BibTeX file.
    db = bibtex.Parser().parse_stream(bibfile)

    # Include the bibliography key in each entry.
    for k, v in db.entries.items():
        v.fields['key'] = k

    # Render the template.
    bib_sorted = sorted(db.entries.values(), key=_sortkey, reverse=True)
    out = tmpl.render(entries=bib_sorted)
    print(out)


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
