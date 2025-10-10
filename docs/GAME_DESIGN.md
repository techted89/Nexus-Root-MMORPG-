# Code Nexus - Game Design Document

## 1. Game Overview

**Code Nexus** is an MMORPG (Massively Multiplayer Online Role-Playing Game) focused on the competitive and cooperative development of software and hardware hacking modules.

### Core Loop

Players start with a minimal, low-power Virtual Computer (VC) and a basic shell interface. They complete missions to earn Credits (C), which are spent on upgrading VC hardware (CPU, RAM, Network Bandwidth) and purchasing/writing new software/scripting modules. Progress unlocks more complex missions and deeper access to the game world's virtual network.

### Learning Focus

The core mechanism of the game is the custom scripting interface. Players must learn real programming concepts (object orientation, data types, control flow) to progress.

## 2. The NexusShell Language & Tool Simulation

The core of the game is the NexusShell interface and its object-oriented custom language, NexusScript. This system is designed to simulate the core function of real-world tools without requiring players to master the full syntax complexity of languages like C++ or Python.

### Core NexusScript Concepts

| Real Concept | NexusScript Implementation | In-Game Command / Function | Learning Focus |
| :--- | :--- | :--- | :--- |
| Data Types | String, Integer, Float, Boolean, IP_Object, Port_Object | `set target_ip = new IP_Object("10.0.0.1")` | Variables and Object Instantiation |
| Control Flow | Loops and Conditionals | `if (target_ip.is_open_port(80)) { run web_scan }` | Logic and Automation |
| Functions/Modules | Custom scripts created by the player | `func my_scan_module(IP) { ... }` | Modular Programming/Code Reusability |
| Exploit Framework | The Exploit_Object Class | `exploit_v1.inject(target_service)` | Object Inheritance and Parameters |

### Simulated Hacking Tools

| Real-World Tool Category | NexusShell Function/Object | Real-World Analogues | Game Functionality |
| :--- | :--- | :--- | :--- |
| Reconnaissance | `scan` (for ports/OS), `ping` | Nmap, Zenmap, OSINT tools | Finds open ports, identifies services, determines target OS. |
| Traffic Sniffing | `sniff_traffic` | Wireshark, Tcpdump | Captures virtual network packets. |
| Exploitation | `exploit` (class), `inject` | Metasploit Framework | Loads and executes an Exploit Module against a vulnerable target. |
| Web App Testing | `web_request`, `fuzz` | Burp Suite, OWASP ZAP | Intercepts, modifies, and replays web traffic. |
| Password Cracking | `hashcrack` | John the Ripper, Hashcat | Takes a captured hash and attempts to crack it. |

## 3. Scalable Mission Design and Progression

Missions are structured around the phases of a real-world penetration test: Reconnaissance, Scanning/Vulnerability Analysis, Exploitation, and Post-Exploitation.

### The New Player Tutorial (The LAN Confinement)

*   **Phase 1: Minimal Resource (The Terminal)**
    *   **Goal:** Access a file on the local machine.
    *   **Action:** Player is limited to `ls` and `cat` commands.
    *   **Reward:** Unlocks the `IP_Object` and the `ping` command.
*   **Phase 2: Network Discovery (The LAN)**
    *   **Goal:** Pwn/control 3 simple devices.
    *   **Action:** Player must use `ping` and `scan`.
    *   **Reward:** Unlocks the Module Editor, `for` loop, and CPU upgrades.
*   **Phase 3: The Gateway (The Firewall)**
    *   **Goal:** Bypass a simple Network Firewall Object.
    *   **Action:** Player must write their first NexusScript module.
    *   **Completion:** The player is now Level 1.

## 4. Freemium Model: Learn Free, Hack Efficiently

The core philosophy is: All knowledge and core gameplay mechanics are free. Time and quality-of-life improvements are paid.

*   **Free-to-Play Tier (The Freelancer):** The complete game, but with time sinks and efficiency limitations.
*   **VIP Subscription Tier (The Architect):** Removes artificial time and efficiency barriers.
*   **In-App Purchases:** Cosmetic items and minor, consumable boosts.

## 5. Expanded NexusScript Coding Interface Features

*   **In-Game Module Editor:** With syntax highlighting, code snippets, and error feedback.
*   **Dynamic Debugging and Logging:** With trace mode, resource monitoring, and conditional breakpoints.
*   **Multiplayer Collaboration Features:** With module sharing and a community marketplace.
*   **Advanced Hardware Interaction:** With thread control and hardware overclocking.

## 6. Command and Knowledge Acquisition System

A "hack-to-learn" system where players must discover and validate commands before they can be used.

*   **"Locked" State:** Commands are initially unrecognized.
*   **Command Discovery Mechanisms:** Mission rewards, filesystem harvesting, and PvP module analysis.
*   **The Knowledge-Map (K-Map):** A central repository for learned commands and concepts.
*   **Advanced Knowledge Acquisition:** Players must synthesize knowledge to create new commands.

## 7. Fragmented Knowledge and Boolean Logic Progression

A multi-step learn-to-unlock process where players must collect, synthesize, and validate knowledge fragments to unlock advanced commands.

*   **Fragment Collection:** Find unique knowledge fragments.
*   **Synthesis:** Compile the fragments into a single Knowledge Module.
*   **Validation:** Execute a mission that requires the concept.
