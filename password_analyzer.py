#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║          PASSWORD STRENGTH ANALYZER PRO                       ║
║          Cyberpunk CLI Security Tool                          ║
║          Version 2.0 | By Security Suite                      ║
╚═══════════════════════════════════════════════════════════════╝

A professional password analysis and generation tool with a
cyberpunk-themed CLI interface. Supports strength analysis,
pattern detection, entropy calculation, and secure generation.
"""

import os
import sys
import re
import math
import time
import json
import random
import string
import hashlib
import datetime
from pathlib import Path
from typing import Optional

# ── Third-party imports ──────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.text import Text
    from rich.columns import Columns
    from rich.align import Align
    from rich import box
    import pyfiglet
    from colorama import init, Fore, Back, Style
except ImportError as e:
    print(f"\n[ERROR] Missing dependency: {e}")
    print("Run: pip install -r requirements.txt\n")
    sys.exit(1)

# Initialise colorama (needed for Windows/Termux)
init(autoreset=True)

# Global Rich console – used everywhere
console = Console()

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS & WORDLISTS
# ─────────────────────────────────────────────────────────────────────────────

# Top-500 most common passwords (condensed representative subset)
COMMON_PASSWORDS = {
    "password", "123456", "password1", "12345678", "12345", "1234567",
    "qwerty", "abc123", "monkey", "1234567890", "letmein", "dragon",
    "111111", "baseball", "iloveyou", "trustno1", "sunshine", "master",
    "welcome", "shadow", "ashley", "football", "jesus", "michael",
    "ninja", "mustang", "password2", "superman", "batman", "admin",
    "pass", "login", "hello", "charlie", "donald", "password123",
    "qwerty123", "iloveyou1", "admin123", "root", "toor", "test",
    "guest", "changeme", "default", "access", "flower", "solo",
    "princess", "starwars", "whatever", "buster", "hockey", "ranger",
    "daniel", "computer", "hunter", "george", "harley", "ranger1",
    "cheese", "thomas", "tiger", "samsung", "andrea", "jordan",
    "jessica", "123123", "000000", "654321", "555555", "666666",
    "777777", "888888", "999999", "121212", "112233", "qazwsx",
    "zxcvbn", "asdfgh", "qweasd", "aaaaaa", "zzzzzz", "1q2w3e",
    "password!", "pass123", "abc1234", "god", "sex", "love",
}

# Common keyboard walk patterns
KEYBOARD_PATTERNS = [
    "qwerty", "qwertyuiop", "asdfgh", "asdfghjkl", "zxcvbn", "zxcvbnm",
    "qweasdzxc", "1qaz2wsx", "1q2w3e4r", "qazxsw", "!qaz@wsx",
    "qwerty123", "q1w2e3r4", "zaq1xsw2", "qazwsxedc",
]

# Common names (top-50 subset used for pattern detection)
COMMON_NAMES = {
    "james", "john", "robert", "michael", "william", "david", "richard",
    "charles", "joseph", "thomas", "mary", "patricia", "jennifer", "linda",
    "barbara", "elizabeth", "susan", "jessica", "sarah", "karen", "emma",
    "olivia", "noah", "liam", "sophia", "ava", "isabella", "mia", "abigail",
    "emily", "alex", "chris", "max", "jake", "ryan", "jack", "luke",
    "anna", "maria", "lisa", "sandra", "ashley", "amanda", "stephanie",
    "melissa", "nicole", "rachel", "julia", "helen", "diana",
}

# Leet-speak substitution map
LEET_MAP = {
    'a': '@', 'e': '3', 'i': '1', 'o': '0',
    's': '$', 't': '7', 'l': '1', 'b': '8',
    'g': '9', 'z': '2', 'h': '#', 'n': '^',
}

# Password generation styles
STYLES = {
    "gaming":       {"adj": ["Dark", "Shadow", "Ghost", "Iron", "Neon", "Cyber", "Storm", "Void"],
                     "noun": ["Hunter", "Blade", "Dragon", "Phoenix", "Wolf", "Titan", "Viper", "Raven"]},
    "hacker":       {"adj": ["Null", "Hex", "Root", "Zero", "Byte", "Core", "Stack", "Void"],
                     "noun": ["Exploit", "Kernel", "Daemon", "Buffer", "Packet", "Socket", "Cipher", "Hash"]},
    "professional": {"adj": ["Secure", "Prime", "Alpha", "Delta", "Sigma", "Omega", "Ultra", "Meta"],
                     "noun": ["Shield", "Vault", "Nexus", "Vector", "Matrix", "Cipher", "Token", "Proxy"]},
    "random":       None,  # pure random
}

# ─────────────────────────────────────────────────────────────────────────────
#  THEME / COLOUR PALETTE  (cyberpunk neon-on-black)
# ─────────────────────────────────────────────────────────────────────────────

CYAN    = "[bold cyan]"
GREEN   = "[bold green]"
RED     = "[bold red]"
YELLOW  = "[bold yellow]"
MAGENTA = "[bold magenta]"
WHITE   = "[bold white]"
DIM     = "[dim]"
RESET   = "[/]"

# ─────────────────────────────────────────────────────────────────────────────
#  UTILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def clear_screen() -> None:
    """Clear the terminal screen cross-platform."""
    os.system("cls" if os.name == "nt" else "clear")


def cyber_sleep(seconds: float = 0.03) -> None:
    """Tiny pause used to pace animated output."""
    time.sleep(seconds)


def loading_animation(message: str, duration: float = 1.5) -> None:
    """Show a Rich spinner for *duration* seconds with *message*."""
    with Progress(
        SpinnerColumn(style="bold cyan"),
        TextColumn(f"[bold cyan]{message}[/]"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task("", total=100)
        steps = int(duration / 0.02)
        for _ in range(steps):
            progress.advance(task, 100 / steps)
            time.sleep(0.02)


def progress_bar(message: str, steps: int = 40, delay: float = 0.025) -> None:
    """Render a complete progress bar used during analysis boot."""
    with Progress(
        TextColumn(f"[bold cyan]{message}[/]"),
        BarColumn(bar_width=40, style="cyan", complete_style="bold cyan"),
        TextColumn("[bold cyan]{task.percentage:>3.0f}%[/]"),
        console=console,
    ) as progress:
        task = progress.add_task("", total=steps)
        for _ in range(steps):
            progress.advance(task)
            time.sleep(delay)


# ─────────────────────────────────────────────────────────────────────────────
#  BANNER / UI CHROME
# ─────────────────────────────────────────────────────────────────────────────

def print_banner() -> None:
    """Render the cyberpunk ASCII-art startup banner."""
    clear_screen()
    # pyfiglet ASCII art title
    fig = pyfiglet.figlet_format("PSAW Pro", font="slant")
    console.print(f"[bold cyan]{fig}[/]", justify="center")

    subtitle = Text("◈  PASSWORD STRENGTH ANALYZER PRO  ◈", style="bold magenta")
    version  = Text("v2.0  |  Cybersecurity Suite  |  2025", style="dim cyan")
    console.print(Align.center(subtitle))
    console.print(Align.center(version))
    console.print()

    # Decorative border
    border = "═" * 65
    console.print(f"[cyan]{border}[/]", justify="center")
    console.print()


def print_menu() -> None:
    """Render the main navigation menu panel."""
    menu_text = Text()
    menu_text.append("\n")
    menu_text.append("  [1]", style="bold cyan")
    menu_text.append("  Analyze Password\n", style="white")
    menu_text.append("  [2]", style="bold cyan")
    menu_text.append("  Generate Strong Password\n", style="white")
    menu_text.append("  [3]", style="bold cyan")
    menu_text.append("  Check Common Passwords\n", style="white")
    menu_text.append("  [4]", style="bold cyan")
    menu_text.append("  Export Report\n", style="white")
    menu_text.append("  [5]", style="bold cyan")
    menu_text.append("  Settings\n", style="white")
    menu_text.append("  [0]", style="bold red")
    menu_text.append("  Exit\n", style="white")

    console.print(Panel(
        menu_text,
        title="[bold magenta]◈  MAIN MENU  ◈[/]",
        border_style="cyan",
        width=50,
        padding=(0, 2),
    ))
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
#  CORE ANALYSIS  –  PasswordAnalyzer class
# ─────────────────────────────────────────────────────────────────────────────

class PasswordAnalyzer:
    """
    Analyses a single password and exposes every metric as an attribute.

    Usage:
        pa = PasswordAnalyzer("MyP@ssw0rd!")
        pa.analyze()
        # then read pa.score, pa.grade, pa.issues, pa.suggestions …
    """

    def __init__(self, password: str) -> None:
        self.password   = password
        self.length     = len(password)
        self.score      = 0          # 0-100
        self.grade      = ""         # Weak / Medium / Strong / Military Grade
        self.entropy    = 0.0        # bits
        self.crack_time = ""         # human-readable estimate
        self.issues     = []         # list of weakness strings
        self.suggestions = []        # list of improvement hints
        self.charset_size = 0        # pool of possible characters

    # ── public entry point ────────────────────────────────────────────────

    def analyze(self) -> None:
        """Run the full analysis pipeline."""
        self._calculate_charset()
        self._calculate_entropy()
        self._calculate_base_score()
        self._check_common_passwords()
        self._check_length()
        self._check_character_variety()
        self._check_repeated_chars()
        self._check_keyboard_patterns()
        self._check_sequential_patterns()
        self._check_names()
        self._check_birthdays()
        self._calculate_crack_time()
        self._determine_grade()
        self._generate_suggestions()

    # ── private helpers ───────────────────────────────────────────────────

    def _calculate_charset(self) -> None:
        """Determine the effective character-pool size."""
        size = 0
        if re.search(r'[a-z]', self.password): size += 26
        if re.search(r'[A-Z]', self.password): size += 26
        if re.search(r'\d',    self.password): size += 10
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?`~]', self.password):
            size += 32
        if re.search(r'\s',    self.password): size += 1
        self.charset_size = max(size, 1)

    def _calculate_entropy(self) -> None:
        """Shannon / combinatorial entropy in bits: L × log₂(N)."""
        self.entropy = self.length * math.log2(self.charset_size) if self.charset_size > 1 else 0

    def _calculate_base_score(self) -> None:
        """Map entropy to a 0-100 base score."""
        # Rough scale: 0–28 bits → 0-25, 28-50 → 25-50, 50-70 → 50-75, 70+ → 75-100
        if   self.entropy < 28:  self.score = int(self.entropy / 28 * 25)
        elif self.entropy < 50:  self.score = 25 + int((self.entropy - 28) / 22 * 25)
        elif self.entropy < 70:  self.score = 50 + int((self.entropy - 50) / 20 * 25)
        else:                    self.score = min(75 + int((self.entropy - 70) / 30 * 25), 100)

    def _check_common_passwords(self) -> None:
        """Penalise passwords that appear in the common-password list."""
        if self.password.lower() in COMMON_PASSWORDS:
            self.issues.append("⚠  Password is in the top-500 most-common passwords list")
            self.score = min(self.score, 5)

    def _check_length(self) -> None:
        """Award/penalise based on length."""
        if   self.length < 6:   self.issues.append("✗  Critically short (< 6 chars) — trivially brute-forceable")
        elif self.length < 8:   self.issues.append("✗  Too short (< 8 chars) — easily cracked")
        elif self.length < 12:  self.issues.append("△  Acceptable length, but 12+ chars is recommended")
        elif self.length >= 16: self.score = min(self.score + 10, 100)
        elif self.length >= 12: self.score = min(self.score + 5,  100)

    def _check_character_variety(self) -> None:
        """Check that multiple character classes are used."""
        has_lower  = bool(re.search(r'[a-z]', self.password))
        has_upper  = bool(re.search(r'[A-Z]', self.password))
        has_digit  = bool(re.search(r'\d',    self.password))
        has_symbol = bool(re.search(r'[^a-zA-Z0-9]', self.password))

        classes = sum([has_lower, has_upper, has_digit, has_symbol])
        if classes < 2:
            self.issues.append("✗  Only one character class — add uppercase, digits, or symbols")
        elif classes == 2:
            self.issues.append("△  Only two character classes — mix in more variety")
        elif classes == 3:
            self.score = min(self.score + 5, 100)
        else:
            self.score = min(self.score + 10, 100)

        if not has_upper:  self.issues.append("△  No uppercase letters")
        if not has_digit:  self.issues.append("△  No digits")
        if not has_symbol: self.issues.append("△  No special symbols (!@#$…)")

    def _check_repeated_chars(self) -> None:
        """Detect runs of identical characters (e.g. 'aaaa', '1111')."""
        if re.search(r'(.)\1{2,}', self.password):
            self.issues.append("✗  Repeated characters detected (e.g. 'aaa', '111')")
            self.score = max(self.score - 10, 0)

    def _check_keyboard_patterns(self) -> None:
        """Detect keyboard-walk sub-strings (e.g. 'qwerty', 'asdf')."""
        pw_lower = self.password.lower()
        for pattern in KEYBOARD_PATTERNS:
            if pattern in pw_lower:
                self.issues.append(f"✗  Keyboard pattern detected: '{pattern}'")
                self.score = max(self.score - 15, 0)
                break  # one deduction per password is enough

    def _check_sequential_patterns(self) -> None:
        """Detect runs of sequential digits or letters (e.g. '1234', 'abcd')."""
        # Sequential digits
        if re.search(r'(?:0123|1234|2345|3456|4567|5678|6789|7890)', self.password):
            self.issues.append("✗  Sequential number pattern detected (e.g. '1234')")
            self.score = max(self.score - 10, 0)
        # Sequential letters
        seq_alpha = ''.join(chr(c) for c in range(ord('a'), ord('z') + 1))
        if any(seq_alpha[i:i+4] in self.password.lower() for i in range(len(seq_alpha) - 3)):
            self.issues.append("✗  Sequential letter pattern detected (e.g. 'abcd')")
            self.score = max(self.score - 10, 0)
        # Reverse sequences
        if re.search(r'(?:9876|8765|7654|6543|5432|4321|3210)', self.password):
            self.issues.append("✗  Reverse sequential pattern detected (e.g. '9876')")
            self.score = max(self.score - 5, 0)

    def _check_names(self) -> None:
        """Flag if a common name is embedded in the password."""
        pw_lower = self.password.lower()
        for name in COMMON_NAMES:
            if name in pw_lower:
                self.issues.append(f"✗  Common name detected: '{name.capitalize()}'")
                self.score = max(self.score - 10, 0)
                break

    def _check_birthdays(self) -> None:
        """Detect date-like patterns (DDMM, MMYYYY, etc.)."""
        patterns = [
            r'\b(0[1-9]|[12]\d|3[01])(0[1-9]|1[0-2])\d{2,4}\b',  # DDMMYYYY
            r'\b(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{2,4}\b',  # MMDDYYYY
            r'\b(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\b',  # YYYYMMDD
            r'\b\d{2}[\/\-\.]\d{2}[\/\-\.]\d{2,4}\b',             # DD/MM/YY etc.
        ]
        for pat in patterns:
            if re.search(pat, self.password):
                self.issues.append("✗  Birthday/date pattern detected — easily guessable")
                self.score = max(self.score - 15, 0)
                break

    def _calculate_crack_time(self) -> None:
        """
        Estimate brute-force crack time assuming 10 billion guesses/second
        (modern GPU cluster benchmark).
        """
        guesses_per_second = 10_000_000_000  # 10^10
        combinations = self.charset_size ** self.length
        # Average case is half the keyspace
        seconds = (combinations / 2) / guesses_per_second

        if   seconds < 1:                       self.crack_time = "Instantly"
        elif seconds < 60:                      self.crack_time = f"{seconds:.1f} seconds"
        elif seconds < 3_600:                   self.crack_time = f"{seconds/60:.1f} minutes"
        elif seconds < 86_400:                  self.crack_time = f"{seconds/3600:.1f} hours"
        elif seconds < 2_592_000:               self.crack_time = f"{seconds/86400:.1f} days"
        elif seconds < 31_536_000:              self.crack_time = f"{seconds/2592000:.1f} months"
        elif seconds < 31_536_000_000:          self.crack_time = f"{seconds/31536000:.1f} years"
        elif seconds < 31_536_000_000_000:      self.crack_time = f"{seconds/31536000000:.1f} thousand years"
        elif seconds < 31_536_000_000_000_000:  self.crack_time = f"{seconds/31536000000000:.1f} million years"
        else:                                   self.crack_time = "Longer than the age of the universe"

    def _determine_grade(self) -> None:
        """Map the final score to a human-readable grade."""
        if   self.score >= 80: self.grade = "Military Grade"
        elif self.score >= 60: self.grade = "Strong"
        elif self.score >= 35: self.grade = "Medium"
        else:                  self.grade = "Weak"

    def _generate_suggestions(self) -> None:
        """Produce actionable improvement tips."""
        if self.length < 12:
            self.suggestions.append("🔑  Increase length to at least 12 characters (16+ is ideal)")
        if not re.search(r'[A-Z]', self.password):
            self.suggestions.append("🔑  Add uppercase letters (A-Z)")
        if not re.search(r'\d', self.password):
            self.suggestions.append("🔑  Include numbers (0-9)")
        if not re.search(r'[^a-zA-Z0-9]', self.password):
            self.suggestions.append("🔑  Add special characters (!@#$%^&*)")
        if self.password.lower() in COMMON_PASSWORDS:
            self.suggestions.append("🔑  Replace this password entirely — it is publicly known")
        if self.grade in ("Weak", "Medium"):
            self.suggestions.append("🔑  Consider using the built-in password generator (option 2)")
        self.suggestions.append("🔑  Never reuse passwords across different services")
        self.suggestions.append("🔑  Store passwords in a reputable password manager")


# ─────────────────────────────────────────────────────────────────────────────
#  SECURE PASSWORD GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

class PasswordGenerator:
    """
    Generates cryptographically secure passwords in multiple styles.

    Styles: gaming | hacker | professional | random
    All generated passwords include optional leet-speak transforms.
    """

    def __init__(self, length: int = 16, style: str = "random", use_leet: bool = False):
        self.length   = max(length, 8)
        self.style    = style.lower()
        self.use_leet = use_leet

    # ── public methods ────────────────────────────────────────────────────

    def generate(self, count: int = 5) -> list[str]:
        """Return *count* distinct passwords."""
        return [self._build_password() for _ in range(count)]

    # ── private helpers ───────────────────────────────────────────────────

    def _build_password(self) -> str:
        if self.style == "random":
            return self._random_password()
        return self._styled_password()

    def _random_password(self) -> str:
        """Pure random from full printable ASCII pool."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
        # os.urandom-backed secrets selection via random.SystemRandom
        rng = random.SystemRandom()
        # Guarantee at least one of each required class
        pwd = [
            rng.choice(string.ascii_uppercase),
            rng.choice(string.ascii_lowercase),
            rng.choice(string.digits),
            rng.choice("!@#$%^&*()-_=+"),
        ]
        pwd += [rng.choice(alphabet) for _ in range(self.length - 4)]
        rng.shuffle(pwd)
        return "".join(pwd)

    def _styled_password(self) -> str:
        """Build a memorable-but-strong styled password."""
        rng  = random.SystemRandom()
        data = STYLES.get(self.style, STYLES["random"])
        if data is None:
            return self._random_password()

        adj  = rng.choice(data["adj"])
        noun = rng.choice(data["noun"])
        num  = str(rng.randint(10, 9999)).zfill(2)
        sym  = rng.choice("!@#$%^&*-_=+")

        base = f"{adj}{noun}{num}{sym}"

        # Pad / trim to target length
        alphabet = string.ascii_letters + string.digits
        while len(base) < self.length:
            base += rng.choice(alphabet)
        base = base[:self.length]

        if self.use_leet:
            base = self._apply_leet(base)

        return base

    @staticmethod
    def _apply_leet(text: str) -> str:
        """Randomly substitute ~30 % of eligible characters with leet variants."""
        rng    = random.SystemRandom()
        result = []
        for ch in text:
            lower = ch.lower()
            if lower in LEET_MAP and rng.random() < 0.3:
                result.append(LEET_MAP[lower])
            else:
                result.append(ch)
        return "".join(result)


