# Packages — deep modules

Every package in this directory is a **deep module**: a lot of behaviour behind a small interface. The public surface is the package's **entry points — the files at the package root** (`index.ts`, `types.ts`). Everything in a subfolder (`lib/`, `tests/`) is private.

```
packages/
  <name>/
    index.ts        ← entry point (public). Import this from outside.
    types.ts        ← another entry point. Packages may expose SEVERAL.
    lib/            ← implementation: hidden from outside.
    tests/          ← co-located tests + fixtures (a subfolder, so private).
```

## The four rules (enforced by `pnpm run lint:boundaries`)

1. **Entry-point boundary** — code outside a package may import only that package's root files, never anything in its subfolders.
2. **Intra-package freedom** — a package's own files import each other freely.
3. **Tests through the entry points** — files under `tests/` may import any package's entry points and their own `tests/` fixtures, but never any package's internals, not even their own.
4. **No cycles** — plus layering: `schemas ← sdk ← cli`, no reverse edges.

## Conventions

- **No barrel files.** Expose several small entry points (root files) instead of re-exporting a whole subtree through one giant `index.ts`. Adding an entry point = adding a root file.
- Any subfolder is private — you never extend the depcruise config to add a folder.
- Tests exercise a package through its entry points, exactly like external callers do.

Run the boundary check with `pnpm run lint:boundaries`. See `docs/architecture.md` for the module map.
