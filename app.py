import io
import tempfile
from pathlib import Path

import chess
import chess.pgn
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Chess Image to PGN", page_icon="♟️", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1120px; padding-top: 2rem;}
.hero {padding: 1.4rem 1.6rem; border: 1px solid rgba(128,128,128,.25); border-radius: 18px; margin-bottom: 1rem;}
.muted {opacity: .72;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>♟ Chess Image to PGN</h1><p class="muted">Upload a chessboard image, recognize its position, verify the FEN, and export a PGN file.</p></div>', unsafe_allow_html=True)

@st.cache_resource
def load_predictor():
    from chessvision import BoardPredictor
    return BoardPredictor()

def render_board(board: chess.Board):
    """Render a simple Unicode board preview."""
    symbols = {
        "K":"♔", "Q":"♕", "R":"♖", "B":"♗", "N":"♘", "P":"♙",
        "k":"♚", "q":"♛", "r":"♜", "b":"♝", "n":"♞", "p":"♟"
    }
    rows = []
    for rank in range(7, -1, -1):
        cells = []
        for file in range(8):
            piece = board.piece_at(chess.square(file, rank))
            cells.append(symbols[piece.symbol()] if piece else "·")
        rows.append(f"{rank+1}  " + "　".join(cells))
    return "\n".join(rows) + "\n   a　b　c　d　e　f　g　h"

def make_pgn(fen: str, event: str, white: str, black: str, result: str):
    board = chess.Board(fen)
    game = chess.pgn.Game()
    game.setup(board)
    game.headers["Event"] = event or "Position from Image"
    game.headers["White"] = white or "White"
    game.headers["Black"] = black or "Black"
    game.headers["Result"] = result
    exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)
    return game.accept(exporter) + "\n"

if "recognized_fen" not in st.session_state:
    st.session_state.recognized_fen = None
if "source_name" not in st.session_state:
    st.session_state.source_name = "chessboard"

uploaded = st.file_uploader("Upload a chessboard image", type=["png", "jpg", "jpeg", "webp"])
if uploaded:
    try:
        image = Image.open(uploaded).convert("RGB")
        st.session_state.source_name = Path(uploaded.name).stem
        left, right = st.columns([1.05, 1])
        with left:
            st.image(image, caption="Uploaded image", use_container_width=True)
        with right:
            st.markdown("#### Recognition")
            st.caption("The open-source ChessVision model runs locally on your machine after its model files are installed/cached.")
            if st.button("🔍 Recognize chess position", type="primary", use_container_width=True):
                try:
                    from chessvision import Orientation, Turn
                    predictor = load_predictor()
                    suffix = Path(uploaded.name).suffix or ".png"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded.getvalue())
                        tmp_path = tmp.name
                    try:
                        prediction = predictor.predict(
                            tmp_path,
                            orientation=Orientation.AUTO,
                            turn=Turn.AUTO,
                            castling="auto",
                        )
                        st.session_state.recognized_fen = prediction.fen
                        st.success("Position recognized. Please verify the board and metadata below.")
                    finally:
                        Path(tmp_path).unlink(missing_ok=True)
                except Exception as e:
                    st.error(f"Recognition failed: {e}")
                    st.info("Try a clear, straight-on image showing the complete 8×8 board. You can also paste a FEN manually below.")
    except Exception as e:
        st.error(f"Could not open image: {e}")

st.divider()
st.subheader("2. Verify or edit the position")

default_fen = st.session_state.recognized_fen or chess.STARTING_FEN
fen_input = st.text_area(
    "FEN (editable)",
    value=default_fen,
    height=90,
    help="The model predicts piece placement and position metadata. Correct anything that looks wrong before exporting."
)

try:
    board = chess.Board(fen_input.strip())
    if not board.is_valid():
        st.warning("This FEN parses, but the position is not fully legal. Check king placement, checks, pawns and castling rights.")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### Board preview")
        st.code(render_board(board), language=None)
        st.caption("White at the bottom · Files a–h · Ranks 1–8")
    with c2:
        st.markdown("#### Position details")
        st.write("**Side to move:**", "White" if board.turn else "Black")
        st.write("**Castling rights:**", board.castling_xfen() or "None")
        st.write("**En passant:**", chess.square_name(board.ep_square) if board.ep_square is not None else "None")
        st.write("**Legal position:**", "Yes" if board.is_valid() else "Needs review")
except Exception as e:
    board = None
    st.error(f"Invalid FEN: {e}")

st.divider()
st.subheader("3. Export PGN")
st.caption("A single image represents one position, not the moves that led to it. The exported PGN therefore stores the position as its starting position and contains no historical moves.")
with st.form("export_form"):
    a, b = st.columns(2)
    with a:
        event = st.text_input("Event", "Position from Image")
        white = st.text_input("White player", "White")
    with b:
        black = st.text_input("Black player", "Black")
        result = st.selectbox("Result", ["*", "1-0", "0-1", "1/2-1/2"])
    submitted = st.form_submit_button("⬇ Generate PGN", type="primary", use_container_width=True)

if submitted:
    try:
        export_board = chess.Board(fen_input.strip())
        if not export_board.is_valid():
            st.error("Please correct the invalid position before exporting.")
        else:
            pgn_text = make_pgn(fen_input.strip(), event, white, black, result)
            st.success("PGN generated successfully.")
            st.code(pgn_text, language="pgn")
            st.download_button(
                "Download .pgn file",
                data=pgn_text.encode("utf-8"),
                file_name=f"{st.session_state.source_name or 'chess-position'}.pgn",
                mime="application/x-chess-pgn",
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"Could not generate PGN: {e}")

with st.expander("Recognition limitations and tips"):
    st.markdown("""
    - Use a clear image with all 64 squares visible.
    - Screenshots and flat chess diagrams are usually easier than angled photographs.
    - Reflections, hands covering pieces, unusual piece sets and rotated boards can reduce accuracy.
    - Always verify the recognized FEN. Side to move, castling rights and en-passant state may not be knowable from a static image alone.
    - This app exports a PGN containing a FEN starting position. It cannot reconstruct earlier moves from one still image.
    """)
