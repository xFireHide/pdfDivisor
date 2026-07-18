# pdfDivisor — Label PDF Splitter (Shopee → thermal printer)

Desktop app that splits each PDF page into **four quadrants**, producing **one
label per page**. Built for personal use in a Shopee store, where the shipping
file ships **four labels on a single sheet** — a format thermal printers (Zebra
and similar) don't handle well, since they expect **one label per page**.

> On ZPL: Zebra printers usually speak ZPL, but in practice the workflow stays in
> PDF (visual, familiar) — it just separates the labels before printing, with no
> `.zpl` files day to day.

## How it works

1. Each page is rendered at 300 DPI (PyMuPDF).
2. Split into **4 quadrants**.
3. Near-white (empty) quadrants are skipped by a heuristic.
4. Each valid quadrant becomes **one page** in the output PDF.

| File | Role |
|---|---|
| `processor.py` | Rasterize, split into 4, filter white, build the output PDF |
| `desktop.py` | tkinter GUI: pick PDF, process in the background, save result |

## Requirements

Python 3.10+, `pymupdf`, `pillow` (see `requirements.txt`).

## Usage

```bash
# macOS / Linux
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python desktop.py        # or ./run.sh (creates the venv on first run)
```

```bat
:: Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python desktop.py
```

In the window: **Select PDF…** → **Process and save as…** → choose where to save
(suggested `*_1-label-per-page.pdf`).

> Personal-use project. Always test a sample before batch-printing — changes to
> Shopee's label layout can affect the cropping.
