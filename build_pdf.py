from __future__ import annotations

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

PAGE_W, PAGE_H = A4
MARGIN_X = 17 * mm
MARGIN_TOP = 15 * mm
MARGIN_BOTTOM = 14 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X

INK = HexColor("#101827")
ACCENT = HexColor("#0E6E7A")
MUTED = HexColor("#55637A")
RULE = HexColor("#D3DAE4")
PANEL = HexColor("#F5F8FA")

BASE = getSampleStyleSheet()["Normal"]


def style(name: str, parent: ParagraphStyle = BASE, **kw) -> ParagraphStyle:
    return ParagraphStyle(name, parent=parent, **kw)


S_NAME = style("s_name", fontName="Helvetica-Bold", fontSize=7.6, leading=9.4,
               textColor=INK, alignment=TA_LEFT)
S_TAG = style("s_tag", fontName="Helvetica", fontSize=7.6, leading=9.4,
              textColor=MUTED, alignment=TA_RIGHT)
S_TITLE = style("s_title", fontName="Helvetica-Bold", fontSize=22, leading=24.5,
                textColor=INK, spaceAfter=1.5)
S_SUB = style("s_sub", fontName="Helvetica", fontSize=10.4, leading=13.4,
              textColor=MUTED)
S_STACK = style("s_stack", fontName="Helvetica", fontSize=8.5, leading=11,
                textColor=ACCENT)
S_H2 = style("s_h2", fontName="Helvetica-Bold", fontSize=10.6, leading=12.6,
             textColor=INK, spaceBefore=0, spaceAfter=0)
S_BODY = style("s_body", fontName="Helvetica", fontSize=9.7, leading=13.6,
               textColor=INK)
S_BULLET = style("s_bullet", parent=S_BODY, fontSize=9.6, leading=13.4)
S_BULLET_MARK = style("s_bullet_mark", parent=S_BULLET, textColor=ACCENT)
S_MONO = style("s_mono", fontName="Courier", fontSize=8.4, leading=11.2,
               textColor=INK)
S_FINE = style("s_fine", fontName="Helvetica", fontSize=8.6, leading=11.4,
               textColor=MUTED)


def rule(width: float = CONTENT_W, thickness: float = 0.5,
         color: HexColor = RULE, space: float = 0) -> Table:
    t = Table([[""]], colWidths=[width], rowHeights=[thickness])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), space),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def heading(text: str) -> list:
    return [
        Spacer(1, 4.6 * mm),
        Paragraph(text, S_H2),
        Spacer(1, 1.5 * mm),
        rule(thickness=0.7, color=INK),
        Spacer(1, 2.6 * mm),
    ]


def marker(size: float = 2.35, color: HexColor = ACCENT) -> Table:
    t = Table([[""]], colWidths=[size * mm], rowHeights=[size * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def bullets(items: list[str], gap: float = 0.55) -> Table:
    rows = [
        [marker(), Paragraph(item, S_BULLET)]
        for item in items
    ]
    t = Table(rows, colWidths=[5.0 * mm, CONTENT_W - 5.0 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 0),
        ("LEFTPADDING", (1, 0), (1, -1), 0),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 3.0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), gap),
    ]))
    return t


