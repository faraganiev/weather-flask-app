from flask import Flask, request, render_template, make_response, Response
from uuid import uuid4
import json

from weather_api import get_weather_for_city
from history_store import log_city_search, get_city_stats, get_user_stats

app = Flask(__name__)

@app.before_request
def ensure_user_id():
    """Устанавливает request.user_id из cookie или генерирует новый"""
    if not request.cookies.get("user_id"):
        request.user_id = str(uuid4())
    else:
        request.user_id = request.cookies.get("user_id")

@app.route("/", methods=["GET", "POST"])
def index():
    remembered_city = request.cookies.get("last_city")
    user_id = request.user_id
    weather = None
    city = None
    show_remembered = request.method == "GET" and remembered_city is not None

    if request.method == "POST":
        city = request.form.get("city")
        if city:
            weather = get_weather_for_city(city)
            log_city_search(city, user_id)

            response = make_response(render_template("index.html", weather=weather, city=city, remembered_city=None))
            if city.lower() != (remembered_city or "").lower():
                response.set_cookie("last_city", city, max_age=60 * 60 * 24 * 30)
            response.set_cookie("user_id", user_id, max_age=60 * 60 * 24 * 365)
            return response

    response = make_response(render_template("index.html", weather=None, city=None, remembered_city=remembered_city if show_remembered else None))
    response.set_cookie("user_id", user_id, max_age=60 * 60 * 24 * 365)
    return response

@app.route("/api/stats", methods=["GET"])
def stats():
    """Глобальная статистика: сколько раз вводили каждый город"""
    return Response(
        json.dumps(get_city_stats(), ensure_ascii=False),
        content_type="application/json"
    )

@app.route("/api/user_stats", methods=["GET"])
def user_stats():
    """Статистика по конкретному пользователю"""
    return Response(
        json.dumps(get_user_stats(request.user_id), ensure_ascii=False),
        content_type="application/json"
    )

if __name__ == "__main__":
    app.run(debug=True)
