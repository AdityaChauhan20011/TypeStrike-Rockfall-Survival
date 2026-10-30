# TypeStrike: Rockfall Survival — Project Synopsis & Case Study

**Project Title**: TypeStrike: Rockfall Survival  
**Domain**: Interactive Multimedia, Human-Computer Interaction (HCI), Gamified EdTech  
**Technology Stack**: Python 3.10+, Pygame / Pygame-CE, NumPy, SQLite3  
**Target Platform**: Desktop (Cross-platform: Windows, macOS, Linux)  

---

## 1. Executive Summary & Abstract

Traditional typing tutors often suffer from repetitive, text-entry paradigms that lead to rapid user fatigue and declining practice engagement. **TypeStrike: Rockfall Survival** re-engineers psychomotor skill acquisition by fusing an arcade survival combat game with a real-time typographic processing engine. 

In *TypeStrike*, the user controls a defensive cyber-turret facing incoming kinetic meteors. Each hazard is procedurally labeled with vocabulary words categorized by phonetic and mechanical difficulty. By typing correctly, the player aims and discharges plasma projectiles; typing mistakes trigger auditory-visual alerts and break combo multipliers. The system features an autonomous procedural audio synthesizer using NumPy, a multi-layered parallax rendering pipeline, sub-millisecond lexical targeting, and a relational telemetry tracker that calculates standardized Gross/Net Words Per Minute (WPM), keystroke accuracy, and error heat patterns.

---

## 2. Key Architecture & Features

### 2.1 Lexical Parsing & Target Acquisition
- **First-Character Dynamic Lock**: Typing a character queries all on-screen rocks, locking onto the lowest/closest hazard beginning with that character.
- **Target Retention**: Once locked, subsequent keystrokes are routed exclusively to that target.
- **Visual Feedback**: Real-time letter coloring differentiates typed prefix (green/cyan) from untyped suffix (crisp white), with typo alerts (neon crimson).

### 2.2 Procedural Audio Synthesis (Zero External Audio Assets)
- Built-in sound generator using NumPy mathematical waveform functions.
- Generates plasma laser chirps, explosion white noise decay, and harmonic alert sounds dynamically in memory.

### 2.3 Comprehensive Analytics & Persistence
- Standard 5-character word convention for Gross and Net WPM.
- Real-time keystroke accuracy and streak multiplier calculation.
- Automated performance grading ($S+, S, A, B, C, D$).
- Embedded SQLite relational database tracking session histories, high scores, and user preferences.

---

## 3. System Architecture

```
                       +-----------------------------+
                       |    main.py (FSM Runner)     |
                       +--------------+--------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
+--------v--------+          +--------v--------+          +--------v--------+
|   MenuScreens   |          |    GameScene    |          |  ResultsScreen  |
+-----------------+          +--------+--------+          +-----------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
+--------v--------+          +--------v--------+          +--------v--------+
|  TypingEngine   |          |  EntityManager  |          |  StatsTracker   |
| (Lexical Lock)  |          | (Rocks/Projectiles) |      |   (WPM / Acc)   |
+--------+--------+          +--------+--------+          +--------+--------+
         |                            |                            |
+--------v--------+          +--------v--------+          +--------v--------+
|    WordBank     |          |  AudioManager   |          |    DBManager    |
| (Assets/Words)  |          |   (NumPy Synth) |          | (SQLite Storage)|
+-----------------+          +-----------------+          +-----------------+
```

---

## 4. Hazard Classification

| Rock Type | Behavior & Threat | Typographic Challenge |
| :--- | :--- | :--- |
| **Normal** | Standard descent speed | Baseline vocabulary |
| **Fast** | High descent velocity | Quick reactive reflex (short words) |
| **Armored** | Multiple hits / shield layer | High-frequency or longer words |
| **Explosive** | Radial explosion upon destruction | Strategic target clearing |
| **Power-up** | Drops Chrono-Slow, Shield, or EMP | High-value bonus acquisition |
| **Boss** | Massive durability & slow descent | Complex multi-word technical phrases |

---

## 5. Performance Metrics

$$\text{Gross WPM} = \frac{(\text{Correct Keystrokes} / 5)}{T_{\text{active (min)}}}$$

$$\text{Net WPM} = \max\left(0, \frac{((\text{Correct Keystrokes} - 0.5 \times \text{Errors}) / 5)}{T_{\text{active (min)}}}\right)$$

$$\text{Accuracy (\%)} = \left(\frac{\text{Correct Keystrokes}}{\text{Total Keystrokes}}\right) \times 100$$
