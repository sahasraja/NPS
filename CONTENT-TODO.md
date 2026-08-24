# Before this site goes live

> **The site is currently in preview mode.** `SITE["preview_mode"] = True` in
> `build.py` adds `noindex,nofollow` to every page and blocks all crawlers in
> `robots.txt`, so none of the placeholder content below can be indexed under your
> brand while you review. **Set it to `False` and rerun `python3 build.py` on launch
> day**, otherwise the finished site stays invisible to Google.

Everything in this file is scaffolding I wrote to demonstrate the structure and
tone. **None of it is verified fact about NPS.** Publishing it as-is would put
claims on your site that you can't back up, which is a bad look for any firm and
a worse one for a security firm.

Each item below names the exact location in `build.py`. Edit there, run
`python3 build.py`, done.

---

## 1. Hard blockers, do not publish without these

| # | What | Where | Why it matters |
|---|------|-------|----------------|
| 1 | **The four headline metrics** ("20+ years", "60+ audits", "9 frameworks", "100%") | `METRICS` | Invented. Replace with numbers you can defend, or delete the whole band, it's better to have no metrics than unverifiable ones. |
| 2 | **Three testimonials** | `TESTIMONIALS` | Invented quotes with invented attributions. Get real ones in writing, or delete the section. |
| 3 | **Three case studies** (SaaS SOC 2, CMMC manufacturer, health system IR) | `CASE_STUDIES` | Fictional engagements written to show the format. Replace with real work: anonymised is fine ("a 400-person defense supplier"), fabricated is not. |
| 4 | **Client logo strip** (Infosys, HCL, GalaxE, Cybersecon, HiQuest) | `CLIENT_LOGOS` | Carried over from your current site. Confirm each one is a client you can name and that you have permission. Naming a company you merely staffed into is a legal risk. |
| 5 | **Certification chips** on About | `build_about()` → `creds` | Currently a generic list (CISSP, CISM, CCSP, CISA, ISO 27001 LA/LI, CMMC RP, AWS/Azure Security, CIPP/E, GIAC, CRISC). Keep only what you or your team actually hold. |

## 2. Configuration, 10 minutes

All in the `SITE` dict at the top of `build.py`:

- `form_action`, currently `REPLACE_WITH_FORMSPREE_ENDPOINT`. Get a free
  endpoint from [Formspree](https://formspree.io) or [Basin](https://usebasin.com),
  or deploy on Netlify/Cloudflare Pages and use their built-in form handling.
  Until this is set, the form shows a fallback message rather than failing silently.
- `booking_url`, **done.** Points at your Outlook Bookings page (30 minutes with
  Raj Kumar). Every "Book a call" button on the site reads from this one value.
- `linkedin`, I guessed the company page URL. Confirm it.
- **Phone number removed** from the whole site at your request (the old one was
  wrong). If you want one back, add `phone_display` and `phone_href` to `SITE` and
  tell me, and I'll restore the footer row, the contact card and the schema entry.
- `email` and the office address are carried from your current site. Confirm they're
  still right.

## 3. Content decisions that need you

**Who is "we"?** The site currently says "we" throughout without naming anyone.
Both reference sites lean hard on a named principal, bdemerson.com is literally a
person's name, and ResilientTech leads with "26 years of expertise." Buyers of
security advisory are buying a specific person's judgment. Strongly recommend
adding a **Team / Principal section** to `about.html` with your photo, bio and
credentials. Send me a bio and headshot and I'll build it.

**Staff augmentation and AI services.** Per your answer, the site now leads with
security advisory only. Your current site sells staff augmentation and AI services.
Decide whether those:
  - disappear entirely (cleanest positioning),
  - live on as a single "Talent" page linked from the footer, or
  - stay as-is on a separate site.

**Years in business / founding date.** The About page says "Founded, Nila Pro
Services" as a placeholder. Give me a real year.

**Insights articles.** The three articles are mine, written in the house voice.
They're publishable as-is if you agree with the opinions in them: read them
first, because they take positions (e.g. that compliance automation platforms are
oversold). Put your name on them or attribute them to "NPS" as you prefer.

## 4. The logo: send me the vector

The logo now in the header, footer, favicon and social card came from the PNG you
sent: **123 × 76 pixels**. That is enough for the header at normal zoom, but it is
below what a favicon at 512px or a social-share card really needs, and it will look
soft on a high-DPI screen at larger sizes.

If your designer's original exists, `.ai`, `.eps`, `.svg` or `.pdf`, send it and
I'll regenerate every logo asset crisply at any size. A PNG at 1000px wide or more
would also do. Failing that, I can redraw it as clean vector, but that's a redraw,
not a reproduction.

Also worth deciding: the logo has a **white** element (the three person glyphs) that
only works on a dark or light background respectively. If you ever need it on white,
you'll want a second colorway. Ask your designer for a light-background and a
dark-background version.

## 5. Nice to have before launch

- **Replace `og.png`** if you change the tagline. It is a real image at `assets/img/og.png`.
- **Real photography**, both reference sites use team photos and office imagery.
  This design deliberately uses none, which keeps it clean, but a single good
  photo of you on the About page would do more for conversion than anything else
  on this list.
- **Analytics**: if you want any, use something privacy-preserving (Plausible,
  Fathom, Cloudflare Web Analytics). The site currently sets no cookies and makes
  no third-party requests at all, which means you need no cookie banner. Don't
  give that up for Google Analytics without deciding it's worth it.
- **Trust page**, a `/trust.html` describing your own security posture. Unusual
  for an advisory firm, and it would land well.
- **Legal review**, `privacy.html` and `terms.html` are templates. Have counsel
  read them.

## 6. What I'd do first if it were my site

1. Replace the case studies with two real ones. This is the single highest-value edit.
2. Add a named principal with a photo and a real bio.
3. Wire the booking link to a real calendar.
4. Delete the metrics band and the testimonials until you have real ones.

That gets you to publishable. Everything else is polish.
