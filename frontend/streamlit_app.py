# frontend/streamlit_app.py
from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

import streamlit as st
import requests
from datetime import datetime
from io import BytesIO
import markdown
import re

# Try to import xhtml2pdf for PDF generation, fallback to HTML if not available
try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except ImportError:
    XHTML2PDF_AVAILABLE = False
    st.warning("⚠️ xhtml2pdf n'est pas disponible. Le téléchargement se fera en format HTML.")

# --- Page Configuration ---
st.set_page_config(
    page_title="SoilSmart par MaliAgriculture",
    page_icon="🌱",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* --- General --- */
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.main { background-color: #F9F9F6; color: #333333; }

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 0.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    overflow-y: auto;
    max-height: 90vh;
}

/* --- Mobile Header --- */
.mobile-header {
    display: none;
    text-align: center;
    background-color: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    padding: 1rem 0.5rem;
    margin-bottom: 1rem;
}
.mobile-header img { width: 80px; }
.mobile-header h1 { color: #4CAF50; font-size: 1.4rem; margin-bottom: 0.25rem; }
.mobile-header .mobile-uploader { margin-top: 0.5rem; }

/* --- Buttons --- */
.stButton>button {
    border-radius: 10px; border: 2px solid #4CAF50;
    background-color: #4CAF50; color: white;
    padding: 12px 28px; font-weight: 600;
    font-size: 1rem; width: 100%;
    box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #FFFFFF; color: #4CAF50; border-color: #4CAF50;
    transform: translateY(-2px);
}

/* --- Cards --- */
.report-card, .language-section {
    background-color: #FFFFFF; border-radius: 12px;
    padding: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
}

/* --- File Uploader --- */
[data-testid="stFileUploader"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding: 0.5rem 0 !important;
}

/* --- Mobile Responsive --- */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { display: none !important; }
    .mobile-header { display: block; }
    .main { margin-left: 0 !important; padding: 0.5rem; }
    .stButton>button { font-size: 0.9rem; padding: 10px 18px; }
    [data-testid="stFileUploader"] { width: 100% !important; padding: 0.8rem !important; }
}
</style>
""", unsafe_allow_html=True)

# --- Mobile Header ---
st.markdown("""
<div class="mobile-header">
    <img src="https://maliagriculture.com/gallery/logo%20n1.jpg?ts=1757619351">
    <h1>🌱 SoilSmart-AI</h1>
</div>
""", unsafe_allow_html=True)

# --- Sidebar (Desktop) ---
with st.sidebar:
    st.markdown("<h1 style='color: #4CAF50; font-weight: 700;'>🌱 Soil Smart </h1>", unsafe_allow_html=True)
    st.markdown("_Innovation au service de vos sols et cultures_")
    st.markdown("---")
    uploaded_file = st.file_uploader(
        "#### Téléverser un résultat d'analyse (PDF)",
        type=["pdf"],
        key="sidebar_uploader"
    )
    if uploaded_file is not None:
        st.success(f"✅ Fichier chargé : **{uploaded_file.name}**")
    st.markdown("---")
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="https://maliagriculture.com/gallery/logo%20n1.jpg?ts=1757619351" width="50">
        <div>
            <strong>© 2025 MaliAgriculture.com</strong><br>
            🌱 Smart Solution for Agriculture.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Main Page ---
st.markdown("<h1 style='text-align: center; color: #4CAF50; font-weight: 700;'>🌱 Rapport d'Analyse Agronomique et Recommandations Stratégiques</h1>", unsafe_allow_html=True)

# --- Main uploader below title (only show if no report is displayed) ---
main_uploaded_file = None
report_data = st.session_state.get('report_data')
if not (report_data and not report_data.get("error")):
    main_uploaded_file = st.file_uploader(
        "Téléverser un fichier PDF",
        type=["pdf"],
        key="main_uploader"
    )

# --- Determine which file to use (priority: main > sidebar) ---
uploaded_file = main_uploaded_file if main_uploaded_file else uploaded_file

if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'show_summaries' not in st.session_state:
    st.session_state.show_summaries = {'wo': False, 'bm': False}
if 'current_file_id' not in st.session_state:
    st.session_state.current_file_id = None

def reset_report_state():
    st.session_state.report_data = None
    st.session_state.show_summaries = {'wo': False, 'bm': False}

if uploaded_file:
    file_bytes = uploaded_file.getvalue()
    file_id = f"{uploaded_file.name}-{len(file_bytes)}"
    if st.session_state.current_file_id != file_id:
        reset_report_state()
        st.session_state.current_file_id = file_id
    if st.session_state.report_data is None:
        with st.spinner("Analyse complète en cours (FR, WO, BM)..."):
            files = {"file": (uploaded_file.name, file_bytes, "application/pdf")}
            try:
                # Use stream=True for large files to improve memory efficiency
                response = requests.post(
                    f"{API_URL}/analyze", 
                    files=files, 
                    timeout=240,
                    stream=False  # Keep False for small PDFs, set True if files are large
                )
                response.raise_for_status()  # Raise exception for HTTP errors
                if response.status_code == 200:
                    st.session_state.report_data = response.json()
                else:
                    st.error(f"Erreur de l'API: {response.text}")
                    st.session_state.report_data = {"error": True}
            except requests.exceptions.Timeout:
                st.error("⏱️ La requête a pris trop de temps. Veuillez réessayer avec un fichier plus petit.")
                st.session_state.report_data = {"error": True}
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur de connexion à l'API: {e}")
                st.session_state.report_data = {"error": True}
else:
    if st.session_state.report_data is not None or st.session_state.current_file_id is not None:
        reset_report_state()
        st.session_state.current_file_id = None

# --- Display report ---
if st.session_state.report_data and not st.session_state.report_data.get("error"):
    data = st.session_state.report_data
    st.markdown(data["report"], unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="language-section"><h2>🌐 Résumés dans d\'autres langues</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇸🇳 Afficher le résumé en Wolof"):
            st.session_state.show_summaries['wo'] = not st.session_state.show_summaries['wo']
    with col2:
        if st.button("🇲🇱 Afficher le résumé en Bambara"):
            st.session_state.show_summaries['bm'] = not st.session_state.show_summaries['bm']

    if st.session_state.show_summaries['wo']:
        with st.expander("📖 Résumé en Wolof", expanded=True):
            st.markdown(data.get("summary_wo", "Résumé non disponible."))
    if st.session_state.show_summaries['bm']:
        with st.expander("📖 Résumé en Bambara", expanded=True):
            st.markdown(data.get("summary_bm", "Résumé non disponible."))
    
    # --- Download button at the end ---
    # Format report for download (PDF format using xhtml2pdf)
    def format_report_for_pdf(data):
        """Format the report as a well-structured HTML document for PDF conversion"""
        current_date = datetime.now().strftime("%d/%m/%Y à %H:%M")
        
        # Pre-process to merge units with values in tables
        report_text = data["report"]
        
        def merge_units_in_tables(text):
            """Merge 3-column tables (Paramètre | Valeur | Unité) into 2-column tables"""
            lines = text.split('\n')
            result = []
            i = 0
            in_table = False
            
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                # Check if this line is part of a markdown table
                if '|' in stripped and stripped.startswith('|') and stripped.endswith('|'):
                    # Check if it's a separator line (|---|---|---|)
                    sep_content = stripped.replace('|', '').replace(' ', '').replace('-', '').replace(':', '')
                    if not sep_content or re.match(r'^[\-\s:]+$', stripped.replace('|', '').replace(' ', '')):
                        # Skip separator line
                        i += 1
                        continue
                    
                    # Extract cells - split by | and remove empty at start/end
                    parts = [p.strip() for p in stripped.split('|')]
                    # Remove empty strings at beginning and end
                    while parts and not parts[0]:
                        parts.pop(0)
                    while parts and not parts[-1]:
                        parts.pop()
                    
                    # Check if it's the header row with 3 columns
                    if len(parts) >= 3:
                        first_col = ' '.join(parts[0:1])
                        all_cols = ' '.join(parts).lower()
                        
                        if 'paramètre' in all_cols and 'valeur' in all_cols and 'unité' in all_cols:
                            # Replace 3-column header with 2-column header
                            result.append('| Paramètre | Valeur |')
                            result.append('|-----------|--------|')
                            in_table = True
                            i += 1
                            # Skip the separator line if next line
                            if i < len(lines):
                                next_line = lines[i].strip()
                                if '|' in next_line and re.match(r'^[\s\-\|:]+$', next_line.replace('|', '').replace(' ', '')):
                                    i += 1
                            continue
                    
                    # Check if we're inside a table and it's a data row with 3 columns
                    if in_table and len(parts) >= 3:
                        param = parts[0] if len(parts) > 0 else ''
                        valeur = parts[1] if len(parts) > 1 else ''
                        unite = parts[2] if len(parts) > 2 else ''
                        
                        # Merge value and unit
                        if unite and unite.strip():
                            valeur_unite = f"{valeur} {unite}".strip()
                        else:
                            valeur_unite = valeur.strip() if valeur else ''
                        
                        # Add 2-column row
                        result.append(f"| {param} | {valeur_unite} |")
                        i += 1
                    else:
                        # Not a 3-column table row or not in table, keep as is
                        result.append(line)
                        i += 1
                else:
                    # Not a table line - end of table if we were in one
                    if in_table:
                        in_table = False
                    result.append(line)
                    i += 1
            
            return '\n'.join(result)
        
        # Apply unit merging
        report_text = merge_units_in_tables(report_text)
        
        report_html = markdown.markdown(
            report_text, 
            extensions=['tables', 'nl2br']
        )
        
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Analyse Agronomique - SoilSmart</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: Helvetica, Arial, sans-serif;
            line-height: 1.8;
            color: #333333;
            font-size: 11pt;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 25px;
            text-align: center;
            margin-bottom: 25px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24pt;
            font-weight: bold;
            color: white;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 12pt;
            color: white;
        }}
        .content {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .summary-section {{
            background-color: #f5f5f5;
            padding: 15px;
            margin-top: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #4CAF50;
        }}
        .summary-section h3 {{
            color: #4CAF50;
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 14pt;
        }}
        h1 {{
            color: #4CAF50;
            font-size: 20pt;
            margin-top: 20px;
            margin-bottom: 15px;
        }}
        h2 {{
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 8px;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 16pt;
        }}
        h3 {{
            color: #795548;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 13pt;
        }}
        p {{
            margin-bottom: 12px;
            text-align: justify;
        }}
        ul, ol {{
            margin-bottom: 15px;
            padding-left: 30px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 10pt;
            table-layout: fixed;
        }}
        table th {{
            background-color: #4CAF50;
            color: white;
            padding: 8px 5px;
            text-align: left;
            border: 1px solid #ddd;
            font-weight: bold;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        table th:nth-child(1) {{
            width: 60%;
        }}
        table th:nth-child(2) {{
            width: 40%;
        }}
        table td {{
            padding: 8px 5px;
            border: 1px solid #ddd;
            word-wrap: break-word;
            overflow-wrap: break-word;
            vertical-align: top;
        }}
        table td:nth-child(2) {{
            text-align: center;
        }}
        table tr:nth-child(even) {{
            background-color: #f5f5f5;
        }}
        strong {{
            color: #4CAF50;
            font-weight: bold;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #666666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dddddd;
            font-size: 9pt;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌱 Rapport d'Analyse Agronomique et Recommandations Stratégiques</h1>
        <p>SoilSmart par MaliAgriculture</p>
    </div>
    
    <div class="content">
        {report_html}
    </div>
"""
        
        # Add summaries if available
        if data.get("summary_wo") or data.get("summary_bm"):
            html_content += """
    <div class="content">
        <h2>🌐 Résumés dans d'autres langues</h2>
"""
            if data.get("summary_wo"):
                summary_wo_html = markdown.markdown(
                    data.get("summary_wo", ""), 
                    extensions=['nl2br']
                )
                html_content += f"""
        <div class="summary-section">
            <h3>🇸🇳 Résumé en Wolof</h3>
            {summary_wo_html}
        </div>
"""
            if data.get("summary_bm"):
                summary_bm_html = markdown.markdown(
                    data.get("summary_bm", ""), 
                    extensions=['nl2br']
                )
                html_content += f"""
        <div class="summary-section">
            <h3>🇲🇱 Résumé en Bambara</h3>
            {summary_bm_html}
        </div>
"""
            html_content += """
    </div>
"""
        
        html_content += f"""
    <div class="footer">
        <p><strong>© 2025 MaliAgriculture.com</strong> - Smart Solution for Agriculture</p>
        <p>Généré le {current_date}</p>
    </div>
</body>
</html>
"""
        return html_content
    
    def generate_pdf(data):
        """Generate PDF from HTML using xhtml2pdf"""
        if not XHTML2PDF_AVAILABLE:
            return None
        try:
            html_string = format_report_for_pdf(data)
            pdf_bytes = BytesIO()
            result = pisa.CreatePDF(
                src=BytesIO(html_string.encode('utf-8')),
                dest=pdf_bytes,
                encoding='utf-8'
            )
            if result.err:
                raise Exception(f"Erreur lors de la création du PDF: {result.err}")
            pdf_bytes.seek(0)
            return pdf_bytes.getvalue()
        except Exception as e:
            st.warning(f"⚠️ Erreur lors de la génération du PDF: {e}")
            return None
    
    # Download button at the end
    
    try:
        col_download = st.columns([1, 2, 1])
        with col_download[1]:
            # Always try to generate PDF first if available, fallback to HTML
            pdf_bytes = None
            if XHTML2PDF_AVAILABLE:
                try:
                    pdf_bytes = generate_pdf(data)
                except Exception as e:
                    st.warning(f"⚠️ Impossible de générer le PDF: {e}")
                    pdf_bytes = None
            
            if pdf_bytes:
                # PDF generated successfully
                file_name = f"rapport_analyse_{st.session_state.current_file_id or 'soil'}.pdf"
                st.download_button(
                    label="📥 Télécharger le rapport complet (PDF)",
                    data=pdf_bytes,
                    file_name=file_name,
                    mime="application/pdf",
                    key="download_report_pdf",
                    use_container_width=True
                )
            else:
                # Fallback to HTML format
                try:
                    html_content = format_report_for_pdf(data)
                    file_name = f"rapport_analyse_{st.session_state.current_file_id or 'soil'}.html"
                    st.download_button(
                        label="📥 Télécharger le rapport complet (HTML)",
                        data=html_content,
                        file_name=file_name,
                        mime="text/html",
                        key="download_report_html",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Erreur lors de la préparation du téléchargement: {e}")
    except Exception as e:
        st.error(f"Erreur critique lors de l'affichage du bouton de téléchargement: {e}")
else:
    st.markdown("""
    <div style="background-color: #FFFFFF; border-radius: 12px; padding: 3rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-top: 2rem;">
        <h3 style="color: #795548; margin-bottom: 1rem;">📄 Commencez votre analyse</h3>
        <p style="color: #666; font-size: 1.1rem;">Veuillez téléverser un fichier PDF pour commencer l'analyse de votre sol.</p>
    </div>
    """, unsafe_allow_html=True)

