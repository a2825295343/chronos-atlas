"""Idempotently merge the reviewed historical war catalogue and detail records."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = json.loads((ROOT / 'public/data/historical-wars-supplements.json').read_bytes())
    for filename, key in [('conflicts.json', 'war'), ('war-details.json', 'detail')]:
        path = ROOT / 'public/data' / filename
        data = json.loads(path.read_bytes())
        rows = {row['id']: row for row in data['wars']}
        for supplement in source['wars']:
            row = supplement[key]
            rows[row['id']] = row
        data['wars'] = list(rows.values())
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
    print('Merged historical wars:', len(source['wars']))


if __name__ == '__main__':
    main()