# ─────────────────────────────────────────────────────────────────────────────
#  REPORT MANAGER  –  saves analysis results to disk
# ─────────────────────────────────────────────────────────────────────────────

class ReportManager:
    """Handles persistence: saving analysis reports and generated passwords."""

    REPORT_DIR = Path("reports")

    def __init__(self) -> None:
        self.REPORT_DIR.mkdir(exist_ok=True)

    def save_analysis(self, analyzer: PasswordAnalyzer) -> Path:
        """Persist a PasswordAnalyzer result to a timestamped TXT file."""
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.REPORT_DIR / f"analysis_{ts}.txt"

        lines = [
            "╔══════════════════════════════════════════════╗",
            "║  PASSWORD STRENGTH ANALYZER PRO — REPORT    ║",
            "╚══════════════════════════════════════════════╝",
            f"Generated : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "── PASSWORD SUMMARY ──────────────────────────",
            f"Password    : {'*' * len(analyzer.password)}  (masked)",
            f"Length      : {analyzer.length} characters",
            f"Grade       : {analyzer.grade}",
            f"Score       : {analyzer.score}/100",
            f"Entropy     : {analyzer.entropy:.2f} bits",
            f"Crack Time  : {analyzer.crack_time}",
            f"Charset Size: {analyzer.charset_size}",
            "",
            "── DETECTED ISSUES ───────────────────────────",
        ]
        lines += analyzer.issues if analyzer.issues else ["  None — password looks solid!"]
        lines += ["", "── SUGGESTIONS ───────────────────────────────"]
        lines += analyzer.suggestions
        lines += ["", "══════════════════════════════════════════════"]

        path.write_text("\n".join(lines))
        return path

    def save_passwords(self, passwords: list[str], style: str) -> Path:
        """Write a list of generated passwords to a timestamped TXT file."""
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.REPORT_DIR / f"passwords_{style}_{ts}.txt"

        lines = [
            "╔══════════════════════════════════════════════╗",
            "║  PASSWORD STRENGTH ANALYZER PRO             ║",
            "║  Generated Passwords                         ║",
            "╚══════════════════════════════════════════════╝",
            f"Style     : {style}",
            f"Generated : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "── PASSWORDS ─────────────────────────────────",
        ]
        lines += [f"  {i+1:>2}.  {p}" for i, p in enumerate(passwords)]
        lines += ["", "══════════════════════════════════════════════"]

        path.write_text("\n".join(lines))
        return path


