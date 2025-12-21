# Feature Ideas for Nexus Root MMORPG

Based on the current architecture (Python Backend, Phaser Web Client, Kotlin Android Client), here are three proposed features to enhance gameplay depth and user engagement.

## 1. NexusScript Marketplace (Player Economy)

**Concept:**
A user-driven economy where players can write, save, and sell automation scripts (written in NexusScript) to other players.

**Value:**
- **Depth:** Encourages players to learn the scripting language.
- **Economy:** Provides a sink for Credits and a way for skilled coders to earn in-game currency.
- **Community:** Fosters a "script kiddie" vs. "developer" dynamic.

**Implementation Details:**
- **Backend:**
  - New DB table `MarketplaceListings` (seller_id, script_code, price, name, description).
  - API endpoints: `POST /api/market/sell`, `GET /api/market/browse`, `POST /api/market/buy`.
  - Validation: Scripts must pass a safety check (AST analysis) to ensure they don't crash the evaluator.
- **Frontend (Web):**
  - New `MarketplaceScene` in Phaser.
  - Code editor integration for writing/previewing scripts.
- **Android:**
  - "App Store" style interface to browse and buy scripts.

## 2. Faction Mainframes (Cooperative Progression)

**Concept:**
Players can form "Factions" (Guilds). Each Faction owns a "Mainframe"—a shared Virtual Computer with massive scaling costs but powerful group-wide benefits.

**Value:**
- **Social:** incentivizes group play and resource pooling.
- **Retention:** Players return to contribute to the daily upkeep and upgrade goals.
- **Strategic Layer:** Factions compete for leaderboard dominance based on Mainframe power.

**Implementation Details:**
- **Backend:**
  - New `Faction` model linking multiple `Player` entities.
  - Shared `VirtualComputer` instance for the Faction.
  - Mechanics: Players "upload" credits or CPU cycles (passive mining) to the Mainframe.
- **Rewards:**
  - High-tier Mainframe unlocks exclusive commands (e.g., `mass_scan`, `ddos_protection`) for all members.
  - Passive credit generation bonus.

## 3. "NetWatch" Android Widget (Mobile Integration)

**Concept:**
A Home Screen widget for the Android client that displays real-time passive mining status and server alerts without opening the app.

**Value:**
- **Stickiness:** Keeps the game visible on the user's personal device.
- **Utility:** "Passive Mining" is a core mechanic; a widget makes monitoring it frictionless.
- **Immersion:** Mimics a real-world server monitor tool.

**Implementation Details:**
- **Android:**
  - `AppWidgetProvider` implementation.
  - Background `WorkManager` job to poll `/api/player/{name}/state` every 15-30 minutes.
  - **Visuals:** Matrix-themed progress bar for mining completion.
  - **Interaction:** Tap to collect credits (launches app deep link).

## 4. "Zero-Day" Research Lab (Crafting Mechanic)

**Concept:**
A resource-sink mechanic where players combine "Knowledge Fragments" (found in missions/files) to research "Zero-Day Exploits". These are single-use or limited-use consumables that bypass high-level security barriers.

**Value:**
- **Resource Sink:** Gives purpose to hoarded Knowledge Fragments.
- **Strategic Depth:** Players must choose between selling fragments or crafting powerful tools.
- **Progression:** Allows lower-level players to tackle higher-level targets occasionally.

**Implementation Details:**
- **Backend:**
  - New `CraftingRecipe` model.
  - `Player.inventory` tracks crafted exploits.
  - Exploit logic hooked into `CommandService` (e.g., `exploit <target_ip> --use-zeroday`).

## 5. Procedural Contract System (Infinite Content)

**Concept:**
An automated mission generator that creates "Contracts" based on the player's level. Instead of a static story, players take on procedurally generated jobs.

**Value:**
- **Replayability:** Infinite content stream.
- **Scaling:** Missions automatically adjust to player power.

**Implementation Details:**
- **Backend:**
  - `ContractGenerator` service.
  - Templates: "Delete logs on [RandomServer]", "Download file [RandomHash]", "DDoS [RandomIP]".
  - Dynamic rewards based on difficulty calculations.
- **UI:**
  - "Dark Web" job board interface in both Web and Android clients.

## 6. Real-Time Terminal PvP (Combat)

**Concept:**
A synchronous 1v1 duel mode where players connect to a "Combat Server". They must type commands to breach the opponent's active defenses (Firewall HP) while patching their own.

**Value:**
- **Skill-Based:** Typist speed and command knowledge matter more than stats.
- **Excitement:** High-stakes, fast-paced gameplay.

**Implementation Details:**
- **Backend:**
  - WebSocket "Combat Room" handling.
  - Real-time state syncing (HP, Shield, Status Effects).
- **Frontend:**
  - Split-screen terminal view (Attacker/Defender logs).
  - Visual effects for successful hacks or blocks.
