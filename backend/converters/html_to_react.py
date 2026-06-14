"""
HTML → React JSX Converter
Converts raw HTML into a functional React component with proper JSX syntax.
"""

import re
from bs4 import BeautifulSoup, NavigableString, Tag

# ── Attribute name mappings ──────────────────────────────────────────────────
ATTR_MAP = {
    "class":          "className",
    "for":            "htmlFor",
    "tabindex":       "tabIndex",
    "readonly":       "readOnly",
    "maxlength":      "maxLength",
    "colspan":        "colSpan",
    "rowspan":        "rowSpan",
    "crossorigin":    "crossOrigin",
    "accesskey":      "accessKey",
    "contenteditable":"contentEditable",
    "enctype":        "encType",
    "usemap":         "useMap",
    "frameborder":    "frameBorder",
    "allowfullscreen":"allowFullScreen",
    "autocomplete":   "autoComplete",
    "autofocus":      "autoFocus",
    "autoplay":       "autoPlay",
    "cellpadding":    "cellPadding",
    "cellspacing":    "cellSpacing",
}

# Self-closing HTML tags
VOID_ELEMENTS = {
    "area","base","br","col","embed","hr","img","input",
    "link","meta","param","source","track","wbr",
}

# Inline event handler conversions  onclick → onClick
def _camel_event(attr: str) -> str:
    if attr.startswith("on") and len(attr) > 2:
        return "on" + attr[2:].capitalize()
    return attr


def _convert_attrs(tag: Tag) -> str:
    """Return a JSX attribute string from a BS4 tag's attrs dict."""
    parts = []
    for attr, val in tag.attrs.items():
        # List values (e.g. class) → join
        if isinstance(val, list):
            val = " ".join(val)

        jsx_attr = ATTR_MAP.get(attr, _camel_event(attr))

        # style="…" → style={{ … }}
        if attr == "style":
            css_obj = _inline_style_to_obj(val)
            parts.append(f'style={{{{{css_obj}}}}}')
        # Boolean attributes
        elif val == "" or val is None:
            parts.append(jsx_attr)
        else:
            # Escape curly braces inside attribute values
            val_escaped = val.replace("{", "&#123;").replace("}", "&#125;")
            parts.append(f'{jsx_attr}="{val_escaped}"')
    return (" " + " ".join(parts)) if parts else ""


def _inline_style_to_obj(style_str: str) -> str:
    """Convert inline CSS string to a JS object literal string."""
    props = []
    for declaration in style_str.split(";"):
        declaration = declaration.strip()
        if ":" not in declaration:
            continue
        prop, _, value = declaration.partition(":")
        prop = prop.strip()
        value = value.strip()
        # camelCase
        camel = re.sub(r"-([a-z])", lambda m: m.group(1).upper(), prop)
        props.append(f'{camel}: "{value}"')
    return ", ".join(props)


def _node_to_jsx(node, indent: int = 2) -> str:
    """Recursively convert a BS4 node to JSX."""
    pad = " " * indent

    if isinstance(node, NavigableString):
        text = str(node)
        # Skip pure whitespace nodes
        if not text.strip():
            return ""
        # Escape curly braces in text content
        text = text.replace("{", "&#123;").replace("}", "&#125;")
        return pad + text.strip()

    if not isinstance(node, Tag):
        return ""

    tag_name = node.name.lower()
    attrs    = _convert_attrs(node)

    if tag_name in VOID_ELEMENTS:
        return f"{pad}<{tag_name}{attrs} />"

    children_jsx = []
    for child in node.children:
        child_str = _node_to_jsx(child, indent + 2)
        if child_str:
            children_jsx.append(child_str)

    if not children_jsx:
        return f"{pad}<{tag_name}{attrs}></{tag_name}>"

    inner = "\n".join(children_jsx)
    return f"{pad}<{tag_name}{attrs}>\n{inner}\n{pad}</{tag_name}>"


def html_to_react(html_code: str, component_name: str = "ConvertedComponent") -> str:
    """
    Main entry point.
    Returns a string containing a runnable React functional component.
    """
    # Sanitize component name
    component_name = re.sub(r"[^A-Za-z0-9]", "", component_name) or "ConvertedComponent"
    if not component_name[0].isupper():
        component_name = component_name.capitalize()

    soup = BeautifulSoup(html_code, "lxml")

    # Try to extract body content; fall back to the whole doc
    body = soup.body
    root_nodes = list(body.children) if body else list(soup.children)

    # Filter out NavigableString whitespace at top level
    elements = [n for n in root_nodes if isinstance(n, Tag)]

    if not elements:
        # Plain text or empty
        jsx_body = "    <div></div>"
    elif len(elements) == 1:
        jsx_body = _node_to_jsx(elements[0], indent=4)
    else:
        # Wrap multiple roots in a Fragment
        children = "\n".join(_node_to_jsx(el, indent=6) for el in elements)
        jsx_body = f"    <>\n{children}\n    </>"

    return (
        f"import React from 'react';\n\n"
        f"const {component_name} = () => {{\n"
        f"  return (\n"
        f"{jsx_body}\n"
        f"  );\n"
        f"}};\n\n"
        f"export default {component_name};\n"
    )
