import re
import json
import pytest
from typing import List, Dict, Any
from app import (
    clean_text,
    get_app_id_by_name,
    get_reviews,
    summarize_reviews,
    app
)

# --- Dummy Summarizer and Tokenizer for Testing ---

def dummy_summarizer(text: str, max_length: int, min_length: int, do_sample: bool, truncation: bool) -> List[Dict[str, str]]:
    # This dummy function always returns a constant summary.
    return [{"summary_text": "Dummy summary."}]

class DummyTokenizer:
    model_max_length: int = 100  # Set a low max length to force chunking

    def encode(self, text: str, truncation: bool = False) -> List[int]:
        # Simulate tokenization: one token per word.
        return list(range(len(text.split())))

    def decode(self, token_ids: List[int], skip_special_tokens: bool, clean_up_tokenization_spaces: bool) -> str:
        # Simply return 'word' repeated as many times as there are tokens.
        return " ".join(["word"] * len(token_ids))

# A dummy summarizer factory that counts calls and returns a unique summary per chunk.
def dummy_summarizer_counter_factory():
    call_count = {"count": 0}
    def dummy_summarizer_fn(text: str, max_length: int, min_length: int, do_sample: bool, truncation: bool) -> List[Dict[str, str]]:
        call_count["count"] += 1
        return [{"summary_text": f"Chunk {call_count['count']} summary."}]
    return dummy_summarizer_fn, call_count

# --- Tests for Utility Functions ---

def test_clean_text() -> None:
    input_text: str = "This is a test – with non-ascii: ü, é, ñ.   Extra   spaces."
    expected: str = "This is a test - with non-ascii: , , . Extra spaces."
    cleaned: str = clean_text(input_text)
    # We check that no non-ascii reapp and extra spaces are reduced.
    assert all(ord(ch) < 128 for ch in cleaned)
    assert "  " not in cleaned

def test_get_app_id_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_html: str = """
    <html>
      <body>
        <a class="search_result_row ds_collapse_flag" href="https://store.steampowered.com/app/123456/Dummy_Game/">
          Dummy result
        </a>
      </body>
    </html>
    """
    class DummyResponse:
        def __init__(self, text: str) -> None:
            self.text = text

    def dummy_get(url: str) -> DummyResponse:
        return DummyResponse(dummy_html)
    
    monkeypatch.setattr("app.requests.get", dummy_get)
    app_id: str = get_app_id_by_name("Dummy Game")
    assert app_id == "123456"

def test_get_reviews(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_json: Dict[str, Any] = {
        "reviews": [
            {"review": "Great game!"},
            {"review": "Really fun experience."}
        ],
        "cursor": "dummy_cursor"
    }
    class DummyResponse:
        def json(self) -> Dict[str, Any]:
            return dummy_json

    def dummy_get(url: str, params: dict) -> DummyResponse:
        return DummyResponse()

    monkeypatch.setattr("app.requests.get", dummy_get)
    reviews: List[Dict[str, str]] = get_reviews("123456", max_reviews=2)
    assert isinstance(reviews, list)
    assert len(reviews) == 2
    assert reviews[0]["review"] == "Great game!"

# --- Tests for Summarization Functionality ---

def test_summarize_reviews_simple(monkeypatch: pytest.MonkeyPatch) -> None:
    # Use our simple dummy summarizer that always returns the same summary.
    monkeypatch.setattr("app.pipeline", lambda task, model: dummy_summarizer)
    monkeypatch.setattr("app.AutoTokenizer.from_pretrained", lambda model: DummyTokenizer())
    sample_reviews: List[Dict[str, str]] = [{"review": "This game is awesome!"}, {"review": "Loved it."}]
    summary: str = summarize_reviews(sample_reviews)
    assert "Dummy summary." in summary

def test_summarize_reviews_long_text(monkeypatch: pytest.MonkeyPatch) -> None:
    # This test creates a long review text that forces the summarizer to split input into multiple chunks.
    # We'll use a dummy tokenizer with a low max length and a dummy summarizer that counts calls.
    dummy_summarizer_fn, call_count = dummy_summarizer_counter_factory()
    monkeypatch.setattr("app.pipeline", lambda task, model: dummy_summarizer_fn)
    monkeypatch.setattr("app.AutoTokenizer.from_pretrained", lambda model: DummyTokenizer())
    
    # Create a long review text with 250 words (tokens).
    long_text: str = "word " * 250
    sample_reviews: List[Dict[str, str]] = [{"review": long_text}]
    summary: str = summarize_reviews(sample_reviews)
    # Since DummyTokenizer.model_max_length is 100 and safety margin is (offset 2 + 50) = 52,
    # max_chunk_tokens = 100 - 52 = 48. 250 tokens should result in at least ceil(250/48) = 6 chunks.
    assert call_count["count"] >= 6
    # Check that the summary includes distinct chunk summaries.
    for i in range(1, call_count["count"] + 1):
        assert f"Chunk {i} summary." in summary

# --- Tests for Flask Routes ---

@pytest.fixture
def client() -> Any:
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index_get(client: Any) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"Steam Game Review Summarizer" in response.data

def test_index_post_game_not_found(monkeypatch: pytest.MonkeyPatch, client: Any) -> None:
    monkeypatch.setattr("app.get_app_id_by_name", lambda game_name: "")
    response = client.post("/", data={"game_name": "Nonexistent Game"})
    assert b"Game not found." in response.data

def test_index_post_success(monkeypatch: pytest.MonkeyPatch, client: Any) -> None:
    monkeypatch.setattr("app.get_app_id_by_name", lambda game_name: "123456")
    monkeypatch.setattr("app.get_reviews", lambda app_id, max_reviews=50: [{"review": "Great game!"}])
    monkeypatch.setattr("app.summarize_reviews", lambda reviews, max_length=150, min_length=50: "Dummy summary of reviews.")
    response = client.post("/", data={"game_name": "Dummy Game"})
    assert b"Dummy summary of reviews." in response.data