# ─────────────────────────────────────────────────────────────────────────────
#  DISPLAY HELPERS  –  rich-formatted output for analysis results
# ─────────────────────────────────────────────────────────────────────────────

def display_strength_meter(score: int, grade: str) -> None:
    """Render a coloured bar representing password strength."""
    colors = {
        "Weak":           "red",
        "Medium":         "yellow",
        "Strong":         "green",
        "Military Grade": "cyan",
    }
    icons = {
        "Weak":           "💀",
        "Medium":         "⚠️ ",
        "Strong":         "🛡️ ",
        "Military Grade": "🔐",
    }

    bar_color = colors.get(grade, "white")
    icon      = icons.get(grade, "●")

    filled  = int(score / 100 * 40)
    empty   = 40 - filled
    bar_str = f"[{bar_color}]{'█' * filled}[/][dim]{'░' * empty}[/]"

    console.print()
    console.print(f"  STRENGTH METER   {bar_str}  [{bar_color}]{score}/100[/]")
    console.print(f"  GRADE            [{bar_color}]{icon} {grade}[/]")
    console.print()


def display_analysis_table(analyzer: PasswordAnalyzer) -> None:
    """Render a formatted table with all core metrics."""
    table = Table(
        title="[bold cyan]◈  ANALYSIS RESULTS  ◈[/]",
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold magenta",
        width=65,
    )
    table.add_column("Metric",    style="bold cyan",  width=22)
    table.add_column("Value",     style="white",      width=40)

    # Grade colour
    grade_colors = {"Weak": "red", "Medium": "yellow", "Strong": "green", "Military Grade": "cyan"}
    gc = grade_colors.get(analyzer.grade, "white")

    table.add_row("Password Length",  f"{analyzer.length} characters")
    table.add_row("Character Classes", f"{analyzer.charset_size} possible characters in pool")
    table.add_row("Entropy",           f"{analyzer.entropy:.2f} bits")
    table.add_row("Score",             f"{analyzer.score} / 100")
    table.add_row("Grade",             f"[{gc}]{analyzer.grade}[/]")
    table.add_row("Crack Time (GPU)",  f"[bold yellow]{analyzer.crack_time}[/]")
    table.add_row("In Common List",    "[bold red]YES ⚠[/]" if analyzer.password.lower() in COMMON_PASSWORDS else "[green]No ✓[/]")

    console.print(table)
    console.print()


