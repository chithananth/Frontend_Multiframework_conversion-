"""
CSS → Tailwind CSS Converter
Parses CSS rules and maps property-value pairs to Tailwind utility classes.
"""

import re

# ── Tailwind mapping tables ──────────────────────────────────────────────────

# Font sizes
FONT_SIZE_MAP = {
    "10px": "text-xs",  "11px": "text-xs", "12px": "text-xs",
    "14px": "text-sm",  "13px": "text-sm",
    "16px": "text-base","15px": "text-base",
    "18px": "text-lg",  "17px": "text-lg",
    "20px": "text-xl",
    "24px": "text-2xl", "22px": "text-2xl", "23px": "text-2xl",
    "30px": "text-3xl", "28px": "text-3xl", "29px": "text-3xl",
    "36px": "text-4xl",
    "48px": "text-5xl",
    "60px": "text-6xl",
    "72px": "text-7xl",
    "96px": "text-8xl",
    "128px":"text-9xl",
}

FONT_WEIGHT_MAP = {
    "100": "font-thin",    "200": "font-extralight",
    "300": "font-light",   "400": "font-normal",
    "500": "font-medium",  "600": "font-semibold",
    "700": "font-bold",    "800": "font-extrabold",
    "900": "font-black",
    "normal": "font-normal", "bold": "font-bold",
    "bolder": "font-extrabold", "lighter": "font-light",
}

TEXT_ALIGN_MAP = {
    "left": "text-left", "center": "text-center",
    "right": "text-right", "justify": "text-justify",
}

DISPLAY_MAP = {
    "block":        "block",
    "inline":       "inline",
    "inline-block": "inline-block",
    "flex":         "flex",
    "inline-flex":  "inline-flex",
    "grid":         "grid",
    "inline-grid":  "inline-grid",
    "hidden":       "hidden",
    "none":         "hidden",
    "table":        "table",
}

FLEX_DIRECTION_MAP = {
    "row":            "flex-row",
    "column":         "flex-col",
    "row-reverse":    "flex-row-reverse",
    "column-reverse": "flex-col-reverse",
}

JUSTIFY_MAP = {
    "flex-start":    "justify-start",
    "center":        "justify-center",
    "flex-end":      "justify-end",
    "space-between": "justify-between",
    "space-around":  "justify-around",
    "space-evenly":  "justify-evenly",
}

ALIGN_ITEMS_MAP = {
    "flex-start": "items-start",
    "center":     "items-center",
    "flex-end":   "items-end",
    "stretch":    "items-stretch",
    "baseline":   "items-baseline",
}

POSITION_MAP = {
    "static":   "static",
    "relative": "relative",
    "absolute": "absolute",
    "fixed":    "fixed",
    "sticky":   "sticky",
}

OVERFLOW_MAP = {
    "auto":   "overflow-auto",
    "hidden": "overflow-hidden",
    "scroll": "overflow-scroll",
    "visible":"overflow-visible",
}

CURSOR_MAP = {
    "pointer":     "cursor-pointer",
    "default":     "cursor-default",
    "not-allowed": "cursor-not-allowed",
    "wait":        "cursor-wait",
    "text":        "cursor-text",
    "move":        "cursor-move",
    "grab":        "cursor-grab",
    "none":        "cursor-none",
}

BORDER_STYLE_MAP = {
    "solid":  "border-solid",
    "dashed": "border-dashed",
    "dotted": "border-dotted",
    "double": "border-double",
    "none":   "border-transparent",
}


# ── Helper utilities ─────────────────────────────────────────────────────────

