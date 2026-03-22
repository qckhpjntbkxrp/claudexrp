// PromptRules — Template data for AI coding assistant rules generation
// Each template category contains rules, best practices, and configuration snippets

const TECH_STACKS = {
  react: {
    name: "React",
    icon: "⚛️",
    tags: ["frontend", "ui"],
    rules: {
      general: [
        "Use functional components with hooks. Never use class components.",
        "Prefer named exports over default exports for better refactoring support.",
        "Keep components small and focused — one component per file.",
        "Use TypeScript for all new files.",
        "Colocate tests next to the files they test (Component.test.tsx).",
      ],
      naming: [
        "Components: PascalCase (UserProfile.tsx)",
        "Hooks: camelCase with 'use' prefix (useAuth.ts)",
        "Utils/helpers: camelCase (formatDate.ts)",
        "Constants: UPPER_SNAKE_CASE",
        "Types/Interfaces: PascalCase with descriptive names (UserProfileProps)",
      ],
      patterns: [
        "Extract custom hooks for reusable stateful logic.",
        "Use React.memo() only when profiling shows a performance issue.",
        "Prefer composition over prop drilling — use context sparingly.",
        "Handle loading, error, and empty states explicitly in every data-fetching component.",
        "Use error boundaries at route-level and around third-party components.",
      ],
      avoid: [
        "Do not use index as key in lists unless the list is static and never reordered.",
        "Do not mutate state directly. Always use setState or dispatch.",
        "Avoid inline function definitions in JSX for event handlers in hot paths.",
        "Do not use any. Define proper types.",
        "Avoid deeply nested ternaries in JSX — extract to variables or early returns.",
      ],
    },
  },
  nextjs: {
    name: "Next.js",
    icon: "▲",
    tags: ["frontend", "fullstack", "ssr"],
    rules: {
      general: [
        "Use the App Router (app/) for all new routes.",
        "Prefer Server Components by default. Add 'use client' only when needed.",
        "Use TypeScript for all files.",
        "Place API routes in app/api/ using Route Handlers.",
        "Use next/image for all images. Never use raw <img> tags.",
      ],
      naming: [
        "Route files: page.tsx, layout.tsx, loading.tsx, error.tsx, not-found.tsx",
        "Components: PascalCase in src/components/",
        "Server actions: camelCase in src/actions/",
        "Utils: camelCase in src/lib/",
      ],
      patterns: [
        "Use Server Actions for form mutations instead of API routes.",
        "Implement loading.tsx and error.tsx at each route segment.",
        "Use generateMetadata() for dynamic SEO metadata.",
        "Prefer fetch() with Next.js caching over third-party HTTP clients.",
        "Use route groups (parentheses folders) to organize without affecting URL structure.",
      ],
      avoid: [
        "Do not use getServerSideProps or getStaticProps — these are Pages Router patterns.",
        "Do not use 'use client' at the top of every file — keep components server-side by default.",
        "Avoid large client-side bundles. Keep 'use client' boundaries as low in the tree as possible.",
        "Do not store secrets in NEXT_PUBLIC_ env vars.",
      ],
    },
  },
  python: {
    name: "Python",
    icon: "🐍",
    tags: ["backend", "scripting"],
    rules: {
      general: [
        "Follow PEP 8 style guidelines.",
        "Use type hints for all function signatures and return types.",
        "Use f-strings for string formatting (not .format() or %).",
        "Prefer pathlib.Path over os.path for file operations.",
        "Use dataclasses or Pydantic models for structured data.",
      ],
      naming: [
        "Functions/variables: snake_case",
        "Classes: PascalCase",
        "Constants: UPPER_SNAKE_CASE",
        "Private attributes: _leading_underscore",
        "Modules: short, lowercase, snake_case",
      ],
      patterns: [
        "Use context managers (with statements) for resource management.",
        "Prefer list/dict/set comprehensions over loops for simple transformations.",
        "Use logging module instead of print() for production code.",
        "Handle exceptions specifically — never use bare except:.",
        "Use virtual environments for every project.",
      ],
      avoid: [
        "Do not use mutable default arguments (def foo(bar=[])).",
        "Do not use wildcard imports (from module import *).",
        "Avoid global variables. Pass dependencies explicitly.",
        "Do not suppress exceptions silently (except: pass).",
        "Avoid deeply nested code — extract to functions at 3+ levels.",
      ],
    },
  },
  typescript: {
    name: "TypeScript",
    icon: "📘",
    tags: ["language"],
    rules: {
      general: [
        "Enable strict mode in tsconfig.json.",
        "Use type inference where the type is obvious. Add explicit types for function signatures.",
        "Prefer interfaces for object shapes, type aliases for unions/intersections.",
        "Use const assertions for literal types.",
        "Prefer unknown over any. Use any only as a last resort with a TODO comment.",
      ],
      naming: [
        "Interfaces/Types: PascalCase (UserProfile, ApiResponse)",
        "Enums: PascalCase with PascalCase members",
        "Generic type parameters: single uppercase letter or descriptive PascalCase (T, TResult)",
        "Files: camelCase or kebab-case consistently",
      ],
      patterns: [
        "Use discriminated unions for state modeling (type State = { status: 'loading' } | { status: 'success', data: T }).",
        "Prefer readonly properties and ReadonlyArray where mutation isn't needed.",
        "Use satisfies operator for type-safe object literals with inference.",
        "Extract shared types to a types/ directory.",
        "Use Zod or similar for runtime validation at system boundaries.",
      ],
      avoid: [
        "Do not use any. If you must, add a // TODO: type this properly comment.",
        "Do not use non-null assertion (!) unless you can prove the value exists.",
        "Avoid enums for simple string unions — use 'type Status = \"active\" | \"inactive\"' instead.",
        "Do not use @ts-ignore. Use @ts-expect-error with an explanation if absolutely necessary.",
      ],
    },
  },
  node: {
    name: "Node.js",
    icon: "🟢",
    tags: ["backend", "runtime"],
    rules: {
      general: [
        "Use ESM (import/export) over CommonJS (require).",
        "Use async/await for all asynchronous operations.",
        "Handle all promise rejections — use process.on('unhandledRejection').",
        "Use environment variables for configuration via process.env.",
        "Use a .env file with dotenv for local development only.",
      ],
      naming: [
        "Files: kebab-case (user-service.ts)",
        "Functions: camelCase",
        "Classes: PascalCase",
        "Environment variables: UPPER_SNAKE_CASE",
      ],
      patterns: [
        "Structure projects by feature/domain, not by technical layer.",
        "Use middleware patterns for cross-cutting concerns.",
        "Validate all input at the API boundary using Zod or Joi.",
        "Use structured logging (JSON format) in production.",
        "Implement graceful shutdown handlers for SIGTERM/SIGINT.",
      ],
      avoid: [
        "Do not use callbacks — convert to promises with util.promisify if needed.",
        "Do not use synchronous file operations in request handlers.",
        "Avoid storing state in module-level variables in serverless environments.",
        "Do not commit .env files or node_modules/.",
      ],
    },
  },
  tailwind: {
    name: "Tailwind CSS",
    icon: "🎨",
    tags: ["css", "styling"],
    rules: {
      general: [
        "Use Tailwind utility classes instead of custom CSS.",
        "Extract repeated class combinations into components, not @apply directives.",
        "Use the official Tailwind prettier plugin for class sorting.",
        "Configure your design system in tailwind.config.js (colors, spacing, fonts).",
      ],
      patterns: [
        "Use cn() or clsx() for conditional class merging.",
        "Prefer responsive variants (sm:, md:, lg:) over media queries.",
        "Use dark: variant for dark mode support.",
        "Group related utilities: layout → spacing → sizing → typography → colors → effects.",
      ],
      avoid: [
        "Do not use @apply extensively — it defeats the purpose of utility-first CSS.",
        "Do not use arbitrary values ([32px]) when a design token exists.",
        "Avoid !important — restructure your class order instead.",
      ],
    },
  },
  vue: {
    name: "Vue.js",
    icon: "💚",
    tags: ["frontend", "ui"],
    rules: {
      general: [
        "Use Composition API with <script setup> for all new components.",
        "Use TypeScript for type safety.",
        "Keep components small and focused.",
        "Use Pinia for state management.",
      ],
      naming: [
        "Components: PascalCase (UserProfile.vue)",
        "Composables: camelCase with 'use' prefix (useAuth.ts)",
        "Props/emits: camelCase in JS, kebab-case in templates",
        "Events: kebab-case (update:modelValue)",
      ],
      patterns: [
        "Use composables for reusable stateful logic.",
        "Prefer provide/inject over deep prop drilling.",
        "Use v-model with defineModel() for two-way binding.",
        "Implement Suspense with async setup for data loading.",
      ],
      avoid: [
        "Do not use Options API for new components.",
        "Do not mutate props directly.",
        "Avoid mixins — use composables instead.",
        "Do not use this in <script setup>.",
      ],
    },
  },
  go: {
    name: "Go",
    icon: "🔵",
    tags: ["backend", "systems"],
    rules: {
      general: [
        "Follow standard Go project layout.",
        "Use gofmt and go vet on all code.",
        "Handle every error explicitly. Never use _ for errors.",
        "Write table-driven tests.",
        "Use context.Context for cancellation and timeouts.",
      ],
      naming: [
        "Packages: short, lowercase, single word (user, auth, http)",
        "Interfaces: -er suffix for single-method (Reader, Writer)",
        "Exported: PascalCase. Unexported: camelCase.",
        "Acronyms: all caps (HTTP, URL, ID) — not Http, Url, Id",
      ],
      patterns: [
        "Accept interfaces, return structs.",
        "Use functional options for configurable constructors.",
        "Prefer errors.Is/errors.As over type assertions for error checking.",
        "Use goroutines with proper synchronization (channels, sync.WaitGroup, sync.Mutex).",
        "Structure: cmd/ for entry points, internal/ for private packages, pkg/ for public libraries.",
      ],
      avoid: [
        "Do not use init() functions unless absolutely necessary.",
        "Do not use panic for normal error handling.",
        "Avoid package-level variables — pass dependencies explicitly.",
        "Do not use dot imports.",
      ],
    },
  },
  rust: {
    name: "Rust",
    icon: "🦀",
    tags: ["systems", "backend"],
    rules: {
      general: [
        "Run cargo clippy with all warnings before committing.",
        "Use Result<T, E> for fallible operations. Reserve panic! for truly unrecoverable errors.",
        "Prefer &str over String for function parameters.",
        "Use derive macros for common trait implementations.",
        "Write doc comments (///) for all public items.",
      ],
      naming: [
        "Types/Traits: PascalCase",
        "Functions/variables: snake_case",
        "Constants: UPPER_SNAKE_CASE",
        "Modules: snake_case",
        "Crates: kebab-case (in Cargo.toml) / snake_case (in code)",
      ],
      patterns: [
        "Use the ? operator for error propagation.",
        "Prefer iterators and combinators over manual loops.",
        "Use thiserror for library errors, anyhow for application errors.",
        "Use Builder pattern for complex struct construction.",
      ],
      avoid: [
        "Do not use unwrap() in production code. Use expect() with a message or proper error handling.",
        "Avoid clone() to satisfy the borrow checker — restructure ownership instead.",
        "Do not use unsafe without a // SAFETY: comment explaining the invariants.",
      ],
    },
  },
  django: {
    name: "Django",
    icon: "🎸",
    tags: ["backend", "fullstack", "python"],
    rules: {
      general: [
        "Follow Django's MTV (Model-Template-View) pattern.",
        "Use class-based views for complex logic, function-based views for simple endpoints.",
        "Run migrations before deploying. Never edit migration files manually.",
        "Use Django REST Framework for API endpoints.",
        "Keep settings modular (base.py, development.py, production.py).",
      ],
      patterns: [
        "Use select_related() and prefetch_related() to avoid N+1 queries.",
        "Validate data in serializers/forms, not in views.",
        "Use Django signals sparingly — prefer explicit method calls.",
        "Use django-environ or similar for environment variable management.",
      ],
      avoid: [
        "Do not use raw SQL unless ORM cannot express the query.",
        "Do not store secrets in settings.py. Use environment variables.",
        "Avoid fat views — push logic into models or service layers.",
        "Do not disable CSRF protection.",
      ],
    },
  },
  rails: {
    name: "Ruby on Rails",
    icon: "💎",
    tags: ["backend", "fullstack"],
    rules: {
      general: [
        "Follow Rails conventions. Convention over configuration.",
        "Use the latest stable Rails version features.",
        "Keep controllers thin. Push logic to models or service objects.",
        "Use Strong Parameters for mass assignment protection.",
        "Write model validations for all user input.",
      ],
      patterns: [
        "Use scopes for reusable query logic.",
        "Use concerns for shared model behavior.",
        "Prefer ActiveRecord callbacks sparingly — use service objects for complex operations.",
        "Use background jobs (Sidekiq/Good Job) for slow operations.",
      ],
      avoid: [
        "Do not use raw SQL unless ActiveRecord cannot express the query.",
        "Avoid N+1 queries — use includes/eager_load/preload.",
        "Do not skip validations (save(validate: false)) in production code.",
        "Do not use dynamic finders (find_by_name) — use find_by(name:).",
      ],
    },
  },
  svelte: {
    name: "Svelte/SvelteKit",
    icon: "🔥",
    tags: ["frontend", "fullstack"],
    rules: {
      general: [
        "Use SvelteKit for full applications, Svelte for component libraries.",
        "Use TypeScript with lang='ts' in script blocks.",
        "Prefer $state, $derived, and $effect runes (Svelte 5+).",
        "Use +page.ts for data loading, +page.server.ts for server-only logic.",
      ],
      patterns: [
        "Use form actions for mutations instead of API endpoints.",
        "Implement progressive enhancement with use:enhance on forms.",
        "Use snippets for reusable template logic.",
        "Prefer stores for shared state across components.",
      ],
      avoid: [
        "Do not use $: reactive statements (Svelte 4 syntax) in new code — use runes.",
        "Do not fetch data in onMount — use load functions.",
        "Avoid complex logic in templates — extract to functions.",
      ],
    },
  },
};