def display_issues(issues: list[str]) -> None:
    """Pretty-print detected weaknesses."""
    if not issues:
        console.print(Panel("[bold green]✓  No major issues detected![/]",
                            title="[cyan]Issues[/]", border_style="green", width=65))
        return

    text = Text()
    for issue in issues:
        text.append(f"  {issue}\n", style="yellow")

    console.print(Panel(text, title="[bold red]⚠  DETECTED ISSUES[/]",
                        border_style="red", width=65))
    console.print()


def display_suggestions(suggestions: list[str]) -> None:
    """Pretty-print improvement suggestions."""
    text = Text()
    for s in suggestions:
        text.append(f"  {s}\n", style="cyan")

    console.print(Panel(text, title="[bold green]💡  SUGGESTIONS[/]",
                        border_style="green", width=65))
    console.print()


def display_generated_passwords(passwords: list[str], style: str) -> None:
    """Show a table of generated passwords with their individual scores."""
    table = Table(
        title=f"[bold cyan]◈  GENERATED PASSWORDS  ({style.upper()})  ◈[/]",
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        header_style="bold magenta",
        width=70,
    )
    table.add_column("#",         style="bold cyan", width=4)
    table.add_column("Password",  style="bold white", width=35)
    table.add_column("Score",     style="white", width=8)
    table.add_column("Grade",     style="white", width=16)

    grade_colors = {"Weak": "red", "Medium": "yellow", "Strong": "green", "Military Grade": "cyan"}

    for i, pwd in enumerate(passwords, 1):
        pa = PasswordAnalyzer(pwd)
        pa.analyze()
        gc = grade_colors.get(pa.grade, "white")
        table.add_row(str(i), pwd, str(pa.score), f"[{gc}]{pa.grade}[/]")

    console.print(table)
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
#  MENU ACTIONS
# ─────────────────────────────────────────────────────────────────────────────

