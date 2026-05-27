import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from apps.knowledge import rag_service

questions = [
    "Comment fertiliser le riz ?",
    "Comment lutter contre les maladies du riz ?",
    "Quand récolter le riz ?",
]

print("docs_phrases_before", len(rag_service._phrases))

for question in questions:
    started_at = time.perf_counter()
    try:
        answer, sources, score = rag_service.get_rag_answer("benchmark", question, "free")
        status = "ok"
    except Exception as exc:
        status = f"error:{type(exc).__name__}:{exc}"
        sources = []
        score = 0
    elapsed = time.perf_counter() - started_at
    print(
        "question=", question,
        "status=", status,
        "elapsed_s=", round(elapsed, 3),
        "sources=", len(sources),
        "score=", score,
        "phrases=", len(rag_service._phrases),
    )
