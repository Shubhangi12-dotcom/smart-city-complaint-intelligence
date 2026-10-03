from sklearn.metrics.pairwise import cosine_similarity


def find_similar_complaint(
    new_complaint,
    existing_complaints,
    vectorizer,
    threshold=0.45
):
    """
    Finds the most similar previous complaint.

    A 45% threshold is used for this prototype.
    """

    if not existing_complaints:
        return None

    existing_texts = [
        complaint["complaint"]
        for complaint in existing_complaints
        if complaint["complaint"]
    ]

    if not existing_texts:
        return None

    new_vector = vectorizer.transform([new_complaint])

    existing_vectors = vectorizer.transform(existing_texts)

    similarities = cosine_similarity(
        new_vector,
        existing_vectors
    )[0]

    best_index = similarities.argmax()

    best_score = float(similarities[best_index])

    if best_score >= threshold:

        best_complaint = existing_complaints[best_index]

        return {
            "id": best_complaint["id"],
            "category": best_complaint["category"],
            "priority": best_complaint["priority"],
            "status": best_complaint["status"],
            "similarity": round(best_score * 100, 2)
        }

    return None