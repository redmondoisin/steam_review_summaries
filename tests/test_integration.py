import pytest
from typing import List, Dict
from app import get_app_id_by_name, get_reviews, summarize_reviews
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.mark.integration
def test_integration_csgo() -> None:
    # Test using "Counter-Strike: Global Offensive" which has app ID "730"
    game_name: str = "Counter-Strike: Global Offensive"
    app_id: str = get_app_id_by_name(game_name)
    # Ensure we got a valid app id
    assert app_id != "", "App ID should not be empty for CS:GO"
    
    reviews: List[Dict] = get_reviews(app_id, max_reviews=20)
    # Check that we retrieved some reviews
    assert len(reviews) > 0, "Should retrieve at least one review for CS:GO"
    
    summary: str = summarize_reviews(reviews)
    # The summary should be non-empty and should not indicate missing content.
    assert summary, "Summary should not be empty"
    assert "No review content available." not in summary, "Summary should be meaningful"
    print("CS:GO summary:", summary)

@pytest.mark.integration
def test_integration_tf2() -> None:
    # Test using "Team Fortress 2" which is known to have many reviews.
    game_name: str = "Team Fortress 2"
    app_id: str = get_app_id_by_name(game_name)
    assert app_id != "", "App ID should not be empty for TF2"
    
    reviews: List[Dict] = get_reviews(app_id, max_reviews=20)
    assert len(reviews) > 0, "Should retrieve at least one review for TF2"
    
    summary: str = summarize_reviews(reviews)
    assert summary, "Summary should not be empty"
    assert "No review content available." not in summary, "Summary should be meaningful"
    print("TF2 summary:", summary)
