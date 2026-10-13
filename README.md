# Azeroth for Warcraft III

**[`dist/(12)Azeroth.w3x`](dist/(12)Azeroth.w3x)** is a 12-player melee map of the whole world of Azeroth. It is built at **480 × 480 tiles**, the largest size Warcraft III supports. The playable area is 468 × 468 tiles, about 60,000 × 60,000 world units.

![Overview of the map](dist/preview.png)

*Overview render: capitals in red, gold mines in yellow, shops and waygates in white, creep camps as red dots, portal links in purple.*

## What's on the map

| Landmass | Zones |
|---|---|
| **Kalimdor** | Teldrassil, Darkshore, Moonglade, Felwood, Winterspring, Mount Hyjal, Azshara, Ashenvale, Stonetalon, the Barrens, Durotar, Desolace, Mulgore, Feralas, Thousand Needles, Dustwallow Marsh, Un'Goro Crater, Tanaris, Silithus, Uldum, plus Azuremyst, Bloodmyst, the Echo Isles and Theramore |
| **Eastern Kingdoms** | Quel'Danas, Eversong, Ghostlands, Tirisfal, both Plaguelands, Silverpine, Gilneas, Hillsbrad, Alterac, the Hinterlands, Arathi, Wetlands, Twilight Highlands, Dun Morogh, Loch Modan, Badlands, Searing Gorge, Burning Steppes, Redridge, Elwynn, Westfall, Duskwood, Deadwind Pass, Swamp of Sorrows, Blasted Lands, Stranglethorn, Tol Barad |
| **Northrend** | Borean Tundra, Sholazar Basin, Icecrown, Wintergrasp, Dragonblight, Crystalsong Forest, the Storm Peaks, Zul'Drak, Grizzly Hills, Howling Fjord |
| **Pandaria** | Jade Forest, Valley of the Four Winds, Krasarang Wilds, Kun-Lai Summit, Townlong Steppes, Dread Wastes, Vale of Eternal Blossoms, Timeless Isle, Isle of Thunder |
| **The Great Sea** | The Maelstrom, the Broken Isles (Azsuna, Val'sharah, Highmountain, Stormheim, Suramar, Broken Shore), Kul Tiras (Drustvar, Stormsong Valley, Tiragarde Sound), Zandalar (Zuldazar, Nazmir, Vol'dun), Kezan and the Lost Isles |

There are 89 zones in all. Each zone has its own ground textures, tree type, relief and creeps: jungle in Stranglethorn, blight in the Plaguelands, lava cracks in the Burning Steppes, cliff mesas in Thousand Needles and at Thunder Bluff, and the crater rim around Un'Goro. A few landmark doodads are placed too: the World Trees at Teldrassil and Hyjal, the Sunwell, the Frozen Throne, the ruins of Dalaran, the Dark Portal, and volcanoes at Blackrock and Un'Goro.

**Start locations** (one per player slot): Stormwind, Orgrimmar, Undercity, Darnassus, Ironforge, Thunder Bluff, Icecrown Citadel, Silvermoon City, the Shrine of Seven Stars, Suramar City, Boralus and Dazar'alor. Each one gets a 15,000-gold mine and a grove of trees for lumber.

**Getting between continents.** Nine pairs of mage portals (waygates) link the landmasses. They sit about 17 tiles outside each capital, so no portal opens directly into a base:

- Stormwind ↔ Darnassus
- Orgrimmar ↔ Undercity
- Ironforge ↔ Dalaran (Northrend)
- Thunder Bluff ↔ Silvermoon
- Stormwind Harbor ↔ Boralus
- Orgrimmar ↔ Dazar'alor
- Ratchet ↔ Pandaria
- Undercity ↔ Icecrown
- Silvermoon ↔ Suramar

Goblin shipyards sit at the ports (Booty Bay, Ratchet, Theramore, Menethil, Auberdine and others), and goblin laboratories sell zeppelins. Teldrassil connects to Darkshore through a shallow strait that ground units can wade across.

**Neutral content.** About 105 gold mines, roughly 300 creep camps (each camp leader drops an item), 58 shops (taverns, merchants, mercenary camps, marketplaces, dragon roosts, fountains), critters, and about 22,000 trees.

## Playing it

You need **patch 1.29 or later** (Reforged included), because older patches cap maps at 256 × 256. Copy the `.w3x` into your maps folder, for example `Documents/Warcraft III/Maps/`. It is flagged as a melee map, so it appears in the normal custom/melee game list with free race choice, the standard melee setup and computer players.

The map also includes the World Editor files: preplaced units, regions, and the Melee Initialization trigger. You can open it in the World Editor and keep building on it.

## Building it yourself

The map is generated entirely from code. Nothing is copied from Blizzard files.

```
pip install numpy pillow
python3 build.py                 # writes dist/(12)Azeroth.w3x and dist/preview.png
python3 build.py --seed 5        # same geography, different noise, forests and creep rolls
python3 -m unittest discover tests
```

| File | Purpose |
|---|---|
| `azeroth/geography.py` | Hand-placed continent outlines, zones, mountain ridges, lakes, rivers, roads, towns, camps and portals, in tile coordinates |
| `azeroth/biomes.py` | Per-biome ground tiles, trees, relief and creep rosters |
| `azeroth/terrain.py` | Rasterises everything into heights, water, cliffs, textures, blight and the pathing map |
| `azeroth/objects.py` | Places start locations, mines, creep camps, shops, waygates, critters and trees |
| `azeroth/jass.py` | Writes `war3map.j` in the same shape the World Editor generates for melee maps |
| `azeroth/formats.py` | Writers for `w3e`, `wpm`, `shd`, `doo`, units `doo`, `w3i`, `mmp`, `blp`, `w3r`, `w3c`, `wtg` and `wct` |
| `azeroth/mpq.py` | MPQ archive writer (zlib sectors, encrypted hash and block tables, HM3W header) |
| `tests/` | Independent MPQ and map-file readers, plus end-to-end checks |

## How it was checked

- The archive passes **StormLib**'s file verification, and every file extracts byte-for-byte.
- `war3map.j` passes the **pjass** syntax checker against both the 1.27 and the Reforged 1.32 `common.j` / `Blizzard.j`.
- Every unit, destructable and doodad ID exists in Blizzard's game data tables (`tests/game_ids.py`).
- Every terrain file parses back exactly. Every cliff tile uses a corner combination that has a cliff model.
- The trigger files are byte-identical to the World Editor's own output for the melee trigger.
- Flood-fill checks confirm that each capital can walk to its main mine. Each continent's mines, shops and portal exits are mutually reachable on foot. The small islands are reached by portal, boat or zeppelin.

**It has not been loaded in the actual game client yet.** If something looks off in game, please open an issue.

## Limits

- 12 players, not 24, so the map loads on every patch that supports 480 × 480 maps.
- The geography is hand-drawn from the world map, not traced from game data. Distances are squeezed to fit a square map.
- Outland, the Dragon Isles and Khaz Algar are not included.
