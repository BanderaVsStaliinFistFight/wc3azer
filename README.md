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

- **Coasts.** Where high ground meets the sea, the shore is a cliff wall rising out of a pale shelf of shallows. Where the land behind is low, it runs down to a beach, about 30% of the shoreline in all. Beaches are also kept wherever units must reach the water: along the wading straits and river mouths, at every shipyard and round the small islands.
- **Lakes.** 64 in all:
  - 20 named lakes, among them Lordamere, Darrowmere, Loch Modan, Lake Everstill, Lake Nazferiti, Brightwater Lake, Lake Elrendar and the Lushwater Oasis;
  - a spring pond at the head of every river no lake feeds;
  - 38 natural lakes scattered across the continents' interiors, clear of roads, settlements and the great ranges, with only the odd oasis in dry country.

  Each lies in a hollow with gentle shores, ringed with reeds and dotted with lily pads.
- **Rivers and valleys.** Rivers wind from side to side, widen from a narrow stream at their spring pond to a broad mouth, and run through valleys. Water running off the land carves a branching network of valleys into everything: shallow swales across the plains, and deep gullies in the mountains. Mountain ranges bend instead of running ruler-straight, and broad swells keep the plains from lying flat.
- **Hills and elevation.** The land rises from its shores towards the heart of each continent, about 90 units higher inland, and rolls with hills: big swells with smaller knolls on top. Most zones span 150 to 300 units from their valleys to their hilltops, and the median height of the land is about 185, against about 70 before. Only true mountain heights are compressed; the hills keep their full height.
- **Raised and sunken zones.** Highland zones stand one cliff level above their neighbours: Winterspring, Mount Hyjal, Stonetalon, Mulgore, Alterac, the Hinterlands, Arathi, the Twilight Highlands, Dun Morogh, Searing Gorge, Icecrown, the Storm Peaks, Zul'Drak, the Grizzly Hills and Drustvar. Un'Goro Crater sinks one level below. Ramps, built the way the World Editor builds them, climb these edges wherever a road crosses and every couple of dozen tiles along them.
- **Massifs.** Sixteen great ranges tower over everything else, up to about 1,800 units high. Each is a chain of steep summits strung along its crest, with saddles between them, so a range ends in a row of peaks rather than a level top. Cliff bands (up to three) ring their lower flanks, and above those the slopes climb as open rock and snow to the summits, crowned with great rock spires or glaciers. No army can climb their cores. They are Stonetalon, the summit of Hyjal, Winterspring, Darkshore's range, the Feralas wall, the cliffs above Thousand Needles, the walls of Un'Goro, the Alterac Mountains, the Khaz Mountains, Blackrock Mountain, Redridge, the Thalassian highlands, the Blasted Lands wall, the Storm Peaks, the Icecrown glacier and the walls of Sholazar. Each is crossed only at its roads' passes: Dun Algaz through the Khaz Mountains, the Great Lift into Thousand Needles, two passes into Un'Goro, and two roads into Sholazar.
- **Cliffs.** The game draws the ground beside every cliff with the cliff type's own tile, whatever is painted there. So each cliff takes the type that suits the ground around it, rather than one type per zone:
  - snow cliffs (grey rock under snow, from Lordaeron Winter) in the snow and on the bare rock of cold zones;
  - grass cliffs in meadows;
  - dirt cliffs on rock, dirt and sand elsewhere.

  The cliff's ground also spills a ragged tile or so beyond each cliff, like scree or drifted snow, so cliffs blend into the land instead of being outlined by a thin stripe. Blight lies only in the Plaguelands and the crypts, and keeps clear of cliffs and mountains. The snowy zones (Icecrown, Winterspring, Dun Morogh, Alterac, the Storm Peaks and the rest of the cold country) are snow with grey, snow-dusted Lordaeron Winter rock on their slopes, rather than a patchwork of blight, ice and red-brown summer rock. No ledge, notch, pit or spike is a single corner wide, and no two cliff levels meet only at a diagonal, so the game draws no stray shards of cliff.
- **Mountain ranges.** The lesser ranges rise out of foothills to their own chains of summits, broken by saddles and spurs, and stepped by ragged cliff ledges. No hill or mountain ends in a flat table: the top level of each keeps rising from its rim to a rounded crown or a peak. The high ground turns to bare rock and scree, with snow on the summits. Roads keep their passes open, and settlements stand in levelled clearings away from the slopes.
- **Getting about on foot.**
  - Outside the massifs, cliff ledges and plateaus get ramps so they are part of the land, not walled-off islands of it. Any patch of ground still sealed off gets a ramp to its neighbour.
  - Every camp and town lies on a track to the nearest road.
  - Wading straits reach Azuremyst, Bloodmyst, Tol Barad and Alcaz Island.
  - About 99% of the walkable land can be reached from the start locations; what is left is small ledges high in the mountains.
