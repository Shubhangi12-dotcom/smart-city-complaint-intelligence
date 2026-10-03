import os

from dotenv import load_dotenv
from google import genai
import markdown

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. "
        "Please add it to your .env file."
    )


client = genai.Client(
    api_key=API_KEY
)


def generate_city_insights(stats, complaints):

    # We only send complaint-management information.
    # Citizen names and contact details are intentionally excluded.
    complaint_data = []

    for complaint in complaints[:20]:

        complaint_data.append({
            "category": complaint["category"],
            "priority": complaint["priority"],
            "status": complaint["status"],
            "location": complaint["location"],
            "complaint": complaint["complaint"]
        })


    prompt = f"""
You are an AI assistant for a Smart City complaint management dashboard.

Analyze the following complaint statistics and complaint records.

Statistics:
{stats}

Complaint records:
{complaint_data}

Create a concise administrative insight report.

Include:
1. Overall situation
2. Most common complaint category
3. Priority concerns
4. Status and resolution situation
5. Location pattern if visible
6. Two practical areas the administration could review

Rules:
- Use only facts directly supported by the provided data.
- Do not infer that complaints come from the same location unless their
  recorded location values explicitly match.
- Do not infer that complaints are related just because their wording
  is similar.
- Clearly distinguish recorded facts from observations.
- If location data is missing, explicitly say that location information
  is unavailable rather than guessing.
- Do not mention citizen names, phone numbers, email addresses, or other
  personal information.
- Do not invent trends, causes, deadlines, or actions not supported by
  the data.
- Keep the report professional and concise.
- Do not use Markdown symbols such as #, *, **, or bullet characters.
- Use plain text headings and numbered sections only.
- Keep headings on separate lines.
"""


    # Try the latest Flash model first.
    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite"
    ]


    last_error = None


    for model_name in models_to_try:

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            return markdown.markdown(
    response.text,
    extensions=["extra"]
)


        except Exception as error:

            last_error = error

            print(
                f"Model {model_name} failed: {error}"
            )


    raise RuntimeError(
        "All configured Gemini models failed. "
        f"Last error: {last_error}"
    )