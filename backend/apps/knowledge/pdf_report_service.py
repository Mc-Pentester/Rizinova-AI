# apps/knowledge/pdf_report_service.py
from weasyprint import HTML
from .report_service import get_expert_report
import tempfile

def generate_b2b_pdf(user_id, query, farm_data=None, country=None,
                     region=None, variety=None, doc_type=None, plan="free"):
    report = get_expert_report(
        user_id=user_id,
        query=query,
        farm_data=farm_data,
        country=country,
        region=region,
        variety=variety,
        doc_type=doc_type,
        plan=plan
    )

    html = "<h1>Rapport Riziculture B2B</h1>"
    html += f"<h2>Question : {query}</h2>"
    html += "<h3>Sources :</h3><ul>"
    for src in report["sources"]:
        html += f"<li>{src}</li>"
    html += "</ul>"

    html += "<h3>Contenu :</h3>"
    for chunk in report["rag_chunks"]:
        html += f"<p>{chunk}</p>"

    html += "<h3>Indicateurs Agronomiques :</h3>"
    html += f"<p>Yield gap : {report['agronomy_risk']['yield_gap']}</p>"
    html += f"<p>Recommendation : {report['agronomy_risk']['recommendation']}</p>"

    html += "<h3>Indicateurs Financiers :</h3>"
    html += f"<p>Coût total : {report['financials']['cost_total']}</p>"
    html += f"<p>Revenu total : {report['financials']['revenue_total']}</p>"
    html += f"<p>ROI : {report['financials']['roi']}</p>"

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    HTML(string=html).write_pdf(tmp_file.name)
    return tmp_file.name