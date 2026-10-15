"""
Backend Technical Learning Roadmap & Curriculum Engine — Component 1
IT22089236 | D T D Perera | R26-IT-148

Generates structured, skill-gap-specific learning roadmaps with syllabus concepts,
practical portfolio projects, estimated study hours, and official documentation links
directly on the backend.
"""

from typing import Any, Dict, List, Optional
import urllib.parse

SKILL_CURRICULUM_CATALOG: Dict[str, Dict[str, Any]] = {
    "typescript": {
        "title": "TypeScript for Enterprise Web Development",
        "description": "Master strict typing, generics, discriminating unions, utility types, and advanced compiler configurations for scalable, maintainable architectures.",
        "key_topics": ["Generics & Type Constraints", "Discriminated Unions", "Utility Types (Pick, Omit, Partial)", "Type Guards & Narrowing", "Strict Compiler Modes"],
        "project": "Migrate a vanilla JavaScript stateful application to strict TypeScript with 100% type safety and type-safe API client interfaces.",
        "est_hours": "14 Hours",
        "level": "Intermediate Architecture",
        "docs_url": "https://www.typescriptlang.org/docs/handbook/intro.html"
    },
    "web performance": {
        "title": "Web Performance Engineering & Core Web Vitals",
        "description": "Optimize rendering cycles, minimize bundle sizes, eliminate layout shifts, and accelerate Largest Contentful Paint (LCP) and Interaction to Next Paint (INP).",
        "key_topics": ["Lighthouse 100 Auditing", "Core Web Vitals (LCP, CLS, INP)", "Dynamic Code-Splitting & Lazy Loading", "Tree-shaking & Asset Optimization", "Memoization & Virtualization"],
        "project": "Audit a complex single-page dashboard and implement code splitting, image optimization, and memoization to achieve 95+ Lighthouse score.",
        "est_hours": "12 Hours",
        "level": "Advanced Performance",
        "docs_url": "https://web.dev/learn/performance"
    },
    "accessibility": {
        "title": "Accessibility (a11y) & WCAG 2.1 Compliance",
        "description": "Build inclusive, high-contrast, fully keyboard-navigable and screen-reader accessible web applications conforming to WCAG 2.1 AA standards.",
        "key_topics": ["Semantic HTML5 Architecture", "WAI-ARIA Roles & Live Regions", "Keyboard Navigation & Focus Traps", "Color Contrast Validation", "Screen Reader (NVDA/VoiceOver) Auditing"],
        "project": "Refactor an interactive multi-step modal dialog and complex data table to pass full axe-core automated audit and NVDA screen reader testing.",
        "est_hours": "10 Hours",
        "level": "Core Production Requirement",
        "docs_url": "https://developer.mozilla.org/en-US/docs/Web/Accessibility"
    },
    "vue.js": {
        "title": "Vue.js 3 & Composition API Architecture",
        "description": "Develop reactive applications using Vue 3 Composition API, script setup syntax, Pinia state stores, and Vue Router with type-safe composables.",
        "key_topics": ["Composition API & setup syntax", "Reactivity Core (ref, reactive, computed)", "Pinia Store Management", "Custom Reusable Composables", "Vue Router Guards & Transitions"],
        "project": "Build a modular e-commerce catalog with reactive shopping cart, filtering composables, and Pinia persistent state storage.",
        "est_hours": "16 Hours",
        "level": "Intermediate Framework",
        "docs_url": "https://vuejs.org/guide/introduction.html"
    },
    "vue": {
        "title": "Vue.js 3 & Composition API Architecture",
        "description": "Develop reactive applications using Vue 3 Composition API, script setup syntax, Pinia state stores, and Vue Router with type-safe composables.",
        "key_topics": ["Composition API & setup syntax", "Reactivity Core (ref, reactive, computed)", "Pinia Store Management", "Custom Reusable Composables", "Vue Router Guards & Transitions"],
        "project": "Build a modular e-commerce catalog with reactive shopping cart, filtering composables, and Pinia persistent state storage.",
        "est_hours": "16 Hours",
        "level": "Intermediate Framework",
        "docs_url": "https://vuejs.org/guide/introduction.html"
    },
    "zustand": {
        "title": "Zustand State Management & Store Slices",
        "description": "Implement lightweight, boilerplate-free state management in React using Zustand store slices, transient updates, and persistent middleware.",
        "key_topics": ["Store Slices Design Pattern", "Transient Updates & Reactive Selectors", "Immer Middleware Integration", "Local Storage Persistence", "Redux DevTools Debugging"],
        "project": "Construct an interactive kanban board application with drag-and-drop state, undo/redo history, and persistent Zustand slice store.",
        "est_hours": "8 Hours",
        "level": "Architecture & State",
        "docs_url": "https://zustand.docs.pmnd.rs/"
    },
    "styled-components": {
        "title": "Styled-Components & Modern CSS-in-JS",
        "description": "Design component-scoped styling systems with dynamic theme tokens, prop-driven variants, global styles, and zero class-name collisions.",
        "key_topics": ["Theme Context & Dynamic Tokens", "Prop-Based Dynamic Styling", "GlobalStyles & Keyframes Animations", "Polymorphic as Prop", "Server-Side Style Extraction"],
        "project": "Create a reusable design system component library with Dark/Light theme switching and accessible interactive states.",
        "est_hours": "8 Hours",
        "level": "Component Styling",
        "docs_url": "https://styled-components.com/docs"
    },
    "react": {
        "title": "Advanced React 18+ Architecture & Patterns",
        "description": "Master custom hook composition, concurrent rendering features, context separation, server components, and performance profiling.",
        "key_topics": ["Custom Hook Design", "useTransition & useDeferredValue", "Context Optimization", "ErrorBoundary & Suspense", "Compound Components Pattern"],
        "project": "Build an enterprise analytics dashboard with suspense data-fetching boundaries and custom hook query abstractions.",
        "est_hours": "18 Hours",
        "level": "Core Framework Mastery",
        "docs_url": "https://react.dev/reference/react"
    },
    "next.js": {
        "title": "Next.js App Router & Full-Stack React",
        "description": "Build high-performance web applications using the Next.js App Router, Server Actions, incremental static regeneration (ISR), and SEO optimization.",
        "key_topics": ["Server vs Client Components", "Server Actions & Mutations", "Route Handlers & Edge Middleware", "Streaming SSR & Suspense", "SEO & Dynamic Metadata API"],
        "project": "Deploy a full-stack content publishing platform with Server Actions for data mutation and on-demand ISR caching.",
        "est_hours": "20 Hours",
        "level": "Full-Stack Architecture",
        "docs_url": "https://nextjs.org/docs"
    },
    "docker": {
        "title": "Docker Containerization & Multi-Stage Builds",
        "description": "Containerize microservices with multi-stage Dockerfiles, minimal base images, security best practices, and Docker Compose orchestration.",
        "key_topics": ["Multi-Stage Dockerfiles", "Alpine & Distroless Base Images", "Volume Mounting & Networking", "Compose Multi-Container Stacks", "Image Size Minimization"],
        "project": "Containerize a full-stack React + FastAPI + PostgreSQL application stack with automated health checks and hot-reload dev containers.",
        "est_hours": "14 Hours",
        "level": "DevOps & Tooling",
        "docs_url": "https://docs.docker.com/get-started/"
    },
    "rest apis": {
        "title": "RESTful API Design & OpenAPI Architecture",
        "description": "Design idempotent, versioned, secure REST APIs adhering to HTTP specifications, JSON:API standards, and comprehensive OpenAPI documentation.",
        "key_topics": ["HTTP Status Codes & Verbs", "Pagination, Filtering, Sorting", "OAuth2 / JWT Authentication", "Rate Limiting & Caching (ETags)", "OpenAPI/Swagger Spec"],
        "project": "Implement a production-ready REST API with JWT authentication, cursor pagination, structured error envelopes, and automated Swagger docs.",
        "est_hours": "12 Hours",
        "level": "Backend Architecture",
        "docs_url": "https://restfulapi.net/"
    },
    "graphql": {
        "title": "GraphQL Schema Design & Federation",
        "description": "Design flexible schemas with type-safe queries, mutations, subscriptions, resolver batching (DataLoader), and client-side cache normalization.",
        "key_topics": ["Schema Definition Language (SDL)", "Resolvers & Execution Context", "N+1 Problem & DataLoader", "Apollo Client Cache Normalization", "Subscriptions (WebSockets)"],
        "project": "Build a real-time notification and feed API with Apollo Server, DataLoader query batching, and WebSocket subscription support.",
        "est_hours": "15 Hours",
        "level": "API Architecture",
        "docs_url": "https://graphql.org/learn/"
    },
    "ci/cd": {
        "title": "CI/CD Pipelines & Automated Deployment",
        "description": "Design automated testing, static analysis, security scanning, container builds, and zero-downtime deployment pipelines using GitHub Actions.",
        "key_topics": ["GitHub Actions Workflows", "Automated Test Matrix", "Docker Build & Push Actions", "Secret Management & Environments", "Zero-Downtime Rollouts"],
        "project": "Build an end-to-end GitHub Actions pipeline with automated linting, unit test coverage gates, and automated deployment to staging.",
        "est_hours": "12 Hours",
        "level": "DevOps & Automation",
        "docs_url": "https://docs.github.com/en/actions"
    }
}


