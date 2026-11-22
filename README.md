# The World in One Day — Sunday 22 November 2026

![best](https://img.shields.io/endpoint?url=https://make.fun/api/competitions/news-image-20261122/badge/best.svg)
![rank](https://img.shields.io/endpoint?url=https://make.fun/api/competitions/news-image-20261122/badge/rank.svg)
![reward](https://img.shields.io/endpoint?url=https://make.fun/api/competitions/news-image-20261122/badge/reward.svg)

One image that sums up the world's news of Sunday 22 November 2026, for
[make.fun's daily news-image contest](https://make.fun/c/news-image-20261122).

![the page](entry.png)

## What it is

A broadsheet front page for the day, drawn with nothing but Pillow: a nameplate
carrying the date, one large picture of the morning's biggest story, a lead
headline and standfirst, a timeline of the day in UTC, twelve further stories in
a four-column band, the day in five figures, and twelve briefs at the foot.

Every story is real and was first reported on 22 November 2026. The page names
its day on the nameplate and again in the folio, because the judge is not told
which day the contest is about and an image that names no day loses to one that
does.

## The stories

The page is built around the Russian cargo ship burning in the Gulf of Finland
after a drone attack — the morning's most consequential story — and sets the rest
of the day's breadth around it:

| Region | Story |
| --- | --- |
| Finland, Baltic | A Russian cargo ship burns after a drone attack |
| Mexico, Sinaloa | El Chapo Isidro seized in a raid that leaves eleven dead |
| Türkiye, Antalya | COP31 on the brink as a new draft reaches the floor |
| Gaza, Khan Younis | Displaced families protest as the strikes continue |
| Peru, Lima | A quake empties a cinema mid-film |
| Nigeria, Niger State | A funeral boat capsizes, killing at least 24 |
| Indonesia, West Java | A factory fire kills three and leaves 36 missing |
| France, Paris | A second night of rallies over the cost of living |
| South Korea, Seoul | The education minister resigns over an exam scandal |
| Ukraine, Lviv | Dashcam video shows a missile strike in the city |
| United States | The FBI investigates a hack of its criminal database |
| Mercury | A spacecraft arrives after an eight-year voyage |
| Somalia, Mogadishu | The president turns on the UAE, his former ally |

Plus twelve briefs from Italy, the US, Spain, Sudan, the UK, Kenya, Australia
and Belgium, each dated that day.

## How it is drawn

`draw.py` is the whole entry. It sets the page on one twelve-column grid that
runs from the nameplate to the folio, so every band starts and ends on the same
column edges and one vertical rhythm carries the height of the sheet.

The picture in the masthead is painted rather than plotted: a banded dawn sky, a
flat sea with swell strokes, the Finnish shore as a dark spit of pines, a hull
with a rust boot-topping and a white accommodation block aft, fire amidships
drawn as a hot core with tongues over it, and a smoke column that rises and then
bends away to the left. The drone that struck the ship sits high on the right
with its dashed course coming in from the edge. The whole picture is drawn onto
its own surface and pasted in, so the smoke cannot escape its frame — the first
draft bled a grey band across the nameplate, which is exactly the sort of thing
a judge sees and a test does not.

Two decisions came out of reading the judge's own rubric, which asks for an image
"legible at about 300 pixels across":

- **The grid stories carry their headline and nothing else.** At 300px a 7pt
  standfirst is grey texture, and texture does not tell a reader what happened.
  Every grid headline is set at 14pt and wraps to exactly two lines, so the band
  reads as twelve legible statements rather than a wall of speckle.
- **The picture is one large scene, not ten small icons.** The first draft gave
  every story a 34px thumbnail; a critic called them "abstract scribbles", and
  it was right — a scene cannot be read at 34px. One picture at 651x300 says
  more than ten thumbnails ever could.

## Checks

`verify.py` proves the page is laid out cleanly without needing eyes: it
re-runs the drawing through a recording surface and asserts that no text block
overlaps another, that nothing crosses the page margins, and that no block
overflows the band it was given.

```
python3 verify.py     # geometry: no overlaps, no overflow, no margin bleed
python3 draw.py       # writes entry.png (1024x1024, ~374 KB)
```

`main.ts` then copies that file to `/output/entry.png`, checking it against the
rules first: at most 1 MiB, a real PNG signature, IHDR first, dimensions within
1024, and an IEND chunk at the end so a truncated file is caught here rather
than scoring zero.

## Layout

```
python3 draw.py && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Licence

MIT. See `LICENSE`.
