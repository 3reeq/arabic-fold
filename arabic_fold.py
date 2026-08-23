"""Arabic search folding — make the spellings people actually type match.

Arabic has several places where one word is legitimately written more than one
way, and people are inconsistent about all of them. Not typos: both spellings
are normal.

    ta marbuta / ha      قهوة  vs  قهوه       coffee
    alef maqsura / ya    مقهى  vs  مقهي       cafe
    hamza carriers       أسواق vs  اسواق      market

A search index that stores these verbatim only matches whichever spelling the
data happens to use, and silently fails everyone who types the other one.

USE:

    from arabic_fold import index_text, search_text

    # when you write to the index
    db.execute("INSERT INTO fts(term) VALUES (?)", (index_text(name),))

    # when someone searches
    db.execute("SELECT * FROM fts WHERE fts MATCH ?", (search_text(query),))

Both sides, always. That is the whole point, and it is why this module does
not expose a bare fold() for you to call once and forget: folding the index
alone does not fix the problem, it just changes which half of your users get
no results. See the README.
"""

import re
import unicodedata

__all__ = ["index_text", "search_text", "is_arabic"]

# --- what gets folded ---------------------------------------------------

_TATWEEL = "ـ"                      # kashida, pure decoration, no meaning
_HARAKAT = re.compile(r"[ً-ٰٟ]")   # short-vowel marks

_AR_MAP = str.maketrans({
    "أ": "ا",   # أ  hamza above alef  -> ا
    "إ": "ا",   # إ  hamza below alef  -> ا
    "آ": "ا",   # آ  madda above alef  -> ا
    "ٱ": "ا",   # ٱ  wasla alef        -> ا
    "ى": "ي",   # ى  alef maqsura      -> ي
    "ة": "ه",   # ة  ta marbuta        -> ه
    "ؤ": "و",   # ؤ  hamza on waw      -> و
    "ئ": "ي",   # ئ  hamza on ya       -> ي
})

_ARABIC_CHAR = re.compile(r"[؀-ۿ]")
_PUNCT = re.compile(r"[^\w\s؀-ۿ]+", re.UNICODE)
_WS = re.compile(r"\s+")


def is_arabic(text):
    """True if the string contains any Arabic-script character."""
    return bool(text) and bool(_ARABIC_CHAR.search(text))


# --- the fold itself is private, deliberately ---------------------------

def _fold_ar(text):
    text = _HARAKAT.sub("", text.replace(_TATWEEL, ""))
    text = text.translate(_AR_MAP)
    return _WS.sub(" ", _PUNCT.sub(" ", text)).strip().lower()


def _fold_latin(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return _WS.sub(" ", _PUNCT.sub(" ", text)).strip().lower()


def _fold(text):
    if not text:
        return ""
    return _fold_ar(text) if is_arabic(text) else _fold_latin(text)


# --- the two sides. Use both. -------------------------------------------

def index_text(text):
    """Fold a value on its way INTO the index."""
    return _fold(text)


def search_text(query):
    """Fold a query on its way OUT to the index.

    Same transform as index_text by construction — they call one function.
    Two separate implementations would drift, and the drift surfaces as
    missing results rather than as an error.
    """
    return _fold(query)
