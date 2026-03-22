# PromptRules — Next Steps

## Immediate (Human Action Required)

### 1. Domain & Deployment
- [ ] Purchase domain: `promptrules.dev` (~$12/year on Namecheap/Cloudflare)
- [ ] Deploy to Vercel: `vercel --prod` from `/product/` directory
- [ ] Or deploy to Cloudflare Pages: connect GitHub repo, set build output to `/product/`
- [ ] Configure custom domain in hosting dashboard

### 2. Payment Setup
- [ ] Create LemonSqueezy account (free)
- [ ] Create product: "PromptRules Pro" — $12 one-time
- [ ] Get checkout link and replace placeholder in `index.html` buy button
- [ ] Test purchase flow end-to-end

### 3. GitHub Repository
- [ ] Create public repo: `github.com/promptrules/promptrules`
- [ ] Push code
- [ ] Add topics: `ai`, `developer-tools`, `claude-code`, `cursor`, `copilot`, `windsurf`
- [ ] Pin repo to GitHub profile

### 4. Launch Sequence (recommended order)
- [ ] **Day 1 AM:** Post on Twitter/X (thread from LAUNCH_KIT.md)
- [ ] **Day 1 PM:** Submit to Hacker News ("Show HN" post)
- [ ] **Day 2:** Post on r/ClaudeAI and r/CursorAI
- [ ] **Day 3:** Post on r/webdev
- [ ] **Day 4:** Launch on Product Hunt (Tuesday-Thursday is best)
- [ ] **Day 5:** Publish DEV.to / Hashnode article

---

## Short-Term (Week 1-2)

### 5. Product Improvements
- [ ] Add more tech stacks: Flutter, SwiftUI, Kotlin, .NET/C#, PHP/Laravel, Elixir
- [ ] Add "All-in-one" export (ZIP with all 4 format files)
- [ ] Add URL sharing (encode config in URL params so configs are shareable)
- [ ] Add "Popular Combos" section showing most-used stack combinations
- [ ] Implement actual Pro checkout flow via LemonSqueezy

### 6. SEO
- [ ] Create `/templates/[stack]` pages for each tech stack (auto-generated)
- [ ] Create comparison pages: "CLAUDE.md vs .cursorrules — what's the difference?"
- [ ] Submit sitemap to Google Search Console
- [ ] Write a blog post targeting "how to write CLAUDE.md"

### 7. Analytics
- [ ] Add Plausible or Fathom analytics (privacy-respecting)
- [ ] Track: page views, format selections, stack selections, copy/download clicks, Pro clicks

---

## Medium-Term (Month 1-3)

### 8. Feature Expansion
- [ ] Team presets: save and share configs with a team link
- [ ] API endpoint: `GET /api/generate?stacks=react,typescript&style=concise&format=claude`
- [ ] VS Code extension: generate rules from command palette
- [ ] CLI tool: `npx promptrules init` to generate config interactively
- [ ] Import existing rules: paste your current .cursorrules and PromptRules will analyze and improve them

### 9. Community
- [ ] Accept community-contributed rule templates via GitHub PRs
- [ ] Create a Discord for AI coding tool discussions
- [ ] Feature community-submitted "real world" configs

### 10. Content Marketing
- [ ] Weekly "Stack Spotlight" posts comparing AI tool output with/without rules
- [ ] Create video demos showing before/after code quality
- [ ] Guest post on AI-focused dev blogs

---

## Long-Term (Month 3+)

### 11. Enterprise
- [ ] Team tier ($49 one-time): shared configs, custom presets
- [ ] Enterprise tier ($199/yr): SSO, central management, API access
- [ ] Template marketplace: community-created templates, 70/30 revenue split

### 12. Platform Expansion
- [ ] Support new AI coding tools as they launch
- [ ] Build integrations with existing dev tools (ESLint, Prettier config import)
- [ ] Explore AI-powered rule suggestions based on codebase analysis
