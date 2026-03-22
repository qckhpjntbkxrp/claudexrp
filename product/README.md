# ⚡ PromptRules

**Generate optimized AI coding rules for Claude Code, Cursor, Copilot & Windsurf — in seconds.**

Stop getting sloppy AI code. PromptRules generates tailored rules files based on your tech stack, coding style, and project type.

## Supported AI Tools

| Tool | Output File | Status |
|------|------------|--------|
| Claude Code | `CLAUDE.md` | ✅ Supported |
| Cursor | `.cursorrules` | ✅ Supported |
| GitHub Copilot | `.github/copilot-instructions.md` | ✅ Supported |
| Windsurf | `.windsurfrules` | ✅ Supported |

## Tech Stacks

React, Next.js, Vue.js, Svelte/SvelteKit, TypeScript, Node.js, Python, Django, Ruby on Rails, Go, Rust, Tailwind CSS — and growing.

## How It Works

1. **Pick your tech stack** (up to 3)
2. **Choose coding style** — Concise, Well-Documented, Defensive, Functional, or Pragmatic
3. **Select project type** — Web App, REST API, CLI Tool, Library, or Mobile App
4. **Set AI behavior** — Concise, Thorough, Minimal Changes, Proactive, or Test-Driven
5. **Copy or download** your generated rules file

That's it. 10 seconds to better AI code.

## Why PromptRules?

Most developers don't configure their AI coding assistant. The result:
- Inconsistent code style across the codebase
- Wrong patterns and anti-patterns in generated code
- Constant manual corrections eating into productivity
- Different AI tools producing conflicting output

PromptRules solves this by generating battle-tested rules based on community best practices — not generic boilerplate.

## Run Locally

No build step required. Just open the file:

```bash
# Clone the repo
git clone https://github.com/promptrules/promptrules.git
cd promptrules

# Open in browser
open index.html
# or
python3 -m http.server 8000
```

## Deploy

Works on any static hosting:

```bash
# Vercel
vercel --prod

# Netlify
netlify deploy --prod --dir=.

# GitHub Pages
# Just enable Pages in your repo settings
```

## Pro ($12 one-time)

- Generate for **all 4 AI tools** at once
- Export as ZIP with all config files
- Attribution-free output
- Premium templates (team presets, enterprise configs)
- Lifetime updates

## Contributing

PRs welcome! To add a new tech stack or improve existing rules:

1. Edit `templates/rules-data.js`
2. Follow the existing structure (general, naming, patterns, avoid)
3. Submit a PR with a description of what you added/changed

## License

MIT
