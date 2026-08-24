# arabic-fold

Make Arabic search match the spellings people actually type.

Arabic has several places where one word is legitimately written more than one
way, and people are inconsistent about all of them. These are not typos — both
spellings are normal, and you will get both:

| | | |
|---|---|---|
| ta marbuta / ha | `قهوة` `قهوه` | coffee |
| alef maqsura / ya | `مقهى` `مقهي` | cafe |
| hamza carriers | `أسواق` `اسواق` | market |
| harakat, tatweel | `مَكْتَبَة` `مكتـــبة` | library |

An index that stores these verbatim matches only whichever spelling your data
happens to use, and returns **nothing** to everyone who types the other one.

## The part that is easy to get wrong

Folding is two-sided. You fold values going *into* the index, and you fold the
query coming *out* to it. Miss either one and the two sides are speaking
different alphabets.

Five records, and nine searches — the same words, each typed both of the normal
ways:

| | found |
|---|---|
| fold neither side | 5 of 9 |
| **fold the index only** | **5 of 9** |
| fold both sides | **9 of 9** |

Look at the first two. Same score — and they find **opposite halves**. Folding
the index alone is not a partial fix; it moves the failure from one group of
users to another without shrinking it. You wrote a correct fold function and
changed nothing.

Which is why this library does not export a bare `fold()`. It exports the two
call sites, with the folding private inside both, so using half of it is not
something you can accidentally do:

```python
from arabic_fold import index_text, search_text

# writing to the index
db.execute("INSERT INTO fts(term) VALUES (?)", (index_text(name),))

# searching it
db.execute("SELECT * FROM fts WHERE fts MATCH ?", (search_text(query),))
```

### The word that hides the bug

`مطعم` (restaurant) has no foldable letter, so it matches whether you fold or
not. Spot-check with it and all three rows above look identical. It is kept in
the test table deliberately, labelled, so nobody rediscovers this the hard way.

## Your tokenizer will not do this for you

SQLite FTS5 with `remove_diacritics 2` strips the harakat, and that is all it
does. It will not fold ta marbuta to ha, which is the one that matters most.

```sql
CREATE VIRTUAL TABLE places_fts USING fts5(
  name_norm,                                    -- store index_text(name) here
  tokenize="unicode61 remove_diacritics 2"
);
```

Whatever the tokenizer does not do, both sides still have to.

## pairs.json is the contract

`pairs.json` holds every input → expected pair. The Python suite reads it, and
so does the JavaScript one. Neither implementation is the source of truth — the
table is.

```
python3 test_fold.py                  # Python
python3 -m http.server                # then open /demo/test.html for the JS
```

Add a language and hold it to the same file. Two implementations of a fold will
drift, and drift surfaces as missing search results rather than as an error —
which is exactly the failure this library exists to prevent. Breaking a single
letter in one implementation fails six cases in the table; that is the point of
it.

## Latin too

Names come mixed. `index_text` routes by script, so accents and case are folded
the same way on the Latin side — `Café` and `CAFE` are one term.

## Licence

**MIT.** Use it, ship it, sell what you build with it. See `LICENSE`.

It is permissive because the problem is not a competitive advantage — an Arabic
search box that returns nothing is a bug the whole ecosystem has, and a library
nobody may use fixes none of it.

The MIT grant covers the code. It does not cover trademarks: the name **3reeq**,
the wordmark and the shurfa logomark are brand identity and are not licensed.
Other 3reeq work sets its terms per item — see <https://3reeq.com/rights>.
