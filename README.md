# pdf-to-jpg

A lightweight command-line tool that converts any PDF file into JPG image(s)
using **only one dependency** — [PyMuPDF](https://pymupdf.readthedocs.io/).

---

## Table of Contents

1. [Why use this tool?](#1-why-use-this-tool)
2. [What problems does it solve?](#2-what-problems-does-it-solve)
3. [Where can it run?](#3-where-can-it-run)
4. [Prerequisites](#4-prerequisites)
5. [Input & Output limits](#5-input--output-limits)
6. [Step-by-step guide for beginners](#6-step-by-step-guide-for-beginners)
7. [All command options at a glance](#7-all-command-options-at-a-glance)
8. [Output examples](#8-output-examples)

---

## 1. Why use this tool?

PDFs are great for sharing documents, but they are **not easy to embed** in
websites, messaging apps, presentations, or social media — most of those
platforms expect image files such as JPG or PNG.

This tool bridges that gap:

- No paid software needed (unlike Adobe Acrobat).
- No internet connection required — everything runs on your computer.
- No complicated setup — one Python file, one package.
- Works on Linux, macOS, and Windows.

---

## 2. What problems does it solve?

| Situation | How this tool helps |
|---|---|
| You need to upload a PDF page to WhatsApp / Instagram | Convert to JPG first |
| You want to preview PDF pages in a web browser without a PDF plugin | Serve as images instead |
| You need to embed a PDF page into a Word / PowerPoint document | Insert the JPG version |
| You want to archive a PDF as flat images (no selectable text) | Rasterise each page |
| You want one long scrollable image of a multi-page document | Combine all pages into one tall JPG |
| A downstream system only accepts images, not PDFs | Batch-convert with a single command |

---

## 3. Where can it run?

| Platform | Supported |
|---|---|
| **Linux** (Ubuntu, Debian, Fedora, Arch, etc.) | ✅ Yes |
| **macOS** (Intel & Apple Silicon) | ✅ Yes |
| **Windows** (10 / 11) | ✅ Yes |
| Any system with **Python 3.8+** installed | ✅ Yes |

> The tool uses only standard Python libraries + PyMuPDF.  
> No GUI, no browser, no cloud service is needed.

---

## 4. Prerequisites

### 4.1 Install Python 3

If Python is not already installed on your computer:

- **Linux (Ubuntu / Debian)**
  ```bash
  sudo apt update && sudo apt install python3 python3-pip
  ```

- **macOS**
  ```bash
  brew install python
  ```
  *(Install [Homebrew](https://brew.sh) first if you don't have it.)*

- **Windows**
  1. Go to <https://www.python.org/downloads/>
  2. Download the latest **Python 3.x** installer.
  3. Run it and **tick "Add Python to PATH"** before clicking Install.

Verify Python is installed:
```bash
python3 --version        # Linux / macOS
python  --version        # Windows
```

---

### 4.2 Set up a virtual environment and install PyMuPDF

> **Why a virtual environment?**  
> Installing packages directly (`pip install`) writes files into your global
> Python installation. This can break other tools on your system over time.  
> A **virtual environment** is an isolated, throwaway Python sandbox — safe,
> clean, and easy to delete if something goes wrong.

#### Linux / macOS

```bash
# 1. Go to the project folder
cd /path/to/pdf-to-jpg

# 2. Create the virtual environment (only needed once)
python3 -m venv myenv

# 3. Activate it  ← you must do this every time you open a new terminal
source myenv/bin/activate

# 4. Install the only dependency
pip install pymupdf
```

You will see `(myenv)` at the start of your prompt when the environment is active.

#### Windows (Command Prompt)

```cmd
:: 1. Go to the project folder
cd C:\Users\YourName\pdf-to-jpg

:: 2. Create the virtual environment (only needed once)
python -m venv myenv

:: 3. Activate it  ← you must do this every time you open a new terminal
myenv\Scripts\activate.bat

:: 4. Install the only dependency
pip install pymupdf
```

#### Windows (PowerShell)

```powershell
# 1. Go to the project folder
cd C:\Users\YourName\pdf-to-jpg

# 2. Create the virtual environment (only needed once)
python -m venv myenv

# 3. Activate it  ← you must do this every time you open a new terminal
myenv\Scripts\Activate.ps1

# 4. Install the only dependency
pip install pymupdf
```

> **PowerShell note:** if you see a "running scripts is disabled" error, run
> this once as Administrator and try again:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

#### Verify the installation

```bash
python3 -c "import fitz; print(fitz.__doc__)"   # Linux / macOS
python  -c "import fitz; print(fitz.__doc__)"   # Windows
```
You should see a short description of PyMuPDF — that means it is working.

#### Deactivate or exit from the virtual environment when you are done with PDF to JPG conversion (optional)

> You can either run `deactivate` to exit the virtual environment cleanly,
> or simply **close the terminal / CMD window** — both are perfectly safe.

```bash
deactivate
```

---

### 4.3 Download the script

Save [pdf-to-jpg.py](pdf-to-jpg.py) **into the same folder** as your virtual
environment, for example:

```
Linux / macOS
  /path/to/pdf-to-jpg/
  ├── myenv/            ← virtual environment
  └── pdf-to-jpg.py      ← the script

Windows
  C:\Users\YourName\pdf-to-jpg\
  ├── myenv\            ← virtual environment
  └── pdf-to-jpg.py      ← the script
```

---

## 5. Input & Output limits

### Input file

| Property | Details |
|---|---|
| **Format** | `.pdf` only |
| **Number of pages** | No hard limit — tested up to hundreds of pages |
| **PDF version** | PDF 1.0 – 2.0 (all modern PDFs) |
| **Protected / encrypted PDFs** | ❌ Not supported — the PDF must be unlocked |
| **Scanned image PDFs** | ✅ Supported (they render just like any other PDF) |
| **CMYK / grayscale colour PDFs** | ✅ Supported — automatically converted to RGB |

### Output files

| Property | Details |
|---|---|
| **Format** | JPEG (`.jpg`) |
| **Default resolution** | 150 DPI — good for screen viewing |
| **Maximum resolution** | Limited only by your available RAM |
| **Quality range** | 1 (lowest, smallest file) to 100 (highest, largest file) |
| **Default quality** | 95 — near-lossless |
| **Combined image size** | For a combined file: height = sum of all page heights at chosen DPI |

#### Memory rule of thumb for combined mode

```
RAM used ≈ (width_px × total_height_px × 3 bytes) × ~2
```

Example — 10 A4 pages at 150 DPI (≈ 1240 × 1754 px each):
```
1240 × 17540 × 3 × 2 ≈ 124 MB RAM
```
At 300 DPI the same document uses ~4× more RAM (~500 MB).
If you run out of memory, use **per-page mode** (`-p`) instead.

---

## 6. Step-by-step guide for beginners

### Step 1 — Open a terminal

- **Windows:** Press `Win + R`, type `cmd`, press Enter.
- **macOS:** Press `Cmd + Space`, type `Terminal`, press Enter.
- **Linux:** Press `Ctrl + Alt + T`.

---

### Step 2 — Navigate to the project folder and activate the environment

> ⚠️ You **must** activate the virtual environment every time you open a new
> terminal. Without this, Python will not find PyMuPDF.

```bash
# Linux / macOS
cd /path/to/pdf-to-jpg
source myenv/bin/activate
```

```cmd
:: Windows (Command Prompt)
cd C:\Users\YourName\pdf-to-jpg
myenv\Scripts\activate.bat
```

```powershell
# Windows (PowerShell)
cd C:\Users\YourName\pdf-to-jpg
myenv\Scripts\Activate.ps1
```

Your prompt will change to show `(myenv)` — this confirms the environment is active:

```
(myenv) user@machine:~/pdf-to-jpg$        ← Linux / macOS
(myenv) C:\Users\YourName\pdf-to-jpg>     ← Windows
```

---

### Step 3 — Run the script

**Most common use — all pages combined into one JPG:**
```bash
python3 pdf-to-jpg.py myfile.pdf           # Linux / macOS
python  pdf-to-jpg.py myfile.pdf           # Windows
```
This creates a folder called `myfile/` containing `myfile.jpg`.

---

**Get one JPG per page:**
```bash
python3 pdf-to-jpg.py myfile.pdf -p
```
This creates `myfile/myfile_1.jpg`, `myfile/myfile_2.jpg`, etc.

---

**Higher quality scan (300 DPI, quality 100):**
```bash
python3 pdf-to-jpg.py myfile.pdf --dpi 300 --quality 100
```

---

**Save to a specific folder with a custom file name:**
```bash
python3 pdf-to-jpg.py myfile.pdf my_output_folder --name invoice
```
Output: `my_output_folder/invoice.jpg`

---

**See all available options:**
```bash
python3 pdf-to-jpg.py --help
```

---

### Step 4 — Deactivate or exit from the virtual environment when you are done with PDF to JPG conversion (optional)

```bash
deactivate
```

This exits the virtual environment and returns your terminal to the normal system Python.

> **Tip:** You don't have to run `deactivate` — you can also just **close the
> terminal / CMD window** directly. Either way is perfectly safe.

---

## 7. All command options at a glance

```
usage: pdf-to-jpg.py [-h] [-p] [--name NAME] [--dpi DPI] [--quality QUALITY]
                    pdf_path [output_folder]

positional arguments:
  pdf_path              Path to the PDF file you want to convert
  output_folder         (Optional) Folder to save images in
                        Default: a new folder named after the PDF

optional arguments:
  -h, --help            Show this help message and exit
  -p, --per-page        Save one JPG per page instead of one combined image
  --name NAME           Custom base name for output files (default: PDF name)
  --dpi  DPI            Image resolution in DPI (default: 150)
  --quality QUALITY     JPEG quality from 1 to 100 (default: 95)
```

---

## 8. Output examples

```
# Input
myfile.pdf  (3 pages)

# Default — combined
python3 pdf-to-jpg.py myfile.pdf
└── myfile/
    └── myfile.jpg          ← all 3 pages stacked into one tall image

# Per-page
python3 pdf-to-jpg.py myfile.pdf -p
└── myfile/
    ├── myfile_1.jpg
    ├── myfile_2.jpg
    └── myfile_3.jpg

# Custom folder and name, per-page
python3 pdf-to-jpg.py myfile.pdf output_dir -p --name report
└── output_dir/
    ├── report_1.jpg
    ├── report_2.jpg
    └── report_3.jpg
```

---

## Troubleshooting

| Error message | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'fitz'` | Virtual environment not active, or PyMuPDF not installed | Activate the environment first (`source myenv/bin/activate`), then `pip install pymupdf` |
| `running scripts is disabled` (Windows PowerShell) | PowerShell execution policy blocks scripts | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` once as Administrator |
| `myenv\Scripts\activate.bat` not found | Virtual environment was not created | Run `python -m venv myenv` inside the project folder |
| `FileNotFoundError: PDF not found` | Wrong path to the PDF file | Double-check the filename and that you are in the right folder |
| Out of memory / crash on large PDF | Combined image too large for RAM | Use `-p` per-page mode instead |
| Script not found | Wrong working directory | `cd` to the folder containing `pdf-to-jpg.py` |

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL v3)**.

You are free to use, modify, and distribute this code, but any modified version must also be released under AGPL v3 with source code made available.  
See the [LICENSE](LICENSE) file for full details.