def _px_to_tw(value: str, prefix: str) -> str:
    """Convert a pixel / rem value to a Tailwind spacing class."""
    value = value.strip()
    # rem → px equivalent
    rem_match = re.match(r"^([\d.]+)rem$", value)
    if rem_match:
        px = float(rem_match.group(1)) * 16
        value = f"{int(px)}px" if px == int(px) else f"{px}px"

    px_match = re.match(r"^([\d.]+)px$", value)
    if px_match:
        px = float(px_match.group(1))
        tw_unit = px / 4          # Tailwind 1 unit = 4px
        if tw_unit == int(tw_unit):
            tw_unit = int(tw_unit)
        return f"{prefix}-{tw_unit}"

    # Percentage fallback
    pct_match = re.match(r"^([\d.]+)%$", value)
    if pct_match:
        pct = float(pct_match.group(1))
        tw_pct = {100: "full", 50: "1/2", 33: "1/3",
                  66: "2/3", 25: "1/4", 75: "3/4"}.get(int(pct))
        if tw_pct:
            return f"{prefix}-{tw_pct}"

    return f"/* {prefix}: {value} */"


def _shorthand_sides(value: str, prefix: str) -> list:
    """Expand shorthand (margin/padding) 1-4 value syntax to 4 Tailwind classes."""
    parts = value.split()
    classes = []
    mapping = {
        1: lambda p: [_px_to_tw(p[0], f"{prefix}"),],
        2: lambda p: [
            _px_to_tw(p[0], f"{prefix}y"),
            _px_to_tw(p[1], f"{prefix}x"),
        ],
        3: lambda p: [
            _px_to_tw(p[0], f"{prefix}t"),
            _px_to_tw(p[1], f"{prefix}x"),
            _px_to_tw(p[2], f"{prefix}b"),
        ],
        4: lambda p: [
            _px_to_tw(p[0], f"{prefix}t"),
            _px_to_tw(p[1], f"{prefix}r"),
            _px_to_tw(p[2], f"{prefix}b"),
            _px_to_tw(p[3], f"{prefix}l"),
        ],
    }
    fn = mapping.get(len(parts))
    if fn:
        classes = fn(parts)
    return classes


def _color_to_tw(value: str, prefix: str) -> str:
    """Very best-effort hex/rgb → Tailwind color hint."""
    # Named colors
    NAMED = {
        "white": f"{prefix}-white", "black": f"{prefix}-black",
        "red":   f"{prefix}-red-500", "blue": f"{prefix}-blue-500",
        "green": f"{prefix}-green-500", "yellow": f"{prefix}-yellow-400",
        "gray":  f"{prefix}-gray-500", "grey":   f"{prefix}-gray-500",
        "transparent": f"{prefix}-transparent",
    }
    lv = value.lower()
    if lv in NAMED:
        return NAMED[lv]
    # hex
    if re.match(r"^#[0-9a-fA-F]{3,6}$", value):
        return f"/* {prefix}: {value} – use arbitrary value [{value}] */"
    # rgb/rgba
    if value.startswith("rgb"):
        return f"/* {prefix}: {value} – use arbitrary value */"
    return f"/* {prefix}: {value} */"


# ── Core conversion function ─────────────────────────────────────────────────

