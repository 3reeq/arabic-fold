// Arabic search folding — the JavaScript side.
//
// This is a PORT. arabic_fold.py is the reference implementation, and both are
// held to ../pairs.json so they cannot drift apart quietly. If you change the
// fold here, change it there, and let the tests tell you if you missed a case.
//
// Same rule as the Python: no bare fold() is exported. Folding the index alone
// does not fix anything — it changes which half of your users get no results.
//
// THIS FILE IS COPIED to the 3reeq site as arabic-fold/fold.js for the live demo.
// The two must stay byte-identical — a page demonstrating that copies drift should
// not be served by a drifted copy. Check it:
//
//     diff site/arabic-fold/fold.js arabic-fold/demo/fold.js

const TATWEEL = /ـ/g;                    // kashida — decoration, no meaning
const HARAKAT = /[ً-ٰ]/g;           // short-vowel marks
const ARABIC_CHAR = /[؀-ۿ]/;
const PUNCT = /[^\p{L}\p{N}_\s؀-ۿ]+/gu;
const WS = /\s+/g;

const AR_MAP = {
  "أ": "ا",  // أ hamza above alef -> ا
  "إ": "ا",  // إ hamza below alef -> ا
  "آ": "ا",  // آ madda above alef -> ا
  "ٱ": "ا",  // ٱ wasla alef       -> ا
  "ى": "ي",  // ى alef maqsura     -> ي
  "ة": "ه",  // ة ta marbuta       -> ه
  "ؤ": "و",  // ؤ hamza on waw     -> و
  "ئ": "ي",  // ئ hamza on ya      -> ي
};

export function isArabic(text) {
  return Boolean(text) && ARABIC_CHAR.test(text);
}

function foldAr(text) {
  let s = text.replace(TATWEEL, "").replace(HARAKAT, "");
  s = s.replace(/./gu, (c) => AR_MAP[c] || c);
  return s.replace(PUNCT, " ").replace(WS, " ").trim().toLowerCase();
}

function foldLatin(text) {
  const s = text.normalize("NFKD").replace(/\p{M}/gu, "");
  return s.replace(PUNCT, " ").replace(WS, " ").trim().toLowerCase();
}

function fold(text) {
  if (!text) return "";
  return isArabic(text) ? foldAr(text) : foldLatin(text);
}

/** Fold a value on its way INTO the index. */
export function indexText(text) { return fold(text); }

/** Fold a query on its way OUT to the index. Same transform, by construction. */
export function searchText(query) { return fold(query); }