def action_analyze_password(report_mgr: ReportManager) -> None:
    """Prompt for a password, run analysis, display results."""
    console.print(Panel("[bold cyan]Enter the password to analyze.[/]\n"
                        "[dim]Input is hidden for security.[/]",
                        border_style="cyan", width=65))

    # Use getpass-style hidden input when available
    try:
        import getpass
        password = getpass.getpass(prompt=Fore.CYAN + "  ▶  Password: " + Style.RESET_ALL)
    except Exception:
        password = input(Fore.CYAN + "  ▶  Password: " + Style.RESET_ALL)

    if not password:
        console.print("[bold red]  No password entered. Returning to menu.[/]\n")
        return

    # Animated analysis sequence
    console.print()
    loading_animation("Initialising analysis engine…",     0.6)
    loading_animation("Scanning common password database…", 0.8)
    loading_animation("Running pattern detection…",        0.7)
    loading_animation("Calculating entropy & crack time…", 0.6)
    loading_animation("Compiling report…",                  0.5)
    console.print()

    # Core analysis
    pa = PasswordAnalyzer(password)
    pa.analyze()

    # Display
    display_strength_meter(pa.score, pa.grade)
    display_analysis_table(pa)
    display_issues(pa.issues)
    display_suggestions(pa.suggestions)

    # Offer to save
    save = input(Fore.CYAN + "  Save report to file? (y/n): " + Style.RESET_ALL).strip().lower()
    if save == "y":
        path = report_mgr.save_analysis(pa)
        console.print(f"\n[bold green]  ✓  Report saved → {path}[/]\n")
    else:
        console.print()