def _prop_value_to_tw(prop: str, value: str) -> list:
    """Map a single CSS property+value to a list of Tailwind classes/comments."""
    prop  = prop.strip().lower()
    value = value.strip()
    classes = []

    # margin
    if prop == "margin":
        classes = _shorthand_sides(value, "m")
    elif prop == "margin-top":
        classes = [_px_to_tw(value, "mt")]
    elif prop == "margin-right":
        classes = [_px_to_tw(value, "mr")]
    elif prop == "margin-bottom":
        classes = [_px_to_tw(value, "mb")]
    elif prop == "margin-left":
        classes = [_px_to_tw(value, "ml")]

    # padding
    elif prop == "padding":
        classes = _shorthand_sides(value, "p")
    elif prop == "padding-top":
        classes = [_px_to_tw(value, "pt")]
    elif prop == "padding-right":
        classes = [_px_to_tw(value, "pr")]
    elif prop == "padding-bottom":
        classes = [_px_to_tw(value, "pb")]
    elif prop == "padding-left":
        classes = [_px_to_tw(value, "pl")]

    # width / height
    elif prop == "width":
        classes = [_px_to_tw(value, "w")]
    elif prop == "height":
        classes = [_px_to_tw(value, "h")]
    elif prop == "min-width":
        classes = [_px_to_tw(value, "min-w")]
    elif prop == "max-width":
        classes = [_px_to_tw(value, "max-w")]
    elif prop == "min-height":
        classes = [_px_to_tw(value, "min-h")]
    elif prop == "max-height":
        classes = [_px_to_tw(value, "max-h")]

    # typography
    elif prop == "font-size":
        classes = [FONT_SIZE_MAP.get(value, f"/* font-size: {value} */")]
    elif prop == "font-weight":
        classes = [FONT_WEIGHT_MAP.get(value, f"/* font-weight: {value} */")]
    elif prop == "text-align":
        classes = [TEXT_ALIGN_MAP.get(value, f"/* text-align: {value} */")]
    elif prop == "line-height":
        classes = [_px_to_tw(value, "leading") if "px" in value else f"leading-{value.replace('.', '-')}"]
    elif prop == "letter-spacing":
        classes = [f"/* letter-spacing: {value} */"]
    elif prop == "text-decoration":
        td = {"none": "no-underline", "underline": "underline",
              "line-through": "line-through", "overline": "overline"}
        classes = [td.get(value, f"/* text-decoration: {value} */")]
    elif prop == "text-transform":
        tt = {"uppercase": "uppercase", "lowercase": "lowercase",
              "capitalize": "capitalize", "none": "normal-case"}
        classes = [tt.get(value, f"/* text-transform: {value} */")]

    # colors
    elif prop == "color":
        classes = [_color_to_tw(value, "text")]
    elif prop in ("background-color", "background"):
        classes = [_color_to_tw(value, "bg")]

    # display
    elif prop == "display":
        classes = [DISPLAY_MAP.get(value, f"/* display: {value} */")]

    # flex
    elif prop == "flex-direction":
        classes = [FLEX_DIRECTION_MAP.get(value, f"/* flex-direction: {value} */")]
    elif prop == "justify-content":
        classes = [JUSTIFY_MAP.get(value, f"/* justify-content: {value} */")]
    elif prop == "align-items":
        classes = [ALIGN_ITEMS_MAP.get(value, f"/* align-items: {value} */")]
    elif prop == "flex-wrap":
        classes = [{"wrap": "flex-wrap", "nowrap": "flex-nowrap",
                    "wrap-reverse": "flex-wrap-reverse"}.get(value, f"/* flex-wrap: {value} */")]
    elif prop == "flex":
        classes = [{"1": "flex-1", "auto": "flex-auto", "none": "flex-none",
                    "0": "flex-none"}.get(value, f"/* flex: {value} */")]
    elif prop == "gap":
        classes = [_px_to_tw(value, "gap")]
    elif prop == "column-gap":
        classes = [_px_to_tw(value, "gap-x")]
    elif prop == "row-gap":
        classes = [_px_to_tw(value, "gap-y")]

    # grid
    elif prop == "grid-template-columns":
        n = re.match(r"repeat\((\d+),", value)
        classes = [f"grid-cols-{n.group(1)}" if n else f"/* grid-template-columns: {value} */"]
    elif prop == "grid-template-rows":
        n = re.match(r"repeat\((\d+),", value)
        classes = [f"grid-rows-{n.group(1)}" if n else f"/* grid-template-rows: {value} */"]

    # border
    elif prop == "border-radius":
        BR = {"0": "rounded-none", "2px": "rounded-sm", "4px": "rounded",
              "6px": "rounded-md", "8px": "rounded-lg", "12px": "rounded-xl",
              "16px": "rounded-2xl", "24px": "rounded-3xl", "50%": "rounded-full",
              "9999px": "rounded-full"}
        classes = [BR.get(value, f"/* border-radius: {value} */")]
    elif prop == "border-width":
        BW = {"0": "border-0", "1px": "border", "2px": "border-2",
              "4px": "border-4", "8px": "border-8"}
        classes = [BW.get(value, f"/* border-width: {value} */")]
    elif prop == "border-style":
        classes = [BORDER_STYLE_MAP.get(value, f"/* border-style: {value} */")]
    elif prop == "border-color":
        classes = [_color_to_tw(value, "border")]
    elif prop == "border":
        parts = value.split()
        bc = []
        for p in parts:
            if p.endswith("px"):
                bw = {"0px": "border-0", "1px": "border", "2px": "border-2",
                      "4px": "border-4", "8px": "border-8"}.get(p, f"/* bw:{p} */")
                bc.append(bw)
            elif p in BORDER_STYLE_MAP:
                bc.append(BORDER_STYLE_MAP[p])
        classes = bc or [f"/* border: {value} */"]

    # sizing
    elif prop == "overflow":
        classes = [OVERFLOW_MAP.get(value, f"/* overflow: {value} */")]
    elif prop == "overflow-x":
        classes = [f"overflow-x-{value}" if value in ("auto","hidden","scroll","visible") else f"/* overflow-x: {value} */"]
    elif prop == "overflow-y":
        classes = [f"overflow-y-{value}" if value in ("auto","hidden","scroll","visible") else f"/* overflow-y: {value} */"]

    # position
    elif prop == "position":
        classes = [POSITION_MAP.get(value, f"/* position: {value} */")]
    elif prop in ("top", "right", "bottom", "left"):
        classes = [_px_to_tw(value, prop)]

    # z-index
    elif prop == "z-index":
        ZI = {"0": "z-0", "10": "z-10", "20": "z-20", "30": "z-30",
              "40": "z-40", "50": "z-50", "auto": "z-auto"}
        classes = [ZI.get(value, f"/* z-index: {value} */")]

    # opacity
    elif prop == "opacity":
        try:
            op = int(float(value) * 100)
            classes = [f"opacity-{op}"]
        except ValueError:
            classes = [f"/* opacity: {value} */"]

    # cursor
    elif prop == "cursor":
        classes = [CURSOR_MAP.get(value, f"/* cursor: {value} */")]

    # shadow
    elif prop == "box-shadow":
        if value == "none":
            classes = ["shadow-none"]
        else:
            classes = ["shadow /* customize: shadow-sm/md/lg/xl/2xl */"]

    # transition
    elif prop == "transition":
        classes = ["transition-all"]
    elif prop == "transition-duration":
        classes = [f"duration-{value.replace('ms', '')}"]

    else:
        classes = [f"/* {prop}: {value} */"]

    return [c for c in classes if c]


