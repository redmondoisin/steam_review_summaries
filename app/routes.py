from flask import render_template_string, request
from app import app
from app.summarizer import get_app_id_by_name, get_reviews, summarize_reviews

TEMPLATE: str = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Steam Game Review Summarizer</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <div class="container">
    <h1>Steam Game Review Summarizer</h1>
    <form method="post">
      <label for="game_name">Enter Game Name:</label>
      <input type="text" name="game_name" id="game_name" value="{{ game_name }}">
      <input type="submit" value="Get Summary">
    </form>
    {% if summary %}
      <h2>Summary:</h2>
      <div class="summary">{{ summary }}</div>
    {% endif %}
  </div>
</body>
</html>
"""

@ app.route("/", methods=["GET", "POST"])
def index() -> str:
    summary: str = ""
    game_name: str = ""
    if request.method == "POST":
        game_name = request.form.get("game_name", "").strip()
        app_id: str = get_app_id_by_name(game_name)
        if not app_id:
            summary = "Game not found."
        else:
            reviews = get_reviews(app_id, max_reviews=50)
            if not reviews:
                summary = "No reviews found for this game."
            else:
                print(f"App ID for '{game_name}': {app_id}, Reviews found: {len(reviews)}")
                summary = summarize_reviews(reviews, bullet=True)
    return render_template_string(TEMPLATE, summary=summary, game_name=game_name)