const CODING_STYLES = {
  concise: {
    name: "Concise",
    description: "Minimal code, minimal comments. Let the code speak.",
    rules: [
      "Write minimal, self-documenting code. If it needs a comment, consider renaming.",
      "Prefer one-liners and short functions. If a function exceeds 20 lines, split it.",
      "No boilerplate comments (file headers, section dividers, obvious descriptions).",
      "Use short but meaningful variable names. Avoid single-letter names except in lambdas/loops.",
      "Remove dead code immediately. Do not comment it out.",
    ],
  },
  documented: {
    name: "Well-Documented",
    description: "Thorough comments and documentation for team readability.",
    rules: [
      "Add JSDoc/docstring comments to all exported functions with @param and @returns.",
      "Document non-obvious business logic with inline comments explaining WHY, not WHAT.",
      "Keep a clear file-level comment explaining the module's purpose.",
      "Document all environment variables, config options, and their valid values.",
      "Add TODO comments with issue tracker links for known technical debt.",
    ],
  },
  defensive: {
    name: "Defensive",
    description: "Guard clauses, validation, and explicit error handling everywhere.",
    rules: [
      "Validate all inputs at function boundaries. Fail fast with descriptive errors.",
      "Use guard clauses (early returns) instead of nested if/else blocks.",
      "Never trust external data — validate and sanitize at every system boundary.",
      "Use typed errors/exceptions with context. Never throw generic Error('something went wrong').",
      "Log errors with full context (function name, inputs, stack trace). Never swallow errors silently.",
    ],
  },
  functional: {
    name: "Functional",
    description: "Immutable data, pure functions, composition over mutation.",
    rules: [
      "Prefer pure functions. Given the same input, always return the same output.",
      "Avoid mutation. Use spread operators, Object.freeze, or immutable data structures.",
      "Use map/filter/reduce over for loops.",
      "Compose small functions into larger operations using pipes or function composition.",
      "Separate side effects (I/O, network, DOM) from pure business logic.",
    ],
  },
  pragmatic: {
    name: "Pragmatic",
    description: "Balance between clean code and getting things done.",
    rules: [
      "Optimize for readability and maintainability, not cleverness.",
      "Follow existing patterns in the codebase. Consistency over personal preference.",
      "Add comments only where the code is genuinely non-obvious.",
      "Use the simplest solution that works correctly. Avoid premature abstraction.",
      "Refactor when you touch code, but don't gold-plate. Good enough is good enough.",
    ],
  },
};

