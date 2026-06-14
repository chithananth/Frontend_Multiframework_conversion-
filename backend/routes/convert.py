"""
/api/convert  and  /api/download/<id>  and  /api/convert-zip  endpoints
"""

import io
import os
import zipfile
from flask import Blueprint, request, jsonify, send_file
from extensions import db
from models import Conversion
from converters.html_to_react import html_to_react
from converters.css_to_tailwind import css_to_tailwind
from converters.zip_builder import build_zip

convert_bp = Blueprint("convert", __name__)


@convert_bp.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json(force=True)

    conv_type     = data.get("type", "")          # html_to_react | css_to_tailwind
    input_code    = data.get("input_code", "")
    output_format = data.get("output_format", "single")   # single | merged | zip
    component_name = data.get("component_name", "ConvertedComponent")

    if not input_code.strip():
        return jsonify({"error": "input_code is required"}), 400
    if conv_type not in ("html_to_react", "css_to_tailwind"):
        return jsonify({"error": "type must be html_to_react or css_to_tailwind"}), 400

    # ── Run conversion ───────────────────────────────────────────────────────
    if conv_type == "html_to_react":
        output_code = html_to_react(input_code, component_name)
        filename    = f"{component_name}.jsx"
    else:
        output_code = css_to_tailwind(input_code)
        filename    = "tailwind_classes.txt"

    # ── Handle output formats ────────────────────────────────────────────────
    if output_format == "merged":
        if conv_type == "html_to_react":
            merged = output_code + "\n\n/* Add your Tailwind CSS classes below */\n"
            output_code = merged
            filename = f"{component_name}_merged.jsx"
        else:
            filename = "tailwind_merged.txt"

    # ── Save to DB ───────────────────────────────────────────────────────────
    record = Conversion(
        type=conv_type,
        input_code=input_code,
        output_code=output_code,
        output_format=output_format,
        filename=filename,
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "id":          record.id,
        "type":        record.type,
        "output_code": record.output_code,
        "filename":    record.filename,
        "output_format": record.output_format,
        "created_at":  record.created_at.isoformat(),
    })


# ─────────────────────────────────────────────────────────────────────────────
#  NEW: Multi-file ZIP upload → convert all → return ZIP download
# ─────────────────────────────────────────────────────────────────────────────
def _detect_and_convert(filename: str, content: str, conv_type: str) -> tuple:
    """
    Convert a single file based on its extension or the chosen conv_type.
    Returns (output_filename, output_content).
    """
    ext = os.path.splitext(filename)[1].lower()
    base = os.path.splitext(filename)[0]

    # Determine conversion based on file extension
    if ext in (".html", ".htm"):
        comp_name = base.replace("-", "_").replace(" ", "_").title().replace("_", "")
        if not comp_name:
            comp_name = "ConvertedComponent"
        out = html_to_react(content, comp_name)
        return (f"{comp_name}.jsx", out)

    elif ext == ".css":
        out = css_to_tailwind(content)
        return (f"{base}_tailwind.txt", out)

    elif ext in (".js", ".jsx"):
        # JS files: if conv_type is html_to_react, try converting any HTML-like content
        # Otherwise pass through unchanged
        if conv_type == "html_to_react" and ("<" in content and ">" in content):
            comp_name = base.replace("-", "_").replace(" ", "_").title().replace("_", "")
            if not comp_name:
                comp_name = "ConvertedComponent"
            out = html_to_react(content, comp_name)
            return (f"{comp_name}.jsx", out)
        return (filename, content)  # pass through

    else:
        # Unknown extension: try to convert based on chosen type
        if conv_type == "html_to_react":
            comp_name = base.replace("-", "_").replace(" ", "_").title().replace("_", "")
            if not comp_name:
                comp_name = "ConvertedComponent"
            out = html_to_react(content, comp_name)
            return (f"{comp_name}.jsx", out)
        else:
            out = css_to_tailwind(content)
            return (f"{base}_tailwind.txt", out)


@convert_bp.route("/api/convert-zip", methods=["POST"])
def convert_zip():
    """
    Accept multiple file uploads, convert each one, package results into a ZIP.
    Form fields:
      - type: html_to_react | css_to_tailwind
      - files: multiple file uploads
    """
    conv_type = request.form.get("type", "html_to_react")
    if conv_type not in ("html_to_react", "css_to_tailwind"):
        return jsonify({"error": "type must be html_to_react or css_to_tailwind"}), 400

    uploaded_files = request.files.getlist("files")
    if not uploaded_files:
        return jsonify({"error": "No files uploaded"}), 400

    converted_files = {}
    all_input_names = []
    all_output_summary = []

    for f in uploaded_files:
        if not f.filename:
            continue

        original_name = f.filename
        all_input_names.append(original_name)

        # Check if the uploaded file is a ZIP itself
        if original_name.lower().endswith(".zip"):
            try:
                zip_data = f.read()
                with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zf:
                    for inner_name in zf.namelist():
                        # Skip directories and hidden files
                        if inner_name.endswith("/") or inner_name.startswith("__") or inner_name.startswith("."):
                            continue
                        try:
                            inner_content = zf.read(inner_name).decode("utf-8", errors="replace")
                        except Exception:
                            continue
                        out_name, out_content = _detect_and_convert(
                            os.path.basename(inner_name), inner_content, conv_type
                        )
                        # Avoid filename collisions
                        if out_name in converted_files:
                            base, ext = os.path.splitext(out_name)
                            out_name = f"{base}_{len(converted_files)}{ext}"
                        converted_files[out_name] = out_content
                        all_output_summary.append(f"{inner_name} → {out_name}")
            except zipfile.BadZipFile:
                return jsonify({"error": f"'{original_name}' is not a valid ZIP file"}), 400
        else:
            # Regular file
            try:
                content = f.read().decode("utf-8", errors="replace")
            except Exception:
                continue

            out_name, out_content = _detect_and_convert(original_name, content, conv_type)

            # Avoid filename collisions
            if out_name in converted_files:
                base, ext = os.path.splitext(out_name)
                out_name = f"{base}_{len(converted_files)}{ext}"

            converted_files[out_name] = out_content
            all_output_summary.append(f"{original_name} → {out_name}")

    if not converted_files:
        return jsonify({"error": "No convertible files found"}), 400

    # Build ZIP
    zip_bytes = build_zip(converted_files)
    zip_filename = "converted_files.zip"

    # Save summary to DB
    input_summary = ", ".join(all_input_names)
    output_summary = "\n".join(all_output_summary)
    record = Conversion(
        type=conv_type,
        input_code=f"[ZIP Upload: {input_summary}]",
        output_code=output_summary,
        output_format="zip",
        filename=zip_filename,
    )
    db.session.add(record)
    db.session.commit()

    return send_file(
        io.BytesIO(zip_bytes),
        mimetype="application/zip",
        as_attachment=True,
        download_name=zip_filename,
    )


@convert_bp.route("/api/download/<int:conv_id>", methods=["GET"])
def download(conv_id):
    record = Conversion.query.get_or_404(conv_id)
    buf = io.BytesIO(record.output_code.encode("utf-8"))
    mime = "application/zip" if record.output_format == "zip" else "text/plain"
    return send_file(
        buf,
        mimetype=mime,
        as_attachment=True,
        download_name=record.filename or f"output_{conv_id}.txt",
    )