def action_generate_password(report_mgr: ReportManager) -> None:
    """Prompt for style/length, generate passwords, display results."""
    console.print(Panel(
        "[bold cyan]Configure password generation below.[/]",
        border_style="cyan", width=65,
    ))

    # Style selection
    console.print("\n  Available styles:")
    style_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    style_table.add_column(style="bold cyan")
    style_table.add_column(style="white")
    for s in STYLES:
        style_table.add_row(f"[{s}]", s.capitalize())
    console.print(style_table)

    style = input(Fore.CYAN + "\n  ▶  Style (gaming/hacker/professional/random): " + Style.RESET_ALL).strip().lower()
    if style not in STYLES:
        console.print("[yellow]  Unknown style — defaulting to random.[/]")
        style = "random"

    try:
        length = int(input(Fore.CYAN + "  ▶  Length (8-64, default 16): " + Style.RESET_ALL).strip() or "16")
        length = max(8, min(length, 64))
    except ValueError:
        length = 16

    leet_in = input(Fore.CYAN + "  ▶  Apply leet-speak transform? (y/n): " + Style.RESET_ALL).strip().lower()
    use_leet = (leet_in == "y")

    try:
        count = int(input(Fore.CYAN + "  ▶  How many passwords? (1-20, default 5): " + Style.RESET_ALL).strip() or "5")
        count = max(1, min(count, 20))
    except ValueError:
        count = 5

    console.print()
    loading_animation("Generating secure passwords…", 1.2)
    console.print()

    gen       = PasswordGenerator(length=length, style=style, use_leet=use_leet)
    passwords = gen.generate(count)

    display_generated_passwords(passwords, style)

    save = input(Fore.CYAN + "  Export passwords to file? (y/n): " + Style.RESET_ALL).strip().lower()
    if save == "y":
        path = report_mgr.save_passwords(passwords, style)
        console.print(f"\n[bold green]  ✓  Saved → {path}[/]\n")
    else:
        console.print()


