# app/agents/orchestrator_agent.py
import tempfile
import json
import threading
from app.agents.ocr_agent import OcrAgent
from app.agents.extractorAgent import ExtractorAgent
from app.agents.analyzerAgent import AnalyzerAgent
from app.agents.recommenderAgent import RecommenderAgent
from app.agents.summarizerAgent import SummarizerAgent
from app.core.translations import get_translation, translate_parameter_name

class OrchestratorAgent:
    def __init__(self):
        self.ocr = OcrAgent()
        self.extractor = ExtractorAgent()
        self.analyzer = AnalyzerAgent()
        self.recommender = RecommenderAgent()
        self.summarizer = SummarizerAgent()
    
    def _format_parameters(self, params: dict, language: str = "fr") -> str:
        """Format parameters as a readable table with one row per parameter.
        - Merges keys ending with ' Min'/' Max' into a single range.
        - Supports values with nested {'valeur': {'min','max'}} or scalar.
        """
        lines = []
        lines.append("| Paramètre | Valeur | Unité |")
        lines.append("|-----------|--------|-------|")

        def nice_name(k: str) -> str:
            mapping = {
                'ph': 'pH',
                'matiere organique': 'Matière organique',
                'azote total': 'Azote total',
                'phosphore': 'Phosphore',
                'potassium': 'Potassium',
                'calcium': 'Calcium',
                'magnesium': 'Magnésium',
                'sodium': 'Sodium',
                'cec': "Capacité d'échange cationique",
                'conductivite electrique': 'Conductivité électrique',
                'carbone organique': 'Carbone organique',
                'c_n': 'C/N',
                'v': 'Saturation',
                'pse': 'PSE',
                'texture': 'Texture'
            }
            base = k.replace('_', ' ').strip().lower()
            base = base.replace(' min', '').replace(' max', '')
            return mapping.get(base, k.replace('_', ' ').title())

        # First pass: collect possible min/max pairs and normal values
        aggregated = {}

        def store_value(base_key: str, role: str, raw_val, unit: str):
            if base_key not in aggregated:
                aggregated[base_key] = {'unit': unit, 'val': {}}
            if unit and not aggregated[base_key]['unit']:
                aggregated[base_key]['unit'] = unit
            aggregated[base_key]['val'][role] = raw_val

        for key, value in params.items():
            if key == 'autres_parametres' and isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    unit = sub_value.get('unite', '') if isinstance(sub_value, dict) else ''
                    base = sub_key.replace('_', ' ').strip()
                    lowered = base.lower()
                    if lowered.endswith(' min'):
                        store_value(lowered[:-4], 'min', sub_value.get('valeur', sub_value) if isinstance(sub_value, dict) else sub_value, unit)
                    elif lowered.endswith(' max'):
                        store_value(lowered[:-4], 'max', sub_value.get('valeur', sub_value) if isinstance(sub_value, dict) else sub_value, unit)
                    else:
                        # Try nested valeur
                        if isinstance(sub_value, dict) and 'valeur' in sub_value:
                            val = sub_value['valeur']
                            if isinstance(val, dict) and 'min' in val and 'max' in val:
                                store_value(base, 'min', val['min'], unit)
                                store_value(base, 'max', val['max'], unit)
                            else:
                                store_value(base, 'single', val, unit)
                        else:
                            store_value(base, 'single', sub_value, unit)
            else:
                unit = value.get('unite', '') if isinstance(value, dict) else ''
                base = key.replace('_', ' ').strip()
                lowered = base.lower()
                if lowered.endswith(' min'):
                    store_value(lowered[:-4], 'min', value.get('valeur', value) if isinstance(value, dict) else value, unit)
                elif lowered.endswith(' max'):
                    store_value(lowered[:-4], 'max', value.get('valeur', value) if isinstance(value, dict) else value, unit)
                else:
                    if isinstance(value, dict) and 'valeur' in value:
                        val = value['valeur']
                        if isinstance(val, dict) and 'min' in val and 'max' in val:
                            store_value(base, 'min', val['min'], unit)
                            store_value(base, 'max', val['max'], unit)
                        else:
                            store_value(base, 'single', val, unit)
                    else:
                        store_value(base, 'single', value, unit)

        # Build lines
        for base, obj in aggregated.items():
            unit = obj.get('unit', '') or ''
            vals = obj.get('val', {})
            if 'min' in vals or 'max' in vals:
                vmin = vals.get('min')
                vmax = vals.get('max')
                # Fallback if only one side present
                if vmin is not None and vmax is not None:
                    val_str = f"{vmin} - {vmax}"
                else:
                    val_str = str(vmin if vmin is not None else vmax)
            else:
                single = vals.get('single', '')
                # Handle nested dictionaries (e.g., texture with argile/limon/sable)
                if isinstance(single, dict):
                    # Format nested dict as readable text
                    parts = []
                    for k, v in single.items():
                        if isinstance(v, dict):
                            val = v.get('valeur', v)
                            u = v.get('unite', '')
                            parts.append(f"{k}: {val}{u}")
                        else:
                            parts.append(f"{k}: {v}")
                    val_str = ', '.join(parts)
                else:
                    # Handle string values that may already contain ranges or lists
                    val_str = str(single) if single else ''
            
            # Skip empty entries
            if val_str and val_str != 'None':
                lines.append(f"| {translate_parameter_name(base, language)} | {val_str} | {unit} |")

        return "\n".join(lines)

    def _normalize_parameters(self, params: dict) -> dict:
        """Normalize parameters to consistent structure.
        Handles both old nested structure and new string-based values.
        """
        out = {}
        buckets = {}

        def ingest(k, v):
            base = k.replace('_', ' ').strip()
            low = base.lower()
            
            # Extract unit and value
            if isinstance(v, dict):
                unit = v.get('unite', '')
                val = v.get('valeur', v)
            else:
                unit = ''
                val = v
            
            # Detect min/max suffixes
            if low.endswith(' min'):
                key0 = low[:-4]
                buckets.setdefault(key0, {'unit': unit, 'min': None, 'max': None})
                if unit and not buckets[key0]['unit']:
                    buckets[key0]['unit'] = unit
                buckets[key0]['min'] = val
            elif low.endswith(' max'):
                key0 = low[:-4]
                buckets.setdefault(key0, {'unit': unit, 'min': None, 'max': None})
                if unit and not buckets[key0]['unit']:
                    buckets[key0]['unit'] = unit
                buckets[key0]['max'] = val
            else:
                # Keep as-is (will be formatted as single value)
                out[base] = {'valeur': val, 'unite': unit}

        # Process all keys
        for k, v in params.items():
            if k == 'autres_parametres' and isinstance(v, dict):
                for sk, sv in v.items():
                    ingest(sk, sv)
            elif k != 'texte_brut' and k != 'error':  # Skip error keys
                ingest(k, v)

        # Apply buckets (merge min/max)
        for key0, obj in buckets.items():
            vmin = obj.get('min')
            vmax = obj.get('max')
            if vmin is not None and vmax is not None:
                out[key0.title()] = {'valeur': {'min': vmin, 'max': vmax}, 'unite': obj.get('unit', '')}
            elif vmin is not None:
                out[key0.title()] = {'valeur': vmin, 'unite': obj.get('unit', '')}
            elif vmax is not None:
                out[key0.title()] = {'valeur': vmax, 'unite': obj.get('unit', '')}

        return out

    def run(self, file, language="fr"):
        """Pipeline complet d'analyse"""
        import time
        start_time = time.time()
        self.language = language
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        # 1️⃣ Lecture PDF
        ocr_start = time.time()
        text = self.ocr.extract_text(tmp_path)
        ocr_time = time.time() - ocr_start
        print(f"\n=== TEXTE EXTRAIT ({len(text)} caractères) ===")
        print(text[:1000])  # Print first 1000 chars for debugging
        print("\n=== FIN EXTRAIT ===")
        
        # Save to debug file for inspection
        import os
        debug_dir = "app/data/debug"
        os.makedirs(debug_dir, exist_ok=True)
        with open(f"{debug_dir}/extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(text)

        # 2️⃣ Extraction paramètres
        extract_start = time.time()
        raw_parameters = self.extractor.extract_parameters(text)
        extract_time = time.time() - extract_start
        print(f"\n=== PARAMÈTRES EXTRAITS (BRUT) ===")
        print(raw_parameters)
        print("\n=== FIN PARAMÈTRES ===")

        # Normalize into clean structure with merged ranges
        parameters = self._normalize_parameters(raw_parameters if isinstance(raw_parameters, dict) else {})

        # 3️⃣ Interprétation agronomique
        analyze_start = time.time()
        analysis = self.analyzer.interpret(parameters, language=language)
        analyze_time = time.time() - analyze_start

        # 4️⃣ Recommandations + fiches cultures
        import json as _json
        recommend_start = time.time()
        recommendations = self.recommender.recommend(_json.dumps(parameters, ensure_ascii=False), analysis, language=language)
        recommend_time = time.time() - recommend_start
        
        total_time = time.time() - start_time

        # Format parameters as readable table
        params_formatted = self._format_parameters(parameters, language)

        # Build the final formatted report string
        report_str = f"""
# 🧾 {get_translation('report_title', language)}

---
**⏱️ {get_translation('analysis_time', language)}:** {total_time:.1f}s (OCR: {ocr_time:.1f}s | Extraction: {extract_time:.1f}s | Analyse: {analyze_time:.1f}s | Recommandations: {recommend_time:.1f}s)

---

## 🔍 {get_translation('parameters_title', language)}
{params_formatted}

## 🌿 {get_translation('interpretation_title', language)}
{analysis}

## 🌾 {get_translation('recommendations_title', language)}
{recommendations}
"""

        # 5. Generate summaries for other languages in parallel
        full_text = analysis + "\n\n" + recommendations
        summaries = {}

        def run_summarizer(lang):
            """Target function for threading to get summary."""
            try:
                summaries[lang] = self.summarizer.summarize(full_text, lang)
            except Exception as e:
                print(f"Error summarizing for {lang}: {e}")
                summaries[lang] = f"Erreur lors de la génération du résumé {lang}."

        # Create and start threads for Wolof and Bambara summaries
        thread_wo = threading.Thread(target=run_summarizer, args=('wo',))
        thread_bm = threading.Thread(target=run_summarizer, args=('bm',))
        
        thread_wo.start()
        thread_bm.start()

        # Wait for both summarization threads to complete
        thread_wo.join()
        thread_bm.join()

        summary_wo = summaries.get('wo', "Résumé Wolof non disponible.")
        summary_bm = summaries.get('bm', "Résumé Bambara non disponible.")

        # Return everything in one payload
        return {
            "report": report_str,
            "summary_wo": summary_wo,
            "summary_bm": summary_bm
        }
