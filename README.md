# NPS, Nila Pro Services

Marketing site for NPS, a cybersecurity advisory practice. Plain static
HTML/CSS/JS: no framework, no runtime dependencies, no build step required
to deploy.

Live target: <https://nilaproservices.com>

---

## What's in here

```
.
├── build.py                 # site generator, all content lives here
├── index.html               # ← generated
├── services.html            # ← generated
├── services/*.html          # ← generated (8 service pages)
├── case-studies/*.html      # ← generated
├── insights/*.html          # ← generated
├── about.html contact.html industries.html privacy.html terms.html 404.html
├── sitemap.xml robots.txt .nojekyll
└── assets/
    ├── css/site.css         # the entire design system (hand-written)
    ├── js/site.js           # ~90 lines, no dependencies
    ├── fonts/*.woff2        # self-hosted, zero third-party requests
    └── img/                 # favicon.svg, og.svg, og.png
```

## Editing content

**All copy, services, case studies and articles live in `build.py`.** Change
them there and regenerate:

```bash
python3 build.py
```

That rewrites every `.html` file. Requires Python 3.8+ and nothing else.

Why a generator? The header, nav, footer and CTA band are identical on 24
pages. Adding a service is one dict entry rather than one new file plus 23
navigation edits. The *output* is still plain static HTML, if you'd rather
hand-edit the generated files and stop using the generator, nothing breaks.

**Design changes** go in `assets/css/site.css` directly (it isn't generated).

## Preview locally

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

Use a server, not `file://`, the site uses root-relative paths (`/assets/...`).

## Deploying

### GitHub Pages (included)

`.github/workflows/pages.yml` publishes the repo root on every push to `main`.
In the repo: **Settings → Pages → Source: GitHub Actions**.

All internal links are **path-relative**, so the site works unchanged at
`https://sahasraja.github.io/NPS/` *and* at `https://nilaproservices.com/`.
Nothing to configure when you switch between them.

#### Attaching the custom domain later

The `CNAME` file is parked as `CNAME.txt` so it doesn't hijack the
`github.io` test URL. When you're ready to go live, either rename it back to
`CNAME` and push, or just set the domain in **Settings → Pages → Custom
domain** (GitHub writes the file for you). Then at your DNS provider:

| Type  | Name | Value                    |
|-------|------|--------------------------|
| A     | @    | 185.199.108.153          |
| A     | @    | 185.199.109.153          |
| A     | @    | 185.199.110.153          |
| A     | @    | 185.199.111.153          |
| CNAME | www  | `sahasraja.github.io.`   |

Then tick **Enforce HTTPS** in Settings → Pages.

### Cloudflare Pages / Netlify (recommended alternative)

Both give you a form handler, better analytics and instant rollbacks:

- Build command: `python3 build.py` (or leave blank, the HTML is committed)
- Output directory: `/` (repo root)

## Before launch, required

See **`CONTENT-TODO.md`**. Short version: every number, testimonial, client
name and case study currently on the site is placeholder scaffolding written
to demonstrate the structure. Replace them.

Also wire up:

1. **Contact form**, set `SITE["form_action"]` in `build.py` to a Formspree,
   Basin or Netlify Forms endpoint. Until then the form shows a fallback
   message with the phone number instead of silently failing.
2. **Booking link**, set `SITE["booking_url"]` to your Calendly / Reclaim /
   Cal.com URL. Currently points at `/contact.html`.
3. **LinkedIn URL**, confirm `SITE["linkedin"]`.

## Notes

- No cookies, no trackers, no third-party font or script requests. Appropriate
  for a security firm and it removes the need for a cookie banner.
- Fonts are Bricolage Grotesque (headings), Manrope (body) and JetBrains Mono
  (small caps labels), all SIL Open Font License 1.1, free for commercial use,
  self-hosted as latin-subset woff2. 124 KB total, no third-party requests.
  The first two are variable fonts, so one file covers weights 200–800.
- `og.png` is generated from `assets/img/og.svg`. Re-render it if you change
  the tagline.
- Accessibility: skip link, visible focus rings, `prefers-reduced-motion`
  respected, one `<h1>` per page, semantic landmarks.
