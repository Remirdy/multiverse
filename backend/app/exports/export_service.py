import csv
import io
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from docx import Document as DocxDocument
from pptx import Presentation
from pptx.util import Inches, Pt
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


_UNICODE_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _register_unicode_font() -> str:
    """Register a TrueType font capable of rendering Turkish and Unicode characters in PDF."""
    font_name = "MultiverseUnicode"
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name
    for path in _UNICODE_FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, path))
                return font_name
            except Exception:
                continue
    return "Helvetica"


def _xml_escape(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


class ExportService:
    """Generates downloadable PDF, DOCX, PPTX, Markdown, JSON, CSV, and ICS artifacts."""

    def render_pdf(
        self,
        title: str,
        sections: List[Dict[str, Any]],
        paper_size: str = "A4",
    ) -> bytes:
        buf = io.BytesIO()
        pagesize = LETTER if paper_size.upper() == "LETTER" else A4
        doc = SimpleDocTemplate(
            buf,
            pagesize=pagesize,
            leftMargin=50,
            rightMargin=50,
            topMargin=54,
            bottomMargin=50,
            title=title,
        )
        font_name = _register_unicode_font()
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "MVTitle",
            parent=styles["Heading1"],
            fontName=font_name,
            fontSize=16,
            leading=22,
            spaceAfter=10,
        )
        h2_style = ParagraphStyle(
            "MVH2",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=12.5,
            leading=17,
            spaceBefore=8,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "MVBody",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=10,
            leading=14,
            spaceAfter=6,
        )

        story: List[Any] = [Paragraph(_xml_escape(title), title_style), Spacer(1, 6)]
        for sec in sections:
            heading = sec.get("heading")
            if heading:
                story.append(Paragraph(_xml_escape(str(heading)), h2_style))
            body = sec.get("body") or ""
            for para in str(body).split("\n\n"):
                cleaned = para.strip()
                if cleaned:
                    story.append(Paragraph(_xml_escape(cleaned).replace("\n", "<br/>"), body_style))
            bullets = sec.get("bullets") or []
            for b in bullets:
                story.append(Paragraph(f"• {_xml_escape(str(b))}", body_style))
            table_rows = sec.get("table")
            if table_rows and len(table_rows) > 0:
                tbl = Table(table_rows, repeatRows=1)
                tbl.setStyle(
                    TableStyle([
                        ("FONTNAME", (0, 0), (-1, -1), font_name),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ])
                )
                story.append(tbl)
                story.append(Spacer(1, 8))

        def _add_page_number(canvas, _doc):
            canvas.saveState()
            canvas.setFont(font_name, 8)
            canvas.drawRightString(pagesize[0] - 50, 26, f"Page {_doc.page}")
            canvas.restoreState()

        doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
        return buf.getvalue()

    def render_docx(self, title: str, sections: List[Dict[str, Any]]) -> bytes:
        doc = DocxDocument()
        doc.add_heading(title, level=0)
        for sec in sections:
            if sec.get("heading"):
                doc.add_heading(str(sec["heading"]), level=2)
            if sec.get("body"):
                for para in str(sec["body"]).split("\n\n"):
                    if para.strip():
                        doc.add_paragraph(para.strip())
            for b in sec.get("bullets") or []:
                doc.add_paragraph(str(b), style="List Bullet")
            table_rows = sec.get("table")
            if table_rows and len(table_rows) > 0:
                cols = max(len(r) for r in table_rows)
                t = doc.add_table(rows=len(table_rows), cols=cols)
                t.style = "Table Grid"
                for r_idx, row in enumerate(table_rows):
                    for c_idx, val in enumerate(row):
                        t.cell(r_idx, c_idx).text = str(val)
        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def render_pptx(self, title: str, slides: List[Dict[str, Any]], subtitle: str = "") -> bytes:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        title_layout = prs.slide_layouts[0]
        title_slide = prs.slides.add_slide(title_layout)
        title_slide.shapes.title.text = title
        if len(title_slide.placeholders) > 1 and subtitle:
            title_slide.placeholders[1].text = subtitle

        content_layout = prs.slide_layouts[1]
        for s in slides:
            slide = prs.slides.add_slide(content_layout)
            slide.shapes.title.text = str(s.get("title", "Slide"))
            body_placeholder = slide.placeholders[1]
            tf = body_placeholder.text_frame
            tf.clear()
            bullets = s.get("bullets") or []
            if not bullets and s.get("body"):
                bullets = [line.strip() for line in str(s["body"]).splitlines() if line.strip()]
            for idx, item in enumerate(bullets[:8]):
                p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
                p.text = str(item)[:220]
                p.font.size = Pt(18)
                p.level = 0
            notes = s.get("speaker_notes")
            if notes:
                slide.notes_slide.notes_text_frame.text = str(notes)

        buf = io.BytesIO()
        prs.save(buf)
        return buf.getvalue()

    def render_markdown(self, title: str, sections: List[Dict[str, Any]]) -> bytes:
        lines = [f"# {title}", ""]
        for sec in sections:
            if sec.get("heading"):
                lines.append(f"## {sec['heading']}")
                lines.append("")
            if sec.get("body"):
                lines.append(str(sec["body"]))
                lines.append("")
            for b in sec.get("bullets") or []:
                lines.append(f"- {b}")
            if sec.get("bullets"):
                lines.append("")
            table_rows = sec.get("table")
            if table_rows and len(table_rows) > 0:
                header = table_rows[0]
                lines.append("| " + " | ".join(str(x) for x in header) + " |")
                lines.append("| " + " | ".join("---" for _ in header) + " |")
                for row in table_rows[1:]:
                    lines.append("| " + " | ".join(str(x) for x in row) + " |")
                lines.append("")
        return "\n".join(lines).encode("utf-8")

    def render_csv(self, rows: List[List[Any]]) -> bytes:
        buf = io.StringIO()
        writer = csv.writer(buf)
        for r in rows:
            writer.writerow(r)
        return buf.getvalue().encode("utf-8-sig")

    def render_ics(self, title: str, sessions: List[Dict[str, Any]]) -> bytes:
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Multiverse//Study Planner//EN",
        ]
        for idx, s in enumerate(sessions):
            date_str = str(s.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))).replace("-", "")
            topic = str(s.get("topic", "Study Session")).replace("\n", " ")
            course = str(s.get("course", "Course")).replace("\n", " ")
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:multiverse-session-{idx + 1}-{date_str}@local",
                f"DTSTART;VALUE=DATE:{date_str}",
                f"SUMMARY:{course}: {topic}",
                f"DESCRIPTION:Duration {s.get('hours', 1.5)}h | Status: {s.get('status', 'planned')}",
                "END:VEVENT",
            ])
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines).encode("utf-8")

    def generate(
        self,
        fmt: str,
        title: str,
        sections: Optional[List[Dict[str, Any]]] = None,
        json_payload: Optional[Any] = None,
        csv_rows: Optional[List[List[Any]]] = None,
        slides: Optional[List[Dict[str, Any]]] = None,
        ics_sessions: Optional[List[Dict[str, Any]]] = None,
        paper_size: str = "A4",
    ) -> Dict[str, Any]:
        ext = fmt.strip().lower().lstrip(".")
        secs = sections or []
        if ext == "pdf":
            return {"bytes": self.render_pdf(title, secs, paper_size=paper_size), "media_type": "application/pdf", "ext": "pdf"}
        if ext == "docx":
            return {"bytes": self.render_docx(title, secs), "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "ext": "docx"}
        if ext == "pptx":
            slide_list = slides if slides is not None else [{"title": s.get("heading", title), "body": s.get("body", ""), "bullets": s.get("bullets", [])} for s in secs]
            return {"bytes": self.render_pptx(title, slide_list), "media_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "ext": "pptx"}
        if ext in {"md", "markdown"}:
            return {"bytes": self.render_markdown(title, secs), "media_type": "text/markdown; charset=utf-8", "ext": "md"}
        if ext == "json":
            data = json_payload if json_payload is not None else {"title": title, "sections": secs}
            return {"bytes": json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"), "media_type": "application/json; charset=utf-8", "ext": "json"}
        if ext == "csv":
            rows = csv_rows or [["Section", "Content"], *[[s.get("heading", ""), s.get("body", "")] for s in secs]]
            return {"bytes": self.render_csv(rows), "media_type": "text/csv; charset=utf-8", "ext": "csv"}
        if ext == "ics":
            return {"bytes": self.render_ics(title, ics_sessions or []), "media_type": "text/calendar; charset=utf-8", "ext": "ics"}
        raise ValueError(f"Unsupported export format '{fmt}'")


export_service = ExportService()
