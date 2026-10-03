from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

import joblib

from priority import detect_priority

from city_rules import (
    get_department,
    get_response_time
)

from duplicate_detector import (
    find_similar_complaint
)
from ai_insights import generate_city_insights

from database import (
    create_table,
    add_complaint,
    get_all_complaints,
    get_filtered_complaints,
    get_statistics,
    get_dashboard_insights,
    update_status
)


app = Flask(__name__)


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "complaint_classifier.pkl"

VECTORIZER_PATH = BASE_DIR / "models" / "tfidf_vectorizer.pkl"


# --------------------------------------------------
# Load trained ML model
# --------------------------------------------------

model = joblib.load(MODEL_PATH)

vectorizer = joblib.load(VECTORIZER_PATH)


# --------------------------------------------------
# Create / update database
# --------------------------------------------------

create_table()


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# Complaint prediction
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    citizen_name = request.form.get(
        "citizen_name",
        ""
    ).strip()

    contact = request.form.get(
        "contact",
        ""
    ).strip()

    location = request.form.get(
        "location",
        ""
    ).strip()

    complaint = request.form.get(
        "complaint",
        ""
    ).strip()


    if not citizen_name:

        return render_template(
            "index.html",
            error="Please enter your name."
        )


    if not location:

        return render_template(
            "index.html",
            error="Please enter the complaint location."
        )


    if not complaint:

        return render_template(
            "index.html",
            error="Please enter a complaint."
        )


    # ML classification

    complaint_vector = vectorizer.transform(
        [complaint]
    )

    prediction = model.predict(
        complaint_vector
    )[0]


    # Priority

    priority = detect_priority(
        complaint
    )


    # Department

    department = get_department(
        prediction
    )


    # Estimated response time

    response_time = get_response_time(
        priority
    )


    # Duplicate detection

    existing_complaints = get_all_complaints()

    duplicate = find_similar_complaint(
        complaint,
        existing_complaints,
        vectorizer
    )


    # Save complaint

    complaint_id = add_complaint(
        complaint=complaint,
        category=prediction,
        priority=priority,
        citizen_name=citizen_name,
        contact=contact,
        location=location,
        department=department,
        response_time=response_time
    )


    return render_template(
        "index.html",
        prediction=prediction,
        priority=priority,
        complaint=complaint,
        complaint_id=complaint_id,
        citizen_name=citizen_name,
        contact=contact,
        location=location,
        department=department,
        response_time=response_time,
        duplicate=duplicate
    )


# --------------------------------------------------
# Admin dashboard
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    search = request.args.get(
        "search",
        ""
    ).strip()

    category = request.args.get(
        "category",
        ""
    ).strip()

    priority = request.args.get(
        "priority",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()


    complaints = get_filtered_complaints(
        search=search,
        category=category,
        priority=priority,
        status=status
    )


    stats = get_statistics()

    insights = get_dashboard_insights()


    categories = [
        "Waste Management",
        "Street Light",
        "Roads & Potholes",
        "Water Supply",
        "Drainage & Sewerage",
        "Public Safety"
    ]


    return render_template(
        "dashboard.html",
        complaints=complaints,
        stats=stats,
        insights=insights,
        categories=categories,
        search=search,
        selected_category=category,
        selected_priority=priority,
        selected_status=status
    )


# --------------------------------------------------
# Generate AI city insights
# --------------------------------------------------

@app.route("/generate-insights", methods=["POST"])
def generate_insights():

    complaints = get_all_complaints()

    stats = get_statistics()

    ai_report = generate_city_insights(
        stats,
        complaints
    )

    insights = get_dashboard_insights()

    categories = [
        "Waste Management",
        "Street Light",
        "Roads & Potholes",
        "Water Supply",
        "Drainage & Sewerage",
        "Public Safety"
    ]

    return render_template(
        "dashboard.html",
        complaints=complaints,
        stats=stats,
        insights=insights,
        categories=categories,
        search="",
        selected_category="",
        selected_priority="",
        selected_status="",
        ai_report=ai_report
    )


# --------------------------------------------------
# Update complaint status
# --------------------------------------------------

@app.route(
    "/update-status/<int:complaint_id>",
    methods=["POST"]
)
def update_complaint_status(complaint_id):

    new_status = request.form.get(
        "status"
    )


    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]


    if new_status in allowed_statuses:

        update_status(
            complaint_id,
            new_status
        )


    return redirect(
        url_for("dashboard")
    )


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)