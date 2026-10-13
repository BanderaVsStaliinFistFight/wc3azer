# Azeroth for Warcraft III

**[`dist/(12)Azeroth.w3x`](dist/(12)Azeroth.w3x)** is a 12-player map of the whole world of Azeroth: terrain only, with no melee setup, gold mines, creeps or shops, ready to build a game on. It is built at **480 × 480 tiles**, the largest size Warcraft III supports. The playable area is 468 × 468 tiles, about 60,000 × 60,000 world units.

![Overview of the map](dist/preview.png)

*Overview render: capitals in red, waygates in violet, portal links between the continents in purple (the instance waygates are left unlinked to keep it readable). Cliff edges are drawn dark.*

## What's on the map

| Landmass | Zones |
|---|---|
| **Kalimdor** | Teldrassil, Darkshore, Moonglade, Felwood, Winterspring, Mount Hyjal, Azshara, Ashenvale, Stonetalon, the Barrens, Durotar, Desolace, Mulgore, Feralas, Thousand Needles, Dustwallow Marsh, Un'Goro Crater, Tanaris, Silithus, Uldum, plus Azuremyst, Bloodmyst, the Echo Isles and Theramore |
| **Eastern Kingdoms** | Quel'Danas, Eversong, Ghostlands, Tirisfal, both Plaguelands, Silverpine, Gilneas, Hillsbrad, Alterac, the Hinterlands, Arathi, Wetlands, Twilight Highlands, Dun Morogh, Loch Modan, Badlands, Searing Gorge, Burning Steppes, Redridge, Elwynn, Westfall, Duskwood, Deadwind Pass, Swamp of Sorrows, Blasted Lands, Stranglethorn. Gilneas is a compact peninsula continuing Lordaeron's west coast south of Silverpine, as on the City-States of Arathor map. The ring of Gilneas City sits by a harbour on its east side, two islets lie off its west coast, and the Greymane Wall seals it off from Silverpine. Tol Barad sits out in Baradin Bay to the south-east |
| **Northrend** | Follows the Wrath of the Lich King continent map across the top of the map: Borean Tundra and Howling Fjord as the southern lobes with Dragonblight's bay between them, Coldarra off Borean, Sholazar Basin, Wintergrasp, Icecrown, Crystalsong Forest, the Storm Peaks, Zul'Drak, the Grizzly Hills with Venture Bay, and the fjords of Howling Fjord |
| **The Great Sea** | The Maelstrom (a whirlpool of spiral shallows round a bottomless eye), the goblin isle of Kezan, and Kul Tiras, traced from the Battle for Azeroth map: Stormsong Valley in the north, Drustvar's peaks to the south-west, and Tiragarde Sound with Boralus to the south-east, split by Boralus harbour, its strait and a western inlet |

| **Instances** | 24 dungeons and raids, each a walled, cliff-edged island in a corner of the sea, reached through a waygate from its entrance in the world. North-west: Onyxia's Lair, Temple of Ahn'Qiraj, Caverns of Time, Wailing Caverns, Maraudon, Dire Maul, Azjol-Nerub, Zul'Farrak, Blackfathom Deeps, Razorfen Downs. North-east: Naxxramas, Ulduar, Icecrown Citadel, Stratholme, Zul'Aman. South: Molten Core, Karazhan, Zul'Gurub, the Deadmines, Sunken Temple, Uldaman, Halls of Origination, Gnomeregan, Scholomance |

### The look

The terrain follows the style of the big hand-made WoW maps for Warcraft III, such as WoW Reanimated. Only the look was used as a reference; none of that map's terrain or objects were copied.

