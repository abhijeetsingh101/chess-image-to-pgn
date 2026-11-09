# Chess Image to PGN

A local-first web app that converts a chessboard screenshot or photo into an editable FEN and downloadable PGN.

## Features

- Upload PNG, JPG, JPEG or WebP.
- Recognize chess positions with the open-source `chessvision` Python package.
- Preview the recognized board.
- Edit/correct the FEN before export.
- Validate the position with `python-chess`.
- Export a PGN whose starting position is the recognized FEN.

## Important: FEN vs PGN

A single image contains a board position, not the move history. This app creates a PGN with a `[SetUp "1"]` and `[FEN "..."]` header and no moves. To produce a complete game PGN, you need the move list or a sequence of frames from the game.

A still image also cannot reliably reveal side to move, castling rights, en-passant target, or move counters. Always verify these fields before export.

## Requirements

- Python 3.10 or newer (Python 3.11 is a good choice).
- Internet connection for the first installation and model downloads.
- 4 GB RAM minimum; 8 GB recommended. CPU inference may take a little time.

## Windows installation

1. Extract the ZIP.
2. Open the extracted folder in Command Prompt or PowerShell.
3. Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
```

4. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Start the app:

```powershell
streamlit run app.py
```

6. Open the local URL Streamlit prints (normally http://localhost:8501).

## macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## How to use

1. Upload a chessboard image.
2. Click **Recognize chess position**.
3. Review the predicted FEN and board preview.
4. Correct the FEN if necessary.
5. Select player names and result.
6. Click **Generate PGN**, then download the `.pgn` file.

## Recognition engine

This app uses the open-source `chessvision` package (PyPI/GitHub), not a paid recognition API. The first model initialization may download model weights and dependencies. See:
- https://pypi.org/project/chessvision/
- https://github.com/harshitpawar64/chessvision

The app uses the documented `BoardPredictor.predict()` API. If a future library release changes its API, pin a compatible version or adjust the call in `app.py`.

## Deploying online

For a public deployment, use a Python host that supports Streamlit and has enough RAM for the recognition model. Streamlit Community Cloud may have resource limitations for deep-learning dependencies. A small VPS or a container host is more predictable. The recognition runs on the server, so uploaded images are sent to that server; add a privacy notice and file-size limits before public launch.

## Project structure

```text
chess_image_to_pgn/
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

## License note

Check the current licenses of `chessvision` and all transitive model/data dependencies before redistributing a hosted or commercial version.