def build_backend_learning_roadmap(
    missing_skills: List[str],
    target_role: str = "Software Engineer",
    max_items: int = 6
) -> List[Dict[str, Any]]:
    """Construct a high-accuracy, structured learning curriculum on the backend."""
    try:
        from ml.extractor import SKILL_ALIASES
    except Exception:
        SKILL_ALIASES = {}
    
    if not missing_skills:
        missing_skills = ["System Design", "Cloud Infrastructure", "Automated CI/CD", "Security Hardening"]

    curriculum = []
    seen = set()
    
    for idx, raw_skill in enumerate(missing_skills[:max_items]):
        clean_skill = str(raw_skill).strip()
        if not clean_skill:
            continue
        c_lower = clean_skill.lower()
        c_name = SKILL_ALIASES.get(c_lower, clean_skill.title())
        if c_lower in seen:
            continue
        seen.add(c_lower)

        is_critical = idx == 0 or idx == 1
        is_high = idx == 2

        meta = None
        for k, v in SKILL_CURRICULUM_CATALOG.items():
            if k == c_lower or k in c_lower or c_lower in k:
                meta = v
                break

        if meta:
            title = meta["title"]
            desc = meta["description"]
            key_topics = meta["key_topics"]
            project = meta["project"]
            est_hours = meta["est_hours"]
            level = meta["level"]
            docs_url = meta["docs_url"]
        else:
            title = f"{c_name} Enterprise Engineering & Architecture"
            desc = f"Master enterprise principles, architectural patterns, and production standards for {c_name} in {target_role} environments."
            key_topics = [f"{c_name} Core Fundamentals", "Architecture & Clean Patterns", "Performance Optimization", "Automated Testing & Deployment"]
            project = f"Construct a production-grade module demonstrating practical implementation of {c_name} with automated tests."
            est_hours = "12-15 Hours"
            level = "Foundational Core" if is_critical else "Intermediate Architecture"
            docs_url = f"https://developer.mozilla.org/en-US/search?q={urllib.parse.quote(c_name)}"

        curriculum.append({
            "step": len(curriculum) + 1,
            "skill": c_name,
            "title": title,
            "description": desc,
            "priority": "Critical" if is_critical else ("High" if is_high else "Medium"),
            "level": level,
            "est_hours": est_hours,
            "key_topics": key_topics,
            "project": project,
            "docs_url": docs_url,
            "target_role": target_role
        })

    return curriculum