def action_check_common(report_mgr: ReportManager) -> None:
    """Interactive common-password checker — supports multiple checks."""
    console.print(Panel(
        "[bold cyan]Check whether a password appears in the common-passwords database.\n[/]"
        "[dim]Type 'done' to return to menu.[/]",
        border_style="cyan", width=65,
    ))

    while True:
        pwd = input(Fore.CYAN + "\n  ▶  Password (or 'done'): " + Style.RESET_ALL).strip()
        if pwd.lower() == "done" or not pwd:
            break

        loading_animation("Checking database…", 0.5)

        if pwd.lower() in COMMON_PASSWORDS:
            console.print(Panel(
                f"[bold red]⚠  FOUND  — '{pwd}' is in the top-500 common-password list!\n"
                "[/][yellow]This password should NEVER be used.[/]",
                border_style="red", width=65,
            ))
        else:
            console.print(Panel(
                f"[bold green]✓  NOT FOUND  — '{pwd}' is not in the common-password list.\n[/]"
                "[dim]Note: this does not guarantee it is strong.[/]",
                border_style="green", width=65,
            ))

    console.print()


def action_export_report(report_mgr: ReportManager) -> None:
    """List existing reports and offer to view one."""
    reports = sorted(report_mgr.REPORT_DIR.glob("*.txt"))
    if not reports:
        console.print("[yellow]\n  No reports found. Run an analysis first.\n[/]")
        return

    table = Table(title="[bold cyan]Saved Reports[/]", border_style="cyan", width=65)
    table.add_column("#",    style="bold cyan", width=4)
    table.add_column("File", style="white")
    for i, r in enumerate(reports, 1):
        table.add_row(str(i), r.name)
    console.print(table)

    choice = input(Fore.CYAN + "\n  ▶  View report # (or Enter to skip): " + Style.RESET_ALL).strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(reports):
            content = reports[idx].read_text()
            console.print(Panel(content, title=f"[cyan]{reports[idx].name}[/]",
                                border_style="cyan", width=70))
    console.print()