def css_to_tailwind(css_code: str) -> str:
    """
    Main entry point.
    Returns an annotated string where each CSS rule block is
    replaced with its Tailwind equivalents.
    """
    output_lines = []
    # Split into rule blocks: selector { ... }
    rule_pattern = re.compile(
        r'([^{]+)\{([^}]*)\}', re.MULTILINE | re.DOTALL
    )
    last_end = 0

    for match in rule_pattern.finditer(css_code):
        selector = match.group(1).strip()
        body     = match.group(2).strip()
        # Comments/whitespace before this rule
        gap = css_code[last_end:match.start()].strip()
        if gap:
            output_lines.append(f"/* {gap} */")
        last_end = match.end()

        tw_classes = []
        for decl in body.split(";"):
            decl = decl.strip()
            if not decl or decl.startswith("/*"):
                continue
            if ":" not in decl:
                continue
            prop, _, val = decl.partition(":")
            tw_classes.extend(_prop_value_to_tw(prop.strip(), val.strip()))

        unique_classes = _dedupe(tw_classes)

        output_lines.append(f"/* Selector: {selector} */")
        if unique_classes:
            output_lines.append(f'className="{" ".join(unique_classes)}"')
        output_lines.append("")

    return "\n".join(output_lines)


def _dedupe(lst: list) -> list:
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
