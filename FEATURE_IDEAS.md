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