- **Coasts.** Where high ground meets the sea, the shore is a cliff wall rising out of a pale shelf of shallows. Where the land behind is low, it runs down to a beach, about a third of the shoreline in all. Beaches are also kept wherever units must reach the water: along the wading straits and river mouths, at every shipyard and round the small islands.
- **Rivers and valleys.** Rivers wind from side to side, widen from a narrow stream at their spring pond to a broad mouth, and run through valleys. Water running off the land carves a branching network of valleys into everything: shallow swales across the plains, and deep gullies in the mountains. Mountain ranges bend instead of running ruler-straight, and broad swells keep the plains from lying flat.
- **Raised and sunken zones.** Highland zones stand one cliff level above their neighbours: Winterspring, Mount Hyjal, Stonetalon, Alterac, the Hinterlands, Dun Morogh, Searing Gorge, Icecrown, the Storm Peaks, Zul'Drak and Drustvar. Un'Goro Crater sinks one level below. Ramps, built the way the World Editor builds them, climb these edges wherever a road crosses and every couple of dozen tiles along them.
- **Massifs.** Sixteen great ranges tower over everything else, up to about 1,750 units high. They are stacks of up to five cliff levels topped with peaks, snow and great rock spires or glaciers, and no army can climb their cores. They are Stonetalon, the summit of Hyjal, Winterspring, Darkshore's range, the Feralas wall, the cliffs above Thousand Needles, the walls of Un'Goro, the Alterac Mountains, the Khaz Mountains, Blackrock Mountain, Redridge, the Thalassian highlands, the Blasted Lands wall, the Storm Peaks, the Icecrown glacier and the walls of Sholazar. Each is crossed only at its roads' passes: Dun Algaz through the Khaz Mountains, the Great Lift into Thousand Needles, two passes into Un'Goro, and two roads into Sholazar.
- **Mountain ranges.** The lesser ranges are broad massifs rising out of foothills, broken into peaks, saddles and spurs, and stepped by ragged cliff ledges. The high ground turns to bare rock and scree, with snow on the summits. Roads keep their passes open, and settlements stand in levelled clearings away from the slopes.
- **Getting about on foot.**
  - Outside the massifs, cliff ledges and plateaus get ramps so they are part of the land, not walled-off islands of it. Any patch of ground still sealed off gets a ramp to its neighbour.
  - Every camp and town lies on a track to the nearest road.
  - Wading straits reach Azuremyst, Bloodmyst, Tol Barad and Alcaz Island.
  - About 99% of the walkable land can be reached from the start locations, against 95% before; what is left is small ledges.
- **Forests.** Woods cover a share of each zone set by its climate. They grow thicker along rivers and lakes, climb the hillsides up to a treeline, break up into clumps and clearings, and fray into scattered trees at their edges. A second species is mixed in here and there: autumn trees among summer ones, pines in the snow, canopy giants in the jungles and Ashenvale. The ground under them is dark forest floor.
- **Ground detail.** The ground follows the lie of the land: each zone's lusher ground gathers on wet valley floors and along the water, and its dirt and rock on slopes and high, dry ground. Zone borders fray into one another instead of meeting on a line. Roads wander a little, as roads do. Flowers, shrubs and mushrooms dot open ground, reeds and cattails line the water, lily pads float on the lakes, and boulders lie on steep slopes and below cliffs. Boulders on walkable ground are written into the pathing map, and none of them is allowed to cut off a path.
- **Instances.** Each dungeon has a vestibule round its waygate, a pillared hall, and a raised dais at the far end, reached up a ramp. Floors are themed: lava cracks in Molten Core and Onyxia's Lair, sand and brick in the desert temples, brick and poison in the crypts, ice in the Northrend raids, and moss in the caverns.
- **Paved capitals:** a brick square with streets leading out along the roads.

There are 93 zones in all, counting the instances. Each zone has its own ground textures, tree type, relief and wildlife: jungle in Stranglethorn, blight in the Plaguelands, lava cracks in the Burning Steppes, cliff mesas in Thousand Needles and at Thunder Bluff, the crater rim around Un'Goro, and the Greymane Wall, a cliff rampart whose gate is the only way into Gilneas on foot. A few landmark doodads are placed too: the World Trees at Teldrassil and Hyjal, the Sunwell, the Frozen Throne, the ruins of Dalaran, the Dark Portal, and volcanoes at Blackrock and Un'Goro.

**Start locations** (one per player slot): Stormwind, Orgrimmar, Undercity, Darnassus, Ironforge, Thunder Bluff, Silvermoon City and Boralus, plus four in Northrend: Icecrown Citadel, Dalaran, Warsong Hold and Valgarde. Each stands in its capital's paved square.

**Getting between continents.** Nine pairs of mage portals (waygates) link the landmasses, and 24 more pairs lead into the instances. They sit about 17 tiles outside each capital, so no portal opens directly into a base:

