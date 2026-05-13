╔═══════════════════════════════════════════════════════════════╗
║        PASSWORD STRENGTH ANALYZER PRO  —  README             ║
╚═══════════════════════════════════════════════════════════════╝

A professional cyberpunk-styled CLI tool for password analysis
and secure password generation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Python 3.9 or higher
  • pip (Python package manager)
  • Terminal with colour support (any modern Linux/macOS terminal,
    Windows Terminal, or Termux on Android)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  INSTALLATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ── Linux / macOS ─────────────────────────────────────────────

  # 1. Clone or copy the files into a directory
  mkdir psaw && cd psaw
  # (place password_analyzer.py and requirements.txt here)

  # 2. (Optional but recommended) create a virtual environment
  python3 -m venv .venv
  source .venv/bin/activate

  # 3. Install dependencies
  pip install -r requirements.txt

  # 4. Run
  python3 password_analyzer.py

  ── Termux (Android) ──────────────────────────────────────────

  pkg update && pkg upgrade
  pkg install python
  pip install -r requirements.txt
  python password_analyzer.py

  ── Windows ───────────────────────────────────────────────────

  # Use Windows Terminal for the best colour experience
  pip install -r requirements.txt
  python password_analyzer.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [1] Analyze Password
      • Strength score 0-100
      • Grade: Weak / Medium / Strong / Military Grade
      • Entropy calculation (bits)
      • Brute-force crack-time estimate (10 Bn guesses/s GPU)
      • Pattern detection:
          - Common/leaked passwords
          - Names, birthdays, keyboard walks
          - Repeated & sequential characters
      • Actionable improvement suggestions
      • Save full analysis to reports/analysis_TIMESTAMP.txt

  [2] Generate Strong Password
      • Four styles: gaming | hacker | professional | random
      • Configurable length (8-64)
      • Optional leet-speak transformation
      • Generates up to 20 passwords per run
      • Each password auto-analysed and graded
      • Export to reports/passwords_STYLE_TIMESTAMP.txt

  [3] Check Common Passwords
      • Interactive bulk checker
      • Database of 500+ most-commonly-used passwords

  [4] Export Report
      • Browse and view previously saved reports

  [5] Settings
      • Technical info, benchmark assumptions, entropy formula

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  psaw/
  ├── password_analyzer.py   ← main script
  ├── requirements.txt       ← pip dependencies
  ├── README.txt             ← this file
  └── reports/               ← auto-created; stores saved reports

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DEPENDENCIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  rich       ≥ 13.0.0   — beautiful terminal UI (tables, panels,
                           progress bars, spinners)
  colorama   ≥ 0.4.6    — cross-platform ANSI colour support
  pyfiglet   ≥ 0.8      — ASCII-art banner generation

  All are pure-Python and install without compilation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECURITY NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Passwords entered for analysis are NEVER stored, logged, or
    transmitted — they exist only in memory during the session.
  • Password input uses getpass (hidden echo) where available.
  • Generated passwords use Python's random.SystemRandom()
    (CSPRNG backed by os.urandom).
  • Crack-time estimates assume an offline attack with a
    10-billion-guess-per-second GPU cluster.  Online attacks
    are typically orders of magnitude slower.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