- **Forests.** Woods cover a share of each zone set by its climate. They grow thicker along rivers and lakes, climb the hillsides up to a treeline, break up into clumps and clearings, and fray into scattered trees at their edges. Inside, the trees stand with gaps between them rather than as a solid wall. Each climate grows a mix of 3–6 species (23 in all), and each species gathers in its own stands, so a wood shifts from one kind of tree to another as you cross it. Elwynn mixes summer oaks with autumn and winter trees and a few round-crowned ones; Duskwood is mostly gnarled ruin trees, with toadstools in the gloom; Ashenvale has its violet trees under wide canopy giants; the jungles grow palms and canopy trees, with the odd giant mushroom; the Barrens have acacias; the north has pines, snowy trees and frosted canopies. The ground under the woods is dark forest floor.
- **Ground detail.** The ground follows the lie of the land: each zone's lusher ground gathers on wet valley floors and along the water, and its dirt and rock on slopes and high, dry ground. Zone borders fray into one another instead of meeting on a line. Roads wander a little, as roads do. Flowers, shrubs and mushrooms dot open ground, reeds and cattails line the water, lily pads float on the lakes, and boulders lie on steep slopes and below cliffs.
- **Roadsides.** Roads are lined with the land's own stones and wild flowers. Every few tiles there is a stone, sometimes with a pebble, at the edge of the verge on one side or the other. Stones sit closer together in rough country and where it is too cold or dry for flowers. Patches of flowers, shrubs and mushrooms come and go along the way: flowers in Elwynn and Hillsbrad, shrubs in the Barrens, toadstools in Duskwood and Felwood.
- **Decorations.** About 100 kinds of doodad are spread thinly across the whole map, mostly natural ones:
  - Open ground in each biome is dotted with its own boulders, bushes, stumps, cacti, thorns and ice, and now and then a man-made piece: hay and wheat on the farms, a grave in the Plaguelands, bones or a totem in the Barrens, a broken column in Ashenvale, a fallen pillar in the jungle, a tombstone in Northrend.
  - Every named camp site has one to three ruins in its region's style.
  - Every town has a little village clutter round its square: hay, lantern posts, weapon racks, carts, braziers and the odd well, with fire pits in the cold and totems in the Barrens.
  - Signposts stand at the forks in the roads and shells lie on the beaches.
  - Birds circle over woods and shores, bats over the dark places, and flies over the swamps.

  Solid pieces are written into the pathing map, and none of them is allowed to cut off a path.
- **Instances.** Each dungeon has a vestibule round its waygate, a pillared hall, and a raised dais at the far end, reached up a ramp. Floors are themed: lava cracks in Molten Core and Onyxia's Lair, sand and brick in the desert temples, brick and poison in the crypts, ice in the Northrend raids, and moss in the caverns.
- **Paved capitals:** a brick square with streets leading out along the roads.

There are 93 zones in all, counting the instances. Each zone has its own ground textures, mix of trees, relief and wildlife: jungle in Stranglethorn, blight in the Plaguelands, lava cracks in the Burning Steppes, cliff mesas in Thousand Needles and at Thunder Bluff, the crater rim around Un'Goro, and the Greymane Wall, a cliff rampart whose gate is the only way into Gilneas on foot. A few landmark doodads are placed too: the World Trees at Teldrassil and Hyjal, the Sunwell, the ruins of Dalaran, the Dark Portal, and volcanoes at Blackrock and Un'Goro.

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
- About 17,600 trees of 23 species.
- The cities: about 340 stone wall segments and 200 spiked barricades (destructables), and about 385 buildings, 155 fence runs, and gate posts, monuments and lights.
- About 6,400 decorations, nearly all of them natural: flowers, shrubs and mushrooms (most of them along the roads), about 2,200 rocks and boulders, bushes, stumps and rock spires. Only about 650 are man-made props and ruins.
- The landmark doodads.
- The waygates.
- Wildlife critters in every zone.
- The 12 start locations.

There are no gold mines, creeps, shops or item drops. The ~60 towns and ~100 camp sites from the geography (Goldshire, Booty Bay, Crossroads, Gadgetzan, Dire Maul, Stratholme and the rest) are levelled clearings joined to the road network; the towns and capitals are built up (see **Cities**), and the camp sites keep a few ruins.