- Stormwind ↔ Darnassus
- Orgrimmar ↔ Undercity
- Thunder Bluff ↔ Silvermoon
- Ironforge ↔ Dalaran
- Undercity ↔ Icecrown
- Orgrimmar ↔ Warsong Hold
- Menethil Harbor ↔ Valgarde
- Stormwind Harbor ↔ Boralus
- Ratchet ↔ Kezan

Shallow straits that ground units can wade across link Teldrassil and Azuremyst to Darkshore, Bloodmyst to Azuremyst, Tol Barad to Gilneas, and Alcaz Island, Theramore and the Echo Isles to the mainland.

**What's placed.**
- About 30,000 trees and some 3,400 boulders, plants and rock spires.
- The landmark doodads.
- The waygates.
- Wildlife critters in every zone.
- The 12 start locations.

There are no gold mines, creeps, shops or item drops. The ~60 towns and ~100 camp sites from the geography (Goldshire, Booty Bay, Crossroads, Gadgetzan, Dire Maul, Stratholme and the rest) are levelled clearings joined to the road network, left empty for you to fill. The towns are kept free of trees.

## Using it

You need **patch 1.29 or later** (Reforged included), because older patches cap maps at 256 × 256. Copy the `.w3x` into your maps folder, for example `Documents/Warcraft III/Maps/`.

It is a custom scenario, not a melee map. It has no triggers, so a game starts with no units, no resources and no victory conditions. It is a world to build on: open it in the World Editor and add your own triggers, units and gameplay. The World Editor files are included: preplaced units (start locations, waygates, critters), the waygates' destination regions, and an empty trigger list.

## Building it yourself

The map is generated entirely from code. Nothing is copied from Blizzard files.

```
pip install numpy pillow
python3 build.py                 # writes dist/(12)Azeroth.w3x and dist/preview.png
python3 build.py --seed 5        # same geography, different noise and forests
python3 -m unittest discover tests
```

| File | Purpose |
|---|---|
| `azeroth/geography.py` | Hand-placed continent outlines, zones, mountain ridges, lakes, rivers, roads, town and camp sites, and portals, in tile coordinates |
| `azeroth/biomes.py` | Per-biome ground tiles, trees, relief and critters |
| `azeroth/terrain.py` | Rasterises everything into heights, water, cliffs, textures, blight and the pathing map |
| `azeroth/objects.py` | Places start locations, waygates, critters, trees and doodads |
| `azeroth/jass.py` | Writes `war3map.j` in the same shape the World Editor generates for a map without triggers |
| `azeroth/formats.py` | Writers for `w3e`, `wpm`, `shd`, `doo`, units `doo`, `w3i`, `mmp`, `blp`, `w3r`, `w3c`, `wtg` and `wct` |
| `azeroth/mpq.py` | MPQ archive writer (zlib sectors, encrypted hash and block tables, HM3W header) |
| `tests/` | Independent MPQ and map-file readers, plus end-to-end checks |

## How it was checked

- The archive passes **StormLib**'s file verification, and every file extracts byte-for-byte.
- `war3map.j` passes the **pjass** syntax checker against both the 1.27 and the Reforged 1.32 `common.j` / `Blizzard.j`.
- Every unit, destructable and doodad ID exists in Blizzard's game data tables (`tests/game_ids.py`).
- Every terrain file parses back exactly. Every cliff tile uses a corner combination that has a cliff model. Every ramp follows the World Editor's corner layout, and its slope is walkable in the pathing map.
- The trigger files follow the World Editor's layout for a map with no triggers: the Initialization category, with nothing in it.
- A test confirms there are no gold mines, neutral hostile units, item drops or melee calls.
- Flood-fill checks confirm that every start location and waygate can be reached on foot or through waygates, and so can about 99% of all walkable land. Two camp names in Northrend sit just offshore; the coast next to them is reachable. Raised zones are entered by their ramps, and the massifs' cores are impassable.

**It has not been loaded in the actual game client yet.** If something looks off in game, please open an issue.

## Limits

- 12 players, not 24, so the map loads on every patch that supports 480 × 480 maps.
- The geography is hand-drawn from the world map, not traced from game data. Kalimdor and the Eastern Kingdoms are drawn about 20% shorter than their true proportions so a correctly shaped Northrend fits above them on a square map.
- Pandaria, the Broken Isles, Zandalar, Outland, the Dragon Isles and Khaz Algar are left out, which leaves room for a much larger Northrend.
