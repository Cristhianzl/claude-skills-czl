# Icons — Lucide and custom

A component's `icon` attribute is either a Lucide icon name (built-in) or the name of a custom SVG registered in the frontend.

---

## Use a Lucide icon (the easy path)

Find an icon at [https://lucide.dev/icons](https://lucide.dev/icons). Set the icon attribute to its name:

```python
class MyComponent(Component):
    icon = "sparkles"
```

Lucide names are PascalCase or kebab-case depending on the version; check the rendered output and pick whatever the existing Langflow components in the same area use.

When to prefer Lucide: brand-agnostic icons (`Search`, `File`, `Database`, `Globe`, `Sparkles`). Anything that represents a generic concept.

---

## Use a custom SVG (for branded providers)

Provider components (OpenAI, Anthropic, Chroma, etc.) typically have custom SVG icons. The end-to-end wiring is:

### Step 1 — Add the SVG component

Create `src/frontend/src/icons/<IconName>/<IconName>.tsx`:

```tsx
import React, { forwardRef } from "react";

type Props = React.SVGProps<SVGSVGElement> & {
  isDark?: boolean;
};

export const AcmeIcon = forwardRef<SVGSVGElement, Props>(
  ({ isDark = false, ...props }, ref) => {
    const fill = isDark ? "#FFFFFF" : "#111111";
    return (
      <svg
        ref={ref}
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        width="1em"
        height="1em"
        fill={fill}
        {...props}
      >
        {/* paste the SVG paths here */}
        <path d="M12 2l3 7h7l-5.5 4.5L18 22l-6-4-6 4 1.5-8.5L2 9h7l3-7z" />
      </svg>
    );
  },
);

AcmeIcon.displayName = "AcmeIcon";
```

### Step 2 — Register lazily

Add the icon to `src/frontend/src/icons/lazyIconImports.ts`:

```typescript
// ... existing imports
export const AcmeIcon = lazy(() =>
  import("./AcmeIcon/AcmeIcon").then((module) => ({ default: module.AcmeIcon })),
);
```

The key in the export map must match what the Python side will set as `icon = "Acme"` (case- and exact-spelling sensitive).

### Step 3 — Use in Python

```python
class AcmeChatModelComponent(Component):
    icon = "Acme"      # matches the key in lazyIconImports.ts
```

---

## Rules of thumb

| Situation                                                              | Choice                          |
|-----------------------------------------------------------------------|---------------------------------|
| Generic concept (search, file, database)                               | Lucide                          |
| Branded provider (OpenAI, Anthropic, Chroma, …)                        | Custom SVG with provider mark   |
| Internal tooling component                                             | Lucide (don't invent a brand)   |
| In doubt                                                                | Copy what the neighboring component uses |

---

## Dark mode

The custom SVG must support dark mode by accepting an `isDark` prop. The convention is: `fill` adapts; everything else stays as-is. Don't hardcode `#000` — the icon will disappear on the dark theme.

If your SVG has a colored brand mark that should stay consistent across themes, hardcode that color and apply `isDark` only to neutral elements (outlines, secondary marks).

---

## Common mistakes

- **`icon = "acme"` (lowercase) when the registered key is `"Acme"`.** Case-sensitive. The frontend silently falls back to a generic icon and the user sees a box.
- **Forgetting to add to `lazyIconImports.ts`.** The TSX file exists but isn't registered, so the icon never resolves at runtime.
- **Inline SVG that hardcodes `#000`.** Invisible on the dark theme. Pass `fill={isDark ? ... : ...}`.
- **Importing the icon eagerly instead of lazily.** Increases the bundle size of the editor; every icon should be lazy-loaded.
- **Icon path stroke widths inconsistent with the rest of the suite.** Match the existing brand icons in `src/frontend/src/icons/` for visual consistency.

---

## Testing an icon

There's no automated test for "does the icon render". The end-to-end check is manual:

1. `LFX_DEV=1 make backend` + `make frontend`.
2. Open the flow editor at `http://localhost:3000`.
3. Find the component in the sidebar — the icon should match.
4. Drag it onto the canvas — the node should show the icon.
5. Switch to dark mode — the icon must still be visible.

If any step fails, fix before opening the PR.
