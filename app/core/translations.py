# app/core/translations.py

TRANSLATIONS = {
    "fr": {
        "report_title": "RAPPORT D'ANALYSE DE SOL",
        "analysis_time": "Temps d'analyse",
        "parameters_title": "Paramètres extraits",
        "interpretation_title": "Interprétation agronomique",
        "recommendations_title": "Recommandations et cultures adaptées",
        "parameter": "Paramètre",
        "value": "Valeur",
        "unit": "Unité",
        "extraction_failed": "Extraction impossible",
        "no_parameters": "Aucun paramètre extrait",
        "ph": "pH",
        "matiere_organique": "Matière organique",
        "azote_total": "Azote total",
        "phosphore": "Phosphore",
        "potassium": "Potassium",
        "calcium": "Calcium",
        "magnesium": "Magnésium",
        "sodium": "Sodium",
        "cec": "Capacité d'échange cationique",
        "conductivite_electrique": "Conductivité électrique",
        "carbone_organique": "Carbone organique",
        "c_n": "C/N",
        "saturation": "Saturation",
        "texture": "Texture"
    },
    "wo": {
        "report_title": "RAPOORU XAM-XAMU SÓL",
        "analysis_time": "Waxtu xam-xam",
        "parameters_title": "Ay paramètres yó nu joxé",
        "interpretation_title": "Xam-xamu agronomique",
        "recommendations_title": "Ay wàcc ak ay mburu yó mu baax",
        "parameter": "Paramètre",
        "value": "Njariñ",
        "unit": "Unité",
        "extraction_failed": "Joxe amul",
        "no_parameters": "Amul paramètres",
        "ph": "pH",
        "matiere_organique": "Matière organique",
        "azote_total": "Azote",
        "phosphore": "Phosphore",
        "potassium": "Potassium",
        "calcium": "Calcium",
        "magnesium": "Magnésium",
        "sodium": "Sodium",
        "cec": "CEC",
        "conductivite_electrique": "Conductivité",
        "carbone_organique": "Carbone",
        "c_n": "C/N",
        "saturation": "Saturation",
        "texture": "Texture"
    },
    "bm": {
        "report_title": "DUGUKOLO SEKO RAPORO",
        "analysis_time": "Seko waati",
        "parameters_title": "Paramètres minw bɔra",
        "interpretation_title": "Seko kɔrɔfoli",
        "recommendations_title": "Lakanaw ani jiri minw ka ɲi",
        "parameter": "Paramètre",
        "value": "Nafa",
        "unit": "Unité",
        "extraction_failed": "Bɔli ma se ka kɛ",
        "no_parameters": "Paramètres si tɛ",
        "ph": "pH",
        "matiere_organique": "Matière organique",
        "azote_total": "Azote",
        "phosphore": "Phosphore",
        "potassium": "Potassium",
        "calcium": "Calcium",
        "magnesium": "Magnésium",
        "sodium": "Sodium",
        "cec": "CEC",
        "conductivite_electrique": "Conductivité",
        "carbone_organique": "Carbone",
        "c_n": "C/N",
        "saturation": "Saturation",
        "texture": "Texture"
    }
}

def get_translation(key: str, lang: str = "fr") -> str:
    """Get translation for a key in the specified language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, key)

def translate_parameter_name(param_name: str, lang: str = "fr") -> str:
    """Translate parameter name"""
    key = param_name.lower().replace(' ', '_').replace("'", '').replace('é', 'e')
    return get_translation(key, lang)