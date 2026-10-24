# BioE Radar accounts

Google Authentication and Firestore are configured in Firebase project `bioe-radar` (Spark). The authorized public domain is `hanmd1990.github.io`; the default Standard Firestore database is in `asia-east2` (Hong Kong). No billing upgrade is required by this change.

`static/literature-account.js` loads official Firebase JS SDK 13.1.0. Web app identifiers are intentionally public. No administrator credential, OAuth client secret, or WeChat secret belongs in this repository.

Private feedback is stored at `readers/{Firebase UID}/feedback/{SHA-256 canonical DOI or article ID}`. The published rules allow only that signed-in UID to read or write its documents, validate fields/types/lengths/signals, require a server timestamp and immutable identity, and deny all other paths and permanent deletion. An empty signal/note document is an undo tombstone. Feedback is not copied to GitHub or the public article payload. Firestore uses its default memory cache; signing out clears the visible feedback and listener.

The rules in `firestore.rules` were published in the Firebase Console on 2026-10-24, after seven passing local Firestore emulator checks covering ownership, anonymous access, injection, validation, timestamps and undo, and retrieved from the published console editor for source control. Security rules are a prototype requiring review before a broader launch.

`For you` uses private signals and the public article history to rank by title/summary similarity and topic overlap. Notes are private reading references, not interpreted by AI. Rankings remain bounded by editorial relevance, retain all articles, and demote an explicitly irrelevant paper. No export/import step is needed. Weekly public surveys remain separate from per-account ranking; the scheduled ChatGPT task does not automatically access private Firestore data.

WeChat remains pending an approved WeChat Open Platform website application and a secure server-side token exchange/custom Firebase token endpoint. AppSecret must never be placed in frontend JavaScript. There is no pretend WeChat login button.

Run ranking tests: `node --test bioe-account/test/personalization.cjs`. Build and verify the site with the existing repository workflow. Actual Google login and cross-tab saving must also be checked in the deployed website before declaring end-to-end verification complete.
