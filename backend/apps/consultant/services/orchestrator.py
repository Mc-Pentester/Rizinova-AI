# apps/knowledge/orchestrator.py

from typing import Dict, Any, List
from django.utils.crypto import get_random_string
from django.utils import timezone

from .intent import detect_intent
from .clarification import check_missing_fields
from .memory import ConversationMemory

from ..engines.yield_engine import YieldEngine
from ..engines.economic_engine import EconomicEngine
from ..engines.risk_engine import RiskEngine

from apps.knowledge.rag_service import get_rag_answer
from .response_evaluator import ResponseEvaluator
from apps.knowledge.auto_rag import run_full_pipeline, audit_base, missing_topics, prepare_new_documents


class ConsultantOrchestrator:

    def __init__(self, memory_turns: int = 3):
        self.memory = ConversationMemory()
        self.yield_engine = YieldEngine()
        self.economic_engine = EconomicEngine()
        self.risk_engine = RiskEngine()
        self.memory_turns = memory_turns  # nombre de tours à utiliser pour contexte RAG

    # ===============================
    # MAIN ENTRY POINT
    # ===============================
    def handle(
        self,
        user,
        query: str,
        data: Dict[str, Any],
        plan: str = "free",
        new_files: List[str] = [],
    ) -> Dict[str, Any]:

        session_id = data.get("session_id") or get_random_string(16)

        # 1️⃣ Save user message
        self.memory.save_message(user, session_id, "user", query)

        # 2️⃣ Retrieve history
        history = self.memory.get_history(user, session_id)

        # 3️⃣ Detect intent
        intent = detect_intent(query)

        # 4️⃣ Check missing required fields
        missing_fields = check_missing_fields(intent, data)

        if missing_fields:
            response = {
                "status": "need_more_info",
                "intent": intent,
                "session_id": session_id,
                "missing_fields": missing_fields,
                "message": self._generate_missing_fields_message(missing_fields),
            }

            self.memory.save_message(user, session_id, "assistant", str(response))
            return response

        # 5️⃣ Route by intent
        if intent == "yield_simulation":
            result = self._handle_yield(data)

        elif intent == "economic_analysis":
            result = self._handle_economic(data)

        else:
            result = self._handle_general_knowledge(user, query, plan, new_files)

        # 6️⃣ Risk evaluation (if agronomic context exists)
        risk = self._evaluate_risk(data)

        # 7️⃣ Build final structured response
        final_response = {
            "status": "success",
            "intent": intent,
            "session_id": session_id,
            "analysis": result,
            "risk": risk,
            "conversation_depth": len(history),
        }

        # 8️⃣ Save assistant response
        self.memory.save_message(user, session_id, "assistant", str(final_response))

        return final_response

    # ===============================
    # YIELD HANDLER
    # ===============================
    def _handle_yield(self, data: Dict[str, Any]) -> Dict[str, Any]:

        surface = data["surface_ha"]
        current_yield = data["current_yield"]
        improvement = data.get("improvement_percent", 15)

        simulation = self.yield_engine.simulate(
            surface=surface,
            current_yield=current_yield,
            improvement_percent=improvement,
        )

        return {
            "type": "yield_simulation",
            "simulation": simulation,
        }

    # ===============================
    # ECONOMIC HANDLER
    # ===============================
    def _handle_economic(self, data: Dict[str, Any]) -> Dict[str, Any]:

        result = self.economic_engine.analyze(
            surface=data["surface_ha"],
            yield_per_ha=data["yield_per_ha"],
            price_per_ton=data["price_per_ton"],
            cost_per_ha=data["cost_per_ha"],
        )

        return {
            "type": "economic_analysis",
            "financials": result,
        }

    # ===============================
    # GENERAL KNOWLEDGE (RAG) HANDLER
    # ===============================
    def _handle_general_knowledge(self, user, query: str, plan: str, new_files: List[str] = []) -> Dict[str, Any]:
        """
        Intègre :
        - RAG optimisé via run_full_pipeline
        - Cross-Encoder
        - Mémoire multi-tour
        - Audit et enrichissement optionnel
        """

        # Enrichissement si fichiers fournis
        if new_files:
            prepare_new_documents(new_files)

        # Inclure le contexte conversationnel multi-tour
        context_history = self._get_context_from_history(user)

        # Génération RAG optimisée
        result = run_full_pipeline(
            user_id=user.id,
            query=query,
            plan=plan,
            new_files=new_files
        )

        # Fusion du contexte historique
        if context_history:
            result["context"] = context_history + " " + result["context"]

        # Évaluation automatique
        evaluator = ResponseEvaluator()
        evaluation = evaluator.evaluate(query, result["context"])
        result["evaluation"] = evaluation

        return result

    # ===============================
    # CONTEXTE HISTORIQUE MULTI-TOUR
    # ===============================
    def _get_context_from_history(self, user) -> str:
        """
        Concatène les réponses des derniers tours pour contextualiser la question.
        """
        convs = self.memory.get_full_history(user)
        if not convs:
            return ""
        last_responses = [c["response"] for c in convs[-self.memory_turns:]]
        return " ".join(last_responses)

    # ===============================
    # RISK EVALUATION
    # ===============================
    def _evaluate_risk(self, data: Dict[str, Any]):
        irrigation = data.get("irrigation_type")
        region = data.get("region")

        risk = self.risk_engine.evaluate(
            region=region,
            irrigation_type=irrigation,
        )

        return risk

    # ===============================
    # MISSING FIELDS MESSAGE
    # ===============================
    def _generate_missing_fields_message(self, fields):
        readable = {
            "surface_ha": "Quelle est la superficie en hectares ?",
            "current_yield": "Quel est votre rendement actuel (t/ha) ?",
            "yield_per_ha": "Quel est votre rendement par hectare ?",
            "price_per_ton": "Quel est votre prix de vente par tonne ?",
            "cost_per_ha": "Quel est votre coût par hectare ?",
        }

        questions = [readable.get(f, f) for f in fields]

        return {
            "questions": questions
        }

    # ===============================
    # AUDIT DE LA BASE DE CONNAISSANCE
    # ===============================
    def audit_knowledge_base(self) -> Dict[str, Any]:
        coverage = audit_base()
        missing = missing_topics(coverage)
        return {"coverage": coverage, "missing_topics": missing}

    # ===============================
    # ENRICHISSEMENT DE LA BASE
    # ===============================
    def enrich_knowledge_base(self, new_files: List[str]):
        prepare_new_documents(new_files)