**Cities.** Every capital and town is built up from the game's own walls and buildings (`azeroth/cities.py`):
- **Capitals** stand inside a stone curtain wall about 27 tiles across, laid segment by segment the way the World Editor lays walls, with posts at the corners and at every gateway. A gateway opens wherever a road passes through the wall, and every side has at least one. Inside, houses line the streets and fill the ring round the open square, where the start location stays clear for building. Each capital has its people's look: Cityscape houses, fountains and statues for Stormwind, Ironforge, Dalaran, Boralus and Valgarde; elven halls for Silvermoon; ruined houses, a ruined cathedral and Lordaeron's stone walls, left broken, for Undercity; Icecrown walls, pillars and crypts for Icecrown Citadel; rough stone walls, totems, fire pits and skull pikes for Orgrimmar and Warsong Hold; a spiked palisade for Thunder Bluff; and elven halls with Sentinel statues, but no wall, for Darnassus.
- **Towns**: the ports, markets and goblin towns (Booty Bay, Gadgetzan, Southshore, Menethil Harbor and the like) get a smaller stone wall, and the rest a wooden fence, broken by the roads. Horde outposts (the Crossroads, Grom'gol, Hammerfall, Kargath, Razor Hill, Camp Taurajo, Agmar's Hammer and the like) are camps behind a spiked palisade instead, wherever they stand. Inside are cottages, an inn or a barn, a well or fire pit and lanterns; granaries and windmills on the farms, elven halls in Ashenvale and Teldrassil, and totems and fire pits in the Horde camps and dry country. A town right beside a capital or another walled town (Brill, the Booty Bay and Gadgetzan markets) shares its neighbour's wall.
- Walls and palisades are destructables, so the game gives them their pathing; buildings, posts and fences are written into the pathing map. A check takes away any wall or building that would shut in a start location, a town or any other stretch of land.

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
| `azeroth/cities.py` | Builds the capitals' and towns' walls, gateways, houses, monuments and fences |
| `azeroth/jass.py` | Writes `war3map.j` in the same shape the World Editor generates for a map without triggers |
| `azeroth/formats.py` | Writers for `w3e`, `wpm`, `shd`, `doo`, units `doo`, `w3i`, `mmp`, `blp`, `w3r`, `w3c`, `wtg` and `wct` |
| `azeroth/mpq.py` | MPQ archive writer (zlib sectors, encrypted hash and block tables, HM3W header) |
| `tests/` | Independent MPQ and map-file readers, plus end-to-end checks |

## How it was checked

- The archive passes **StormLib**'s file verification, and every file extracts byte-for-byte.
- `war3map.j` passes the **pjass** syntax checker against both the 1.27 and the Reforged 1.32 `common.j` / `Blizzard.j`.
- Every unit, destructable and doodad ID exists in Blizzard's game data tables (`tests/game_ids.py`).
- Every terrain file parses back exactly. Every cliff tile uses a corner combination that has a cliff model. Every ramp follows the World Editor's corner layout, and its slope is walkable in the pathing map. The ground painted beside each cliff is exactly what the game draws there, and grass cliffs stand in grassy ground.
- The trigger files follow the World Editor's layout for a map with no triggers: the Initialization category, with nothing in it.
- A test confirms there are no gold mines, neutral hostile units, item drops or melee calls.
- Flood-fill checks confirm that every start location and waygate can be reached on foot or through waygates, and so can about 99% of all walkable land. Two camp names in Northrend sit just offshore; the coast next to them is reachable. Raised zones are entered by their ramps, and the massifs' cores are impassable. With every city wall and palisade in place, no start location is shut in.

**It has not been loaded in the actual game client yet.** If something looks off in game, please open an issue.

## Limits

- 12 players, not 24, so the map loads on every patch that supports 480 × 480 maps.
- The geography is hand-drawn from the world map, not traced from game data. Kalimdor and the Eastern Kingdoms are drawn about 20% shorter than their true proportions so a correctly shaped Northrend fits above them on a square map.
- The pathing footprints of the Cityscape houses, inns, barns and the ruined cathedral are estimates (3 x 3 or 4 x 4 tiles), as their pathing textures aren't in the game data this was built from. Re-saving the map in the World Editor recomputes them from the real textures.
- Pandaria, the Broken Isles, Zandalar, Outland, the Dragon Isles and Khaz Algar are left out, which leaves room for a much larger Northrend.
