<!-- RPG:START -->

<div align="center">

**⚔️ TERMINAL DUNGEON CRAWLER ⚔️**

*A community-driven RPG adventure — 2 heroes, 6 turns played*

</div>

```
gxcsoccer@github ~ $ ./dungeon_crawler

  HP [████████░░] 40/50   Lv.1
  ATK 8  DEF 4  Gold 0  XP 0/20

  📍 The Great Hall

     | ||  || |
     | ||  || |
     |  *~~*  |
     | ||  || |
     |_||__||_|

  A vast stone hall with crumbling pillars and ancient runes on the floor.

  ⚔️ Skeleton Knight appears!
  Enemy HP [████████░░] 27/35

  Exits: NORTH | WEST | EAST | SOUTH

  📜 Adventure Log:
  > ⚡ Skeleton Knight appears!
  > @gxcsoccer Attacked Skeleton Knight for 3 dmg!
  > ⚡ Skeleton Knight strikes back for 5 dmg!
  > @gxcsoccer Attacked Skeleton Knight for 5 dmg!
  > ⚡ Skeleton Knight strikes back for 5 dmg!
```

| | | |
|:---:|:---:|:---:|
| [⚔️ Attack](https://github.com/gxcsoccer/gxcsoccer/issues/new?title=RPG%3AATTACK&body=I%20chose%20%2A%2AATTACK%2A%2A%21%20Let%20the%20adventure%20continue%21) | [🛡️ Defend](https://github.com/gxcsoccer/gxcsoccer/issues/new?title=RPG%3ADEFEND&body=I%20chose%20%2A%2ADEFEND%2A%2A%21%20Let%20the%20adventure%20continue%21) | [🏃 Run](https://github.com/gxcsoccer/gxcsoccer/issues/new?title=RPG%3ARUN&body=I%20chose%20%2A%2ARUN%2A%2A%21%20Let%20the%20adventure%20continue%21) |

---

<details>
<summary><b>📜 Adventure Log</b></summary>

### 🏆 Heroes

<table>
  <thead>
    <tr><th>Hero</th><th>Moves</th></tr>
  </thead>
  <tbody>
    <tr><td><img src="https://github.com/gxcsoccer.png?size=16" alt="" width="16"> **[gxcsoccer](https://github.com/gxcsoccer)**</td><td align='center'>5</td></tr>
    <tr><td><img src="https://github.com/GaryXJT.png?size=16" alt="" width="16"> **[GaryXJT](https://github.com/GaryXJT)**</td><td align='center'>1</td></tr>
  </tbody>
</table>

### 🗺️ Move History

| Turn | Time | Hero | Event | Issue |
| :---: | :---: | :--- | :--- | :---: |
| **6** | 2026-03-28 06:24 UTC | <img src="https://github.com/gxcsoccer.png?size=16" alt="" width="16"> **[gxcsoccer](https://github.com/gxcsoccer)** | ⚔️ Attacked Skeleton Knight for 5 dmg! | [#7](https://github.com/gxcsoccer/gxcsoccer/issues/7) |
| **5** | 2026-03-28 06:23 UTC | <img src="https://github.com/gxcsoccer.png?size=16" alt="" width="16"> **[gxcsoccer](https://github.com/gxcsoccer)** | ⚔️ Attacked Skeleton Knight for 3 dmg! | [#6](https://github.com/gxcsoccer/gxcsoccer/issues/6) |
| **4** | 2026-03-26 04:08 UTC | <img src="https://github.com/GaryXJT.png?size=16" alt="" width="16"> **[GaryXJT](https://github.com/GaryXJT)** | 🐉 Skeleton Knight appears! | [#5](https://github.com/gxcsoccer/gxcsoccer/issues/5) |
| **4** | 2026-03-26 04:08 UTC | <img src="https://github.com/GaryXJT.png?size=16" alt="" width="16"> **[GaryXJT](https://github.com/GaryXJT)** | ⬇️ Moved to The Great Hall | [#5](https://github.com/gxcsoccer/gxcsoccer/issues/5) |
| **3** | 2026-03-15 07:31 UTC | <img src="https://github.com/gxcsoccer.png?size=16" alt="" width="16"> **[gxcsoccer](https://github.com/gxcsoccer)** | 💚 Rested and healed 20 HP |  |
| **2** | 2026-03-15 07:31 UTC | <img src="https://github.com/gxcsoccer.png?size=16" alt="" width="16"> **[gxcsoccer](https://github.com/gxcsoccer)** | ➡️ Moved to Dusty Library |  |
| **1** | 2026-03-15 07:30 UTC | <img src="https://github.com/gxcsoccer.png?size=16" alt="" width="16"> **[gxcsoccer](https://github.com/gxcsoccer)** | ⚡ Poison darts shoot from the walls! |  |
| **1** | 2026-03-15 07:30 UTC | <img src="https://github.com/gxcsoccer.png?size=16" alt="" width="16"> **[gxcsoccer](https://github.com/gxcsoccer)** | ⬇️ Moved to Dark Corridor |  |

</details>

<details>
<summary><b>🎮 How to Play</b></summary>

### Rules

This is a **community-driven dungeon crawler RPG**! Everyone controls the same hero together.

**How it works:**
1. Click an action button above (e.g. **South**, **Attack**)
2. This creates a GitHub Issue automatically
3. A GitHub Action processes your move and updates this README
4. The issue is closed with a confirmation comment

**Game mechanics:**
- ⬆️⬇️⬅️➡️ **Move** through the dungeon rooms
- ⚔️ **Attack** enemies to deal damage (ATK - enemy DEF + random 0~3)
- 🛡️ **Defend** to take half damage and counter-attack
- 🏃 **Run** from combat (60% success rate)
- 💚 **Rest** at peaceful locations to heal HP
- 🛒 **Shop** to buy potions, weapons, and armor

**Leveling up:**
- Defeat enemies to earn XP and Gold
- Level up at XP thresholds: 20, 50, 100, 180, 300
- Each level grants +5 HP, +2 ATK, +1 DEF and full heal

**Death & Respawn:**
- If HP reaches 0, the hero falls
- Click any button to respawn at the entrance with base stats
- Your contribution to the hero list is preserved!

**Dungeon Map (📍 10 rooms):**
```
         [Entrance]
             |
         [Hallway]        <- trap!
        /         \
   [Armory]    [Library]   <- treasure / rest
        \         /
       [Great Hall]        <- Skeleton Knight
      /     |      \
  [Crypt] [Throne] [Garden]
    |    Dragon!      |
  [Vault]         [Fountain] <- shop
```

</details>

<!-- RPG:END -->

<div align="center">

<img alt="pacman" src="https://raw.githubusercontent.com/gxcsoccer/gxcsoccer/output/pacman-contribution-graph.svg" width="100%" />

</div>

<!-- 🏆 Achievement Unlocked: YOLO -->
