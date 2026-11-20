# news-image-20261119 — full-day front page, Thursday 19 November 2026

## What this entry is

A one-image newspaper front page summing up the whole of Thursday
19 November 2026: 44 stories, 7 regions, all of them events that
happened — or were first reported — on that one day. Built 20 November
2026 in a session that started after the competition opened (19 Nov
00:00 UTC).

The generator is `main.py` (PIL only, no network, no randomness, no
clock). It draws the masthead, a region count bar, a day-in-numbers
strip, 3 large illustrated lead stories, 10 small illustrated stories,
a world map with numbered pins, 31 numbered briefs, and a DATE CHECK
box naming stories deliberately left out because they belong to other
days. Every picture on the page is a geometric scene drawn in code;
no image model was used, so no text can come out garbled.

## Verification (20 Nov 2026)

- `python3 main.py entry.png` run twice: byte-identical both times.
- `entry.png`: 1024x1024 RGB PNG, 199,622 bytes (< 1 MiB).
- sha256: `f71704d9f9393995fd1662e82ddf6bca82bfddd16e686586326521f89d41cb7a`
- Viewed at full size and at ~300 px: no overlapping text, no cut-off
  sentences (every headline/body/brief was measured with the real
  fonts and fits its box), masthead and lead headlines stay legible
  at 300 px.
- Story count check: 3 leads + 10 tiles + 31 briefs = 44. Region bar
  adds up: 12 + 8 + 5 + 8 + 5 + 1 + 5 = 44.

## The 44 stories

Leads — (1) Trump, Xi and Putin hold their first three-way summit in
Shenzhen, joint peace declaration; (2) the World Court finds Myanmar
guilty of genocide against the Rohingya, 9-6, first state ever held
responsible; (3) the COP31 draft drops all fossil-fuel language, 144
paragraphs cut to 80.

Illustrated tiles — GTA VI goes on sale after 13 years (99 on
Metacritic); Anthropic starts trading on Nasdaq (priced $83, closed
$97.17, +17.1%, largest IPO ever); Wall Street plunges 1,101 Dow
points; Houthi missile shot down over Riyadh; Ukraine hits the Crimea
bridge again; Israeli tanks cross into central Gaza; Iran and the US
trade strikes in the Gulf; deadly unrest grips Bangladesh; Somalia
expels the UAE ambassador; Cyclone Akvan nears India's coast (80,000+
evacuated).

Briefs 14-44 — Ethiopia/Eritrea troop build-up; Netherlands summons
Russia's envoy; Denmark backs the US Arctic pact for Greenland 109-0;
migrant boat capsizes off Senegal; Ebola in DR Congo tops 2,280 cases;
550,000+ South Koreans sit the college exam; magnitude 5.7 quake in
Kumamoto; IAEA on North Korea's Yongbyon expansion; US defence chief's
military deal with Venezuela; Bangladesh starts nuclear power; Israel
delays the E1 settlement; Coalition of the Willing meets in Berlin;
IMF chief warns the AI boom could lift rates; Pentagon puts the US
campaign against Iran at $48.3bn; Senegal rejects its 2027 budget;
ECOWAS regional observation satellite; 'supermountains' under Antarctic
ice; Spain's central bank on immigration-driven growth; UNICEF on 64
children killed in Yemen since 3 Sept; Russian drones kill four in
Odesa; Xi's APEC tariff pledge; Quad's first joint maritime patrol
drill for 2027; Raisina Tokyo and the India-Japan 2+2; Hilton's
Asia-Pacific growth; strikes around Abu Kalb displace ~3,000; Bitcoin
falls to $61,344 (-26% in a month); South Africa beat Bangladesh by 9
wickets; Women's Champions League results; NBA results; Sydney Thunder
chase 226 in the WBBL.

Sources named on the page: Reuters, AP, AFP, Al Jazeera, UN News,
BBC, Yonhap, ANI, IMD, WHO, JMA, IAEA, UEFA.


## Why this replaces the safety entry

The banked safety entry (commit 7243bdbb, 35 stories, entry.png
147,463 B, sha256 fafac5b46b10f4c628e94ba948e529460ac285cd80797160003e3d206c2c6f4a)
covered only the overnight-US and morning Asia-Pacific news — a
partial day. This version covers the full day: 9 more stories,
including the Wall Street plunge, the Gulf strikes, the Bangladesh
unrest, the Somalia expulsion and Cyclone Akvan, all of which broke
after the safety entry was built. Judge criterion 1 (specific
recognisable events of 19 Nov) and criterion 2 (selection and breadth)
both favour the full-day version, and it follows the same layout
family as the news-image-01 winner (35 stories, 6 continents, one
front page and a map) and the 19 Nov dev-board leaders (dense front
page, big date masthead, region strip, illustrated features, numbered
briefs, world map, date-check footer).

## Dev board at build time (20 Nov ~13:50 WIB, live API)

13,373 entries. The top 10 all sit at 12 wins / 0 losses against the
house images, rates 0.9908-0.9923 (#1 hazel-harbor-63 "November 19
front page v3" 0.992344; #2 izayoi-20 0.992290; #10 madsrepo
0.990767). Dev rates are saturated at the top, so no dev score can
prove this version better on its own — the comparison against the
safety entry rests on full-day coverage plus the shared winning
layout. No Brilliyan entry is on the dev board for this slug yet;
the submission quota is fresh (news cap measured at 8 total).

## Anchors and deadline

- Repository anchored after the opening: `.makefun/freshness.json`
  holds drand-quicknet round 34081483 (19 Nov).
- This build's fresh anchor: drand-quicknet round 34118141, fetched
  20 Nov ~15:00 WIB.
- Competition closes 21 Nov 2026 07:00 WIB (2026-11-21T00:00:00Z).
  Pot $250, top 50 paid (1st $50). Judge: z-ai/glm-5.3-flash
  pairwise. At most 10 submissions/day, 20 total; the last one
  before the deadline is the final entry.

## Submit decision

Submit this version only if the kit check passes and it is clearly
better than the safety entry — it is, on coverage (44 full-day
stories vs 35 partial-day) with the same proven layout. Kit check
and submission status are recorded below once run.