const PROJECT_TYPES = {
  webapp: {
    name: "Web Application",
    rules: [
      "Implement authentication and authorization before any other feature.",
      "Use HTTPS everywhere. Set secure cookie flags.",
      "Sanitize all user input to prevent XSS.",
      "Use parameterized queries to prevent SQL injection.",
      "Implement rate limiting on all public endpoints.",
      "Add CORS headers appropriate to your deployment.",
    ],
  },
  api: {
    name: "REST API",
    rules: [
      "Use consistent URL naming: plural nouns, kebab-case (/api/user-profiles).",
      "Return appropriate HTTP status codes (201 Created, 404 Not Found, 422 Unprocessable Entity).",
      "Version your API in the URL (/api/v1/) or headers.",
      "Implement pagination for list endpoints with consistent cursor/offset format.",
      "Return standardized error responses: { error: { code, message, details } }.",
      "Document all endpoints with OpenAPI/Swagger.",
    ],
  },
  cli: {
    name: "CLI Tool",
    rules: [
      "Use a CLI framework (Commander, Click, Cobra) for argument parsing.",
      "Provide --help with clear descriptions and examples for every command.",
      "Use exit codes: 0 for success, 1 for general errors, 2 for usage errors.",
      "Support --json output for machine consumption alongside human-readable output.",
      "Support --quiet and --verbose flags for output control.",
      "Use stderr for errors and progress, stdout for data output.",
    ],
  },
  library: {
    name: "Library / Package",
    rules: [
      "Write comprehensive README with installation, quick start, and API reference.",
      "Export a clean, minimal public API. Keep internals private.",
      "Follow semantic versioning strictly.",
      "Include TypeScript declarations (or type stubs for Python).",
      "Write unit tests for every public API method.",
      "Minimize dependencies. Each dependency is a liability.",
    ],
  },
  mobile: {
    name: "Mobile App",
    rules: [
      "Handle offline state gracefully with local caching.",
      "Implement proper loading states for all network operations.",
      "Follow platform-specific design guidelines (HIG for iOS, Material for Android).",
      "Optimize for battery life — minimize background work and network calls.",
      "Handle all permission requests with clear explanations of WHY.",
      "Test on real devices, not just simulators.",
    ],
  },
};