def code_panel(lines: list[str]) -> Table:
    rows = [[Paragraph(line, S_MONO)] for line in lines]
    t = Table(rows, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


INLINE = {"<c>": "<font face='Courier' size='8.8'>",
          "</c>": "</font>"}


def rich(text: str) -> str:
    for key, val in INLINE.items():
        text = text.replace(key, val)
    return text


REPO_URL = "https://github.com/namitkharade/dqc-engine"


def build(path: str) -> None:
    flow: list = []

    header = Table(
        [[Paragraph("NAMIT BHALENDRA KHARADE", S_NAME),
          Paragraph("CODE SAMPLE", S_TAG)]],
        colWidths=[CONTENT_W * 0.6, CONTENT_W * 0.4],
    )
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    flow.append(header)
    flow.append(Spacer(1, 2.2 * mm))
    flow.append(rule(thickness=0.9, color=INK))
    flow.append(Spacer(1, 4.2 * mm))

    flow.append(Paragraph("DQC Mini Engine", S_TITLE))
    flow.append(Paragraph(
        "A small data-quality validation service, written to be read.",
        S_SUB))
    flow.append(Spacer(1, 1.6 * mm))
    flow.append(Paragraph(
        "Python &nbsp;/&nbsp; FastAPI &nbsp;/&nbsp; Pydantic &nbsp;/&nbsp; "
        "SQLAlchemy &nbsp;/&nbsp; SQLite &nbsp;/&nbsp; OpenAI Responses API",
        S_STACK))
    flow.append(Spacer(1, 4.2 * mm))

    flow.append(Paragraph(rich(
        "A little over 500 lines of Python in six files. A record comes in, "
        "the rules check it, the issues are stored in SQLite, and each issue "
        "comes back with a severity and a fix someone can act on. I wrote it "
        "because data quality is usually the part of a backend that gets "
        "bolted on last, and I wanted a small piece of code I could hand over "
        "and defend line by line."), S_BODY))

    flow += heading("What it does")
    flow.append(Paragraph(rich(
        "Four endpoints under <c>/api/v1</c>, every request and response a "
        "Pydantic model, so the OpenAPI output at <c>/docs</c> is the "
        "documentation instead of a page I forget to update."), S_BODY))
    flow.append(Spacer(1, 1.4 * mm))
    flow.append(bullets([
        rich("<c>POST /validate</c> checks one record, stores what it found "
             "and returns the issues."),
        rich("<c>POST /validate/batch</c> takes up to 100 records, validates "
             "them concurrently and returns the counts with the detail."),
        rich("<c>GET /issues</c> lists stored issues, optionally filtered by "
             "severity."),
        rich("<c>POST /suggest</c> asks a model for a fix when a canned "
             "message is not enough."),
    ]))
    flow.append(Spacer(1, 0.6 * mm))

    flow += heading("How I built it")
    flow.append(bullets([
        "The contract came first. A record in, a result out, both typed as "
        "Pydantic models. That settles the shape of the code before I write "
        "any of it.",

        rich("Validation is one pure function. <c>validate_record()</c> takes "
             "a record and returns a list of issues. No session, no request "
             "object, no import from FastAPI, so a rule can be exercised with "
             "a plain dict and the whole rule set stays in one readable file."),

        "The rule writes its own fix. Each check returns its suggested_fix "
        "next to the failure, for example telling you that a phone number is "
        "missing its leading plus. A deterministic rule explains itself "
        "better than a language model does, and it never invents a value.",

        "A broken record does not sink the batch. Every record is wrapped, "
        "and an exception becomes a system_error issue on that row only. One "
        "bad row returns one failure, not a 500 for all hundred.",

        rich("The model sits behind one function. The endpoint calls "
             "<c>_suggestion_provider</c>, so moving off OpenAI is a one-line "
             "change and the rest of the service never learns about it."),
    ]))

    flow += heading("What I would change next")
    flow.append(bullets([
        rich("Tests around <c>validator.py</c>. It is the cheapest thing to "
             "pin down and the only part holding real rules."),
        "The country check is a 30-code allowlist. It should load the full "
        "ISO 3166 table rather than the codes I happened to type.",
        "The suggestion route calls the synchronous OpenAI client inside an "
        "async app. AsyncOpenAI is the honest fix.",
    ]))

    flow += heading("Running it")
    flow.append(code_panel([
        "pip install -r requirements.txt",
        "python main.py          # docs at http://localhost:8000/docs",
        "# OPENAI_API_KEY in .env is only needed for /suggest",
    ]))

    flow.append(Spacer(1, 4.0 * mm))
    flow.append(rule(thickness=0.7, color=INK))
    flow.append(Spacer(1, 2.2 * mm))

    footer = Table(
        [[
            Paragraph(
                "<font color='#55637A'>The code</font><br/>"
                f"<link href='{REPO_URL}'><font color='#0E6E7A'>"
                "github.com/namitkharade/dqc-engine</font></link>",
                S_BODY),
            Paragraph(
                "The README covers the layout and both setup paths. "
                "The core service runs with no key at all.",
                S_FINE),
        ]],
        colWidths=[CONTENT_W * 0.46, CONTENT_W * 0.54],
    )
    footer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    flow.append(KeepTogether(footer))

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="DQC Mini Engine: code sample",
        author="Namit Bhalendra Kharade",
        subject="Data-quality validation service in Python and FastAPI",
    )
    doc.build(flow)


if __name__ == "__main__":
    out = "NamitKharade_DQC-Engine_Code-Sample.pdf"
    build(out)
    print(f"wrote {out}")
