"""Build a conservative global historical office inventory and fetch holders.
Country headings and birth/death dates never determine a reign. Office-holder
claims and exact bounded P39 appointments are kept as independent evidence.
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.local/python'))
from enrich_polities import simplify, label

CACHE = ROOT / '.local/global-archive-review'
CACHE.mkdir(exist_ok=True)


def read(path):
    return json.loads(path.read_bytes())


def write(name, data):
    (CACHE / name).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf8')


def human(e):
    return any((r := simplify(c)) and r['value'] == 'Q5' for c in e.get('claims', {}).get('P31', []))


def fetch(ids, pool, name):
    saved = CACHE / (name + '-downloaded.json')
    added = read(saved) if saved.exists() else {}
    pool.update(added)
    missing = sorted({q for q in ids if str(q).startswith('Q')} - pool.keys())
    for i in range(0, len(missing), 40):
        group = missing[i:i + 40]
        params = urllib.parse.urlencode({'action': 'wbgetentities', 'format': 'json', 'ids': '|'.join(group),
                                        'props': 'labels|claims|descriptions', 'languages': 'zh-hans|zh|en'})
        req = urllib.request.Request('https://www.wikidata.org/w/api.php?' + params,
                                     headers={'User-Agent': 'GuanlanAtlas/1.6 educational historical atlas'})
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                result = json.load(response)['entities']
        except urllib.error.HTTPError as error:
            if error.code != 429: raise
            write(name + '-downloaded.json', added)
            print('Official endpoint requested a rate-limit pause; cache retained.', flush=True)
            time.sleep(min(45, max(20, int(error.headers.get('Retry-After', '30')))))
            with urllib.request.urlopen(req, timeout=45) as response:
                result = json.load(response)['entities']
        pool.update(result)
        added.update(result)
        write(name + '-downloaded.json', added)
        print(name, min(i + 40, len(missing)), '/', len(missing), flush=True)
        time.sleep(1.5)
    return pool


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['inventory', 'fetch', 'apply'])
    args = parser.parse_args()
    pool_path = CACHE / 'entities.json'
    if pool_path.exists():
        pool = read(pool_path)
    else:
        pool = read(ROOT / '.local/postwar-review/cached-entities.json')
        sources = [(ROOT / '.local/wikidata', '*.json'),
                   (ROOT / '.local/historical-review-2026-10-31', '*people*.json'),
                   (ROOT / '.local/historical-review-2026-10-31', '*offices*.json'),
                   (ROOT / '.local/postwar-review', '*people*.json')]
        for folder, pattern in sources:
            for path in folder.glob(pattern):
                data = read(path)
                if not isinstance(data, dict): continue
                for q, e in data.items():
                    if isinstance(e, dict) and e.get('claims'): pool[q] = e
        write('entities.json', pool)
    facts = read(ROOT / 'public/data/polity-facts.json')
    if args.stage in ['inventory', 'fetch']:
        offices = defaultdict(list)
        for q, e in facts['entities'].items():
            for field, prop in [('ruler', 'P1906'), ('headOfGovernment', 'P1313')]:
                for c in pool.get(q, {}).get('claims', {}).get(prop, []):
                    r = simplify(c)
                    if r and isinstance(r['value'], str): offices[r['value']].append({'country': q, 'field': field, 'from': r['from'], 'to': r['to']})
            for field in ['ruler', 'headOfGovernment']:
                for r in e['fields'].get(field, []):
                    value = r.get('value')
                    if value in pool and not human(pool[value]) and pool[value].get('claims', {}).get('P1308'):
                        offices[value].append({'country': q, 'field': field, 'from': r.get('from'), 'to': r.get('to')})
        # Explicit title of the Prussian kings is an office, not a human.
        offices['Q3240735'].append({'country': 'Q27306', 'field': 'ruler', 'from': 1701, 'to': 1918})
        offices = {q: list({json.dumps(r, sort_keys=True): r for r in rows}.values()) for q, rows in offices.items()}
        write('offices.json', offices)
        print('Exact historical office definitions:', len(offices), flush=True)
        if args.stage == 'inventory': return
        fetch(offices, pool, 'offices')
        write('entities.json', pool)
        candidates = set()
        for q in offices:
            for c in pool.get(q, {}).get('claims', {}).get('P1308', []):
                r = simplify(c)
                if r and isinstance(r['value'], str): candidates.add(r['value'])
        fetch(candidates, pool, 'office-holders')
        write('entities.json', pool)
        print('Office-holder candidates:', len(candidates), 'cached humans:', sum(human(e) for e in pool.values()), flush=True)
        return

    offices = read(CACHE / 'offices.json')
    curated = read(ROOT / 'public/data/curated-facts.json')
    lifetimes = {}
    for path in (ROOT / 'public/data/temporal').glob('*.geojson'):
        for f in read(path)['features']:
            p = f['properties']; q = curated['identities'].get(p['NAME'], p.get('qid'))
            if not q: continue
            lo, hi = lifetimes.get(q, (p['validFrom'], p['validTo']))
            lifetimes[q] = (min(lo, p['validFrom']), max(hi, p['validTo']))
    lifetimes['Q27306'] = (1701, 1918)
    lifetimes['Q43287'] = (1871, 1918)
    tag = 'global-office-review-2026-10-31'
    added, removed, ambiguous = [], [], []
    # Existing deliberately collective/vacancy entries are not persons and are
    # preserved. Known office titles mistakenly used as people are moved to audit.
    for country, e in facts['entities'].items():
        for field in ['ruler', 'headOfGovernment']:
            rows = []
            for r in e['fields'].get(field, []):
                if r.get('supplement') == tag: continue
                value = r.get('value')
                if value in offices and value in pool and not human(pool[value]) and not r.get('kind'):
                    removed.append({'country': country, 'field': field, **r})
                    continue
                rows.append(r)
            if field in e['fields']: e['fields'][field] = rows
    for person, e in pool.items():
        if not human(e): continue
        for claim in e.get('claims', {}).get('P39', []):
            term = simplify(claim)
            if not term or term['from'] is None or term['to'] is None or term['from'] > term['to'] or term['from'] > 1900: continue
            office = term['value']
            targets = offices.get(office, [])
            # A generic title like "king" cannot identify one of many countries.
            countries = {r['country'] for r in targets}
            if len(countries) > 3:
                ambiguous.append({'office': office, 'person': person, 'countries': len(countries)})
                continue
            for target in targets:
                if target['from'] is not None and term['to'] < target['from']: continue
                if target['to'] is not None and term['from'] > target['to']: continue
                country, field = target['country'], target['field']
                if country not in facts['entities']: continue
                lo, hi = lifetimes.get(country, (-3400, 1900))
                if term['to'] < lo or term['from'] > hi: continue
                # A title inherited by a successor state is not an excuse to
                # display its predecessors' kings centuries before that state.
                start, end = max(lo, term['from']), min(hi, term['to'])
                rows = facts['entities'][country]['fields'].setdefault(field, [])
                if any(r.get('value') == person and r.get('from') == start and r.get('to') == end for r in rows): continue
                row = {**term, 'from': start, 'to': end, 'value': person, 'label': label(e), 'office': office,
                       'roleLabel': label(pool.get(office, {})), 'supplement': tag,
                       'citation': term['citation'] or ['https://www.wikidata.org/wiki/' + person + '#P39'],
                       'derived': True, 'dateSource': 'exact bounded P39 / ' + office,
                       'inference': '按准确职务及有起止日期的任期匹配；不使用出生／去世日期或网页相邻国家标题。'}
                rows.append(row)
                facts['labels'][person] = row['label']
                added.append({'country': country, 'field': field, **row})
    # Country-side holder lists often retain the full reign even when the
    # person's P39 entry is incomplete (including all nine Prussian kings).
    for office, targets in offices.items():
        if len({r['country'] for r in targets}) > 3: continue
        for claim in pool.get(office, {}).get('claims', {}).get('P1308', []):
            term = simplify(claim)
            if not term or term['from'] is None or term['to'] is None or term['from'] > 1900 or term['from'] > term['to']: continue
            person = term['value']
            if not human(pool.get(person, {})): continue
            for target in targets:
                country, field = target['country'], target['field']
                lo, hi = lifetimes.get(country, (-3400, 1900))
                start, end = max(lo, term['from']), min(hi, term['to'])
                if target['from'] is not None: start = max(start, target['from'])
                if target['to'] is not None: end = min(end, target['to'])
                if start > end or country not in facts['entities']: continue
                rows = facts['entities'][country]['fields'].setdefault(field, [])
                if any(r.get('value') == person and r.get('from') == start and r.get('to') == end for r in rows): continue
                role = label(pool.get(office, {}))
                if re.search(r'[A-Za-z]', role): role = facts['entities'][country]['label'] + ('君主／元首' if field == 'ruler' else '政府首脑')
                row = {**term, 'from': start, 'to': end, 'value': person, 'label': label(pool[person]), 'office': office,
                    'roleLabel': role, 'rank': 'preferred', 'supplement': tag, 'derived': True,
                    'citation': term['citation'] or ['https://www.wikidata.org/wiki/' + office + '#P1308'],
                    'dateSource': 'dated exact office P1308 / ' + office,
                    'inference': '采用该准确职位名录中有起止日期的在位人物，不以职务名称冒充人名。'}
                if country == 'Q27306': row['citation'].append('https://www.stadtmuseum-cottbus.de/cottbus-lexikon-detail/koenige-von-preussen.html')
                rows.append(row); facts['labels'][person] = row['label']; added.append({'country': country, 'field': field, **row})
    for r in added:
        if re.search(r'[A-Za-z]', r.get('roleLabel', '')):
            r['roleLabel'] = facts['entities'][r['country']]['label'] + ('君主／元首' if r['field'] == 'ruler' else '政府首脑')
            for row in facts['entities'][r['country']]['fields'][r['field']]:
                if row.get('supplement') == tag and row['value'] == r['value'] and row.get('office') == r.get('office'): row['roleLabel'] = r['roleLabel']
    old_report = ROOT / 'public/data/global-office-review.json'
    if old_report.exists():
        previous = read(old_report).get('removedOfficeTitles', [])
        removed = list({json.dumps(r, sort_keys=True): r for r in previous + removed}.values())
    (ROOT / 'public/data/polity-facts.json').write_text(json.dumps(facts, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
    report = {'reviewedAt': '2026-10-31', 'method': '准确国家职务 + 已核对为人类的人物 + 有界任期；通用职务不能自动指定国家。',
              'records': added, 'removedOfficeTitles': removed, 'ambiguousOfficeMatchesSkipped': ambiguous,
              'summary': {'records': len(added), 'countries': len({r['country'] for r in added}), 'people': len({r['value'] for r in added}), 'titleErrorsRemoved': len(removed)}}
    (ROOT / 'public/data/global-office-review.json').write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
    write('verified-people.json', {r['value']: pool[r['value']] for r in added})
    print(report['summary'], flush=True)


if __name__ == '__main__':
    main()