const AI_BEHAVIORS = {
  concise_responses: {
    name: "Concise Responses",
    description: "Short, direct answers without filler",
    rules: [
      "Keep responses short and focused. Answer the question, then stop.",
      "Do not repeat the question or restate what I said.",
      "Skip preamble like 'Sure!' or 'Great question!'",
      "When showing code changes, show only the changed lines with minimal context.",
      "If the answer is a single line of code, just show that line.",
    ],
  },
  thorough_responses: {
    name: "Thorough Responses",
    description: "Detailed explanations with context and alternatives",
    rules: [
      "Explain your reasoning before showing code changes.",
      "Show the full file context when making changes, not just the diff.",
      "Mention alternative approaches and why you chose this one.",
      "Include edge cases and potential issues in your explanation.",
      "Add inline comments explaining non-obvious changes.",
    ],
  },
  minimal_changes: {
    name: "Minimal Changes",
    description: "Touch as little code as possible",
    rules: [
      "Make the smallest possible change to achieve the goal.",
      "Do not refactor surrounding code unless explicitly asked.",
      "Do not add types, comments, or tests unless explicitly asked.",
      "Do not change formatting or style of untouched code.",
      "If asked to fix a bug, fix only that bug. Do not improve nearby code.",
    ],
  },
  proactive: {
    name: "Proactive",
    description: "Anticipate needs and suggest improvements",
    rules: [
      "After completing a task, suggest related improvements or potential issues.",
      "Add tests for any new or changed functionality.",
      "Update related documentation when changing code.",
      "Fix obvious code smells when you encounter them, even if not asked.",
      "Suggest better patterns when you see anti-patterns in existing code.",
    ],
  },
  test_driven: {
    name: "Test-Driven",
    description: "Write tests first, then implementation",
    rules: [
      "Before writing any implementation, write a failing test that describes the expected behavior.",
      "Run the test to confirm it fails for the right reason.",
      "Write the minimal implementation to make the test pass.",
      "Refactor while keeping tests green.",
      "Every bug fix must include a regression test.",
    ],
  },
};

// Export for use in the main app
if (typeof module !== "undefined") {
  module.exports = {
    TECH_STACKS,
    CODING_STYLES,
    PROJECT_TYPES,
    AI_BEHAVIORS,
  };
}