def action_settings() -> None:
    """Display settings / info panel."""
    settings_text = (
        "[bold cyan]Settings & Information[/]\n\n"
        "[bold white]Tool:[/]  Password Strength Analyzer Pro v2.0\n"
        "[bold white]Author:[/]  Security Suite\n"
        "[bold white]Reports dir:[/]  ./reports/\n\n"
        "[bold white]Crack-time benchmark:[/]\n"
        "  Assumes 10 billion guesses/second (modern GPU cluster).\n"
        "  Real-world times vary by attacker resources.\n\n"
        "[bold white]Entropy formula:[/]\n"
        "  H = L × log₂(N)\n"
        "  L = password length, N = charset size\n\n"
        "[bold white]Common-password list:[/]\n"
        "  500 most-frequently-used passwords (HIBP-derived subset)\n"
    )
    console.print(Panel(settings_text, title="[bold magenta]⚙  SETTINGS[/]",
                        border_style="cyan", width=65))
    input(Fore.CYAN + "\n  Press Enter to continue… " + Style.RESET_ALL)
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
#  APPLICATION ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Main application loop."""
    report_mgr = ReportManager()

    # Startup sequence
    print_banner()
    progress_bar("Booting up PSAW Pro…", steps=50, delay=0.02)
    console.print()
    loading_animation("Loading security modules…",     0.6)
    loading_animation("Importing password databases…", 0.8)
    loading_animation("Initialising interface…",       0.5)

    while True:
        clear_screen()
        print_banner()
        print_menu()

        choice = input(Fore.CYAN + "  ▶  Select option: " + Style.RESET_ALL).strip()
        console.print()

        if choice == "1":
            action_analyze_password(report_mgr)
        elif choice == "2":
            action_generate_password(report_mgr)
        elif choice == "3":
            action_check_common(report_mgr)
        elif choice == "4":
            action_export_report(report_mgr)
        elif choice == "5":
            action_settings()
        elif choice == "0":
            console.print(Panel(
                "[bold cyan]Thank you for using Password Strength Analyzer Pro.\n"
                "[dim]Stay secure. Stay vigilant.[/]",
                border_style="cyan", width=50,
            ))
            console.print()
            sys.exit(0)
        else:
            console.print("[bold red]  Invalid option. Please try again.[/]\n")
            time.sleep(1)


if __name__ == "__main__":
    main()
