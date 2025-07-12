# Cursor IDE Project Rule & Documentation Ecosystem Guide

You will follow a strict, multi-step process:

## Phase 1: FORENSIC ANALYSIS & DISCOVERY\*\*

Your analysis must be deep and methodical. You are not just scanning; you are investigating to find the project's soul. Follow this checklist precisely:

1. **Dependency & Tech Stack Forensics:**

   - **Identify Core Frameworks and Libraries:** First, identify the primary frameworks (e.g., Angular, Angular Material, Nx, Django) and key libraries by analyzing `package.json`, `requirements.txt`, etc.
   - **Check for Deprecated Libraries:** Actively search for the use of outdated or deprecated libraries where modern alternatives exist. A key goal is to propose rules that enforce migrations, such as moving from legacy Angular modules or APIs to their modern equivalents.
   - **Identify "Keystone" Libraries:** Pinpoint libraries central to the project's workflow (e.g., `@angular/forms` for forms, `@ngrx/store` for state management, `scss` for styling) as these are prime candidates for rules that enforce their consistent use.

2. **Architectural & Code Pattern Analysis:**

   - **Directory Structure:** Analyze the file system for established Angular patterns like `src/app/components`, `src/app/services`, or `libs/`. Note if it's a monorepo with nested `.cursor/rules` directories, as this requires localized rules.
   - **Framework Best Practices:** For the identified framework, investigate adherence to modern Angular best practices.
     - _For Angular:_ Analyze the use of standalone components, signals, dependency injection with `inject`, lazy-loaded feature modules, and the use of Angular CLI conventions. Check for the use of `NgOptimizedImage` for images, and deferrable views for performance.
     - _For Django:_ Search for potential N+1 query issues and analyze whether ORM usage is efficient (`select_related`, `prefetch_related`). Check for consistent use of Class-Based Views vs. Function-Based Views.
   - **Naming Conventions & Code Style:** Go beyond formatters. Identify common naming conventions for variables, functions (e.g., `isActive`, `fetchData`), and Angular artifacts (e.g., `*.component.ts`, `*.service.ts`). Look for general code quality patterns like early returns, use of pure functions, and high function complexity that could be standardized.

3. **Testing & DevOps Analysis:**

   - **Testing Patterns:** Locate test files (`*.spec.ts`, etc.). Analyze the testing commands and common file naming conventions to understand the testing strategy, such as the use of Jasmine, Jest, or Vitest for Angular.
   - **DevOps Files:** Examine `Dockerfile` or CI/CD configurations for opportunities to enforce best practices, such as using multi-stage builds or Angular-specific build optimizations.

4. **Synthesize Findings:** Conclude this phase by creating a detailed summary of your findings before moving on to proposing any rules.

## Phase 2: PLAN & PROPOSE\*\*

1. **Formulate a Strategy**: Based on your analysis, create a detailed plan. Do not write the rules or documents yet.
2. **Propose Rules**: Propose a list of standard project rules, categorized by activation trigger (`Auto Attached`, `Always`, `Manual`).
3. **Propose Knowledge Management Framework (if necessary)**: If you identified the project as complex in Phase 1, your plan MUST also include a proposal to create a documentation framework. This prevents the AI from suffering from "amnesia" on complex tasks. This proposal should include:
   - The creation of key Markdown files (e.g., `docs/project-plan.md`, `docs/tech-debt.md`).
   - The creation of a special rule (`documentation-practices.mdc`) that instructs the AI on how to use and maintain these files.
4. **Present the Plan**: Report your complete plan to me (both rules and the knowledge framework). Wait for my approval before proceeding.

## Phase 3: EXECUTE & SAVE RULES

1. **Generate Rules**: Once I approve the plan, generate each rule file as planned. Use strong, unambiguous language ("You MUST...", "NEVER...") for critical rules.
2. **Save the Rule Files**: Use your `Edit & Reapply` tool to create and save each `.mdc` file in the `.cursor/rules/` directory.

## Phase 4: EXECUTE & SAVE KNOWLEDGE FRAMEWORK (if approved)\*\*

1. **Create Documentation Templates**: If I approved the knowledge framework, create the proposed `.md` files (e.g., inside a `/docs` directory). Populate them with a basic structure or introduction.

2. **Create the "Documentation" Rule**: Generate the `documentation-practices.mdc` rule. The instructions within this rule are critical. They should be similar to this

   ***

   globs:

   - "\*_/_"
     description: "Rules for maintaining and using this project's knowledge base."

   ***

   ### Project Knowledge & Task Management

   This project uses Markdown files in the `/docs` directory to maintain a persistent memory and track tasks. You MUST adhere to this workflow to ensure context is never lost.

   - **Consult Before Acting**: Before beginning any new feature or complex task, you MUST first reference the plan in `@docs/project-plan.md` to understand the high-level goals and current status.
   - **Update As You Work**: As you complete steps of a task, you should update `@docs/project-plan.md` to reflect the progress. This preserves the "why" behind your changes.
   - **Formalize Learnings**: If a productive development session leads to a new, reusable pattern, formalize it by creating or updating a Project Rule.

3. **Completion Notification**: After saving all files, confirm that the process is complete.
