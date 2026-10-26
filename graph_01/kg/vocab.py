"""Curated diabetes vocabulary: canonical entity -> (label, aliases).

Aliases are lowercase Vietnamese (with diacritics) as they appear in Vinmec text.
Static facts (drug class, organ, threshold) are general medical knowledge and
are loaded with source = "curated" so they can be told apart from extracted facts.
"""

DIABETES_TYPES = {
    "Đái tháo đường type 1": ["tuýp 1", "type 1", "típ 1", "tip 1", "týp 1", "tuyp 1"],
    "Đái tháo đường type 2": ["tuýp 2", "type 2", "típ 2", "tip 2", "týp 2", "tuyp 2"],
    "Đái tháo đường thai kỳ": ["thai kỳ", "thai kì", "mang thai", "mẹ bầu", "bà bầu"],
    "Tiền đái tháo đường": ["tiền đái tháo đường", "tiền tiểu đường"],
}
GENERAL = "Đái tháo đường"

VOCAB = {
    # ---- Symptoms
    "Khát nhiều": ("Symptom", ["khát nhiều", "uống nhiều", "khát nước", "hay khát", "khô miệng"]),
    "Tiểu nhiều": ("Symptom", ["tiểu nhiều", "đi tiểu nhiều", "tiểu đêm", "đi tiểu thường xuyên", "tiểu thường xuyên"]),
    "Ăn nhiều": ("Symptom", ["ăn nhiều", "đói nhiều", "hay đói", "thèm ăn", "nhanh đói"]),
    "Sụt cân": ("Symptom", ["sụt cân", "giảm cân không rõ", "gầy sút", "gầy nhiều", "sút cân"]),
    "Mệt mỏi": ("Symptom", ["mệt mỏi", "uể oải", "mệt"]),
    "Nhìn mờ": ("Symptom", ["nhìn mờ", "mờ mắt", "giảm thị lực"]),
    "Vết thương lâu lành": ("Symptom", ["lâu lành", "chậm lành", "khó lành"]),
    "Tê bì tay chân": ("Symptom", ["tê bì", "tê tay", "tê chân", "dị cảm", "ngứa ran", "kiến bò"]),
    "Nhiễm trùng tái phát": ("Symptom", ["nhiễm trùng tái phát", "nhiễm nấm", "ngứa vùng kín", "nhiễm trùng da"]),
    "Da sạm (gai đen)": ("Symptom", ["gai đen", "sạm da", "da sẫm màu"]),
    "Chóng mặt": ("Symptom", ["chóng mặt", "hoa mắt"]),
    "Vã mồ hôi": ("Symptom", ["vã mồ hôi", "đổ mồ hôi", "toát mồ hôi"]),
    "Run tay": ("Symptom", ["run tay", "run rẩy", "run"]),
    "Buồn nôn": ("Symptom", ["buồn nôn", "nôn"]),
    "Đau bụng": ("Symptom", ["đau bụng"]),
    "Hơi thở mùi trái cây": ("Symptom", ["mùi trái cây", "mùi ceton", "mùi táo"]),

    # ---- Causes / risk factors
    "Kháng insulin": ("RiskFactor", ["kháng insulin", "đề kháng insulin"]),
    "Thiếu hụt insulin": ("RiskFactor", ["thiếu insulin", "thiếu hụt insulin", "không sản xuất insulin", "giảm tiết insulin"]),
    "Tự miễn phá hủy tế bào beta": ("RiskFactor", ["tự miễn", "tế bào beta", "kháng thể kháng đảo tụy"]),
    "Di truyền / tiền sử gia đình": ("RiskFactor", ["di truyền", "tiền sử gia đình", "gia đình có người", "bố mẹ mắc"]),
    "Thừa cân, béo phì": ("RiskFactor", ["béo phì", "thừa cân", "béo bụng", "vòng eo"]),
    "Ít vận động": ("RiskFactor", ["ít vận động", "lười vận động", "lối sống tĩnh tại", "ngồi nhiều"]),
    "Chế độ ăn nhiều đường, tinh bột": ("RiskFactor", ["ăn nhiều đường", "ăn nhiều tinh bột", "đồ ngọt", "nước ngọt"]),
    "Tuổi cao": ("RiskFactor", ["tuổi cao", "trên 45 tuổi", "> 45 tuổi", "người cao tuổi", "lớn tuổi"]),
    "Tăng huyết áp": ("RiskFactor", ["tăng huyết áp", "cao huyết áp", "huyết áp cao"]),
    "Rối loạn mỡ máu": ("RiskFactor", ["rối loạn mỡ máu", "mỡ máu cao", "rối loạn lipid", "cholesterol cao", "triglycerid cao"]),
    "Hội chứng buồng trứng đa nang": ("RiskFactor", ["buồng trứng đa nang"]),
    "Hút thuốc lá": ("RiskFactor", ["hút thuốc"]),
    "Căng thẳng, stress": ("RiskFactor", ["căng thẳng", "stress"]),
    "Tiền sử ĐTĐ thai kỳ": ("RiskFactor", ["tiền sử đái tháo đường thai kỳ", "tiền sử tiểu đường thai kỳ"]),
    "Sinh con trên 4kg": ("RiskFactor", ["trên 4kg", "trên 4 kg", "> 4kg"]),
    "Nhiễm virus": ("RiskFactor", ["virus", "coxsackie", "rubella"]),
    "Dùng corticoid kéo dài": ("RiskFactor", ["corticoid", "corticosteroid"]),

    # ---- Complications
    "Hạ đường huyết": ("Complication", ["hạ đường huyết", "tụt đường huyết", "đường huyết thấp"]),
    "Nhiễm toan ceton": ("Complication", ["nhiễm toan ceton", "nhiễm ceton", "toan ceton", "dka"]),
    "Tăng áp lực thẩm thấu": ("Complication", ["tăng áp lực thẩm thấu", "tăng áp lực thẩm thấu máu"]),
    "Bệnh thận đái tháo đường": ("Complication", ["biến chứng thận", "bệnh thận", "suy thận", "protein niệu", "albumin niệu"]),
    "Bệnh võng mạc": ("Complication", ["võng mạc", "biến chứng mắt", "mù lòa"]),
    "Đục thủy tinh thể": ("Complication", ["đục thủy tinh thể", "cườm khô"]),
    "Tăng nhãn áp": ("Complication", ["tăng nhãn áp", "glaucoma", "cườm nước"]),
    "Bệnh thần kinh ngoại biên": ("Complication", ["biến chứng thần kinh", "bệnh thần kinh", "thần kinh ngoại biên", "tổn thương thần kinh"]),
    "Bàn chân đái tháo đường": ("Complication", ["bàn chân đái tháo đường", "loét bàn chân", "loét chân", "hoại tử", "cắt cụt"]),
    "Bệnh tim mạch": ("Complication", ["tim mạch", "bệnh mạch vành", "nhồi máu cơ tim", "suy tim", "xơ vữa"]),
    "Đột quỵ": ("Complication", ["đột quỵ", "tai biến mạch máu não"]),
    "Rối loạn cương dương": ("Complication", ["rối loạn cương", "yếu sinh lý"]),
    "Liệt dạ dày": ("Complication", ["liệt dạ dày"]),
    "Bệnh nha chu": ("Complication", ["nha chu", "viêm nướu", "viêm lợi"]),
    "Loãng xương": ("Complication", ["loãng xương", "gãy xương"]),
    "Thai to": ("Complication", ["thai to", "con to"]),
    "Tiền sản giật": ("Complication", ["tiền sản giật"]),
    "Sinh non": ("Complication", ["sinh non"]),
    "Hạ đường huyết sơ sinh": ("Complication", ["hạ đường huyết sơ sinh", "trẻ sơ sinh bị hạ đường huyết"]),

    # ---- Tests
    "HbA1c": ("Test", ["hba1c", "hemoglobin a1c", "a1c"]),
    "Đường huyết lúc đói": ("Test", ["đường huyết lúc đói", "glucose lúc đói", "đường huyết đói", "glucose máu lúc đói"]),
    "Nghiệm pháp dung nạp glucose (OGTT)": ("Test", ["dung nạp glucose", "ogtt", "75g glucose", "75 gam glucose", "nghiệm pháp tăng đường huyết"]),
    "Đường huyết ngẫu nhiên": ("Test", ["đường huyết bất kỳ", "đường huyết bất kì", "đường huyết ngẫu nhiên"]),
    "Xét nghiệm nước tiểu": ("Test", ["xét nghiệm nước tiểu", "tổng phân tích nước tiểu", "đường niệu", "ceton niệu"]),
    "Kháng thể kháng đảo tụy": ("Test", ["kháng thể kháng đảo tụy", "anti-gad", "anti gad", "kháng thể gad"]),
    "C-peptide": ("Test", ["c-peptide", "c peptide"]),
    "Máy đo đường huyết": ("Test", ["máy đo đường huyết", "tự theo dõi đường huyết", "đo đường huyết tại nhà", "cgm"]),
    "Mỡ máu (lipid)": ("Test", ["bilan lipid", "ldl-c", "hdl-c", "xét nghiệm mỡ máu"]),
    "Soi đáy mắt": ("Test", ["soi đáy mắt", "khám mắt"]),

    # ---- Drugs
    "Metformin": ("Drug", ["metformin", "glucophage"]),
    "Insulin": ("Drug", ["insulin"]),
    "Insulin glargine": ("Drug", ["glargine", "lantus", "toujeo"]),
    "Insulin aspart": ("Drug", ["aspart", "novorapid", "novomix"]),
    "Insulin lispro": ("Drug", ["lispro", "humalog"]),
    "Insulin NPH": ("Drug", ["insulin nph", "insulatard"]),
    "Gliclazide": ("Drug", ["gliclazide", "diamicron"]),
    "Glimepiride": ("Drug", ["glimepiride", "amaryl"]),
    "Glibenclamide": ("Drug", ["glibenclamide", "glyburide"]),
    "Sitagliptin": ("Drug", ["sitagliptin", "januvia"]),
    "Vildagliptin": ("Drug", ["vildagliptin", "galvus"]),
    "Linagliptin": ("Drug", ["linagliptin", "trajenta"]),
    "Saxagliptin": ("Drug", ["saxagliptin"]),
    "Empagliflozin": ("Drug", ["empagliflozin", "jardiance"]),
    "Dapagliflozin": ("Drug", ["dapagliflozin", "forxiga"]),
    "Canagliflozin": ("Drug", ["canagliflozin"]),
    "Pioglitazone": ("Drug", ["pioglitazone"]),
    "Acarbose": ("Drug", ["acarbose", "glucobay"]),
    "Repaglinide": ("Drug", ["repaglinide"]),
    "Liraglutide": ("Drug", ["liraglutide", "victoza"]),
    "Semaglutide": ("Drug", ["semaglutide", "ozempic", "rybelsus"]),
    "Dulaglutide": ("Drug", ["dulaglutide", "trulicity"]),

    # ---- Food (direction RECOMMENDS / AVOIDS is decided by the section heading)
    "Rau xanh": ("Food", ["rau xanh", "rau lá xanh", "rau củ", "bông cải", "súp lơ"]),
    "Ngũ cốc nguyên hạt": ("Food", ["ngũ cốc nguyên hạt", "gạo lứt", "yến mạch", "bánh mì nguyên cám", "lúa mạch"]),
    "Các loại đậu": ("Food", ["đậu đỗ", "các loại đậu", "đậu lăng", "đậu xanh", "đậu đen", "đậu nành"]),
    "Cá béo": ("Food", ["cá hồi", "cá thu", "cá béo", "omega-3", "omega 3"]),
    "Các loại hạt": ("Food", ["hạnh nhân", "óc chó", "hạt chia", "hạt lanh", "các loại hạt"]),
    "Trái cây ít ngọt": ("Food", ["bưởi", "táo", "lê", "quả mọng", "dâu tây", "ổi"]),
    "Sữa chua không đường": ("Food", ["sữa chua"]),
    "Dầu ô liu": ("Food", ["dầu ô liu", "dầu oliu"]),
    "Trứng": ("Food", ["trứng"]),
    "Đồ ngọt, bánh kẹo": ("Food", ["bánh kẹo", "đồ ngọt", "kẹo", "bánh ngọt", "đường tinh luyện"]),
    "Nước ngọt có ga": ("Food", ["nước ngọt", "nước có ga", "nước giải khát"]),
    "Cơm trắng, tinh bột tinh chế": ("Food", ["cơm trắng", "gạo trắng", "bánh mì trắng", "tinh bột tinh chế"]),
    "Trái cây nhiều đường": ("Food", ["sầu riêng", "xoài chín", "nhãn", "vải", "mít", "chuối chín", "trái cây sấy"]),
    "Rượu bia": ("Food", ["rượu", "bia"]),
    "Đồ chiên rán, mỡ động vật": ("Food", ["chiên rán", "đồ chiên", "mỡ động vật", "chất béo bão hòa", "chất béo chuyển hóa"]),
    "Thịt chế biến sẵn": ("Food", ["xúc xích", "thịt xông khói", "thịt chế biến sẵn", "đồ hộp"]),

    # ---- Lifestyle
    "Tập thể dục đều đặn": ("Lifestyle", ["tập thể dục", "vận động thể lực", "hoạt động thể chất", "đi bộ", "150 phút"]),
    "Giảm cân": ("Lifestyle", ["giảm cân", "kiểm soát cân nặng", "duy trì cân nặng"]),
    "Bỏ thuốc lá": ("Lifestyle", ["bỏ thuốc lá", "ngừng hút thuốc"]),
    "Ngủ đủ giấc": ("Lifestyle", ["ngủ đủ", "giấc ngủ"]),
    "Chăm sóc bàn chân": ("Lifestyle", ["chăm sóc bàn chân", "kiểm tra bàn chân"]),
    "Khám sức khỏe định kỳ": ("Lifestyle", ["khám định kỳ", "tái khám", "kiểm tra định kỳ"]),
}

DRUG_CLASS = {
    "Metformin": "Biguanide",
    "Insulin": "Nhóm Insulin", "Insulin glargine": "Nhóm Insulin", "Insulin aspart": "Nhóm Insulin",
    "Insulin lispro": "Nhóm Insulin", "Insulin NPH": "Nhóm Insulin",
    "Gliclazide": "Sulfonylurea", "Glimepiride": "Sulfonylurea", "Glibenclamide": "Sulfonylurea",
    "Sitagliptin": "Ức chế DPP-4", "Vildagliptin": "Ức chế DPP-4", "Linagliptin": "Ức chế DPP-4",
    "Saxagliptin": "Ức chế DPP-4",
    "Empagliflozin": "Ức chế SGLT2", "Dapagliflozin": "Ức chế SGLT2", "Canagliflozin": "Ức chế SGLT2",
    "Pioglitazone": "Thiazolidinedione", "Acarbose": "Ức chế alpha-glucosidase",
    "Repaglinide": "Meglitinide",
    "Liraglutide": "Đồng vận GLP-1", "Semaglutide": "Đồng vận GLP-1", "Dulaglutide": "Đồng vận GLP-1",
}

COMPLICATION_ORGAN = {
    "Bệnh thận đái tháo đường": "Thận", "Bệnh võng mạc": "Mắt", "Đục thủy tinh thể": "Mắt",
    "Tăng nhãn áp": "Mắt", "Bệnh thần kinh ngoại biên": "Thần kinh", "Bàn chân đái tháo đường": "Bàn chân",
    "Bệnh tim mạch": "Tim mạch", "Đột quỵ": "Não", "Liệt dạ dày": "Dạ dày",
    "Bệnh nha chu": "Răng miệng", "Loãng xương": "Xương", "Rối loạn cương dương": "Thần kinh",
}

# Diagnostic thresholds (ADA / Bộ Y tế 2020 guideline, also quoted on Vinmec disease pages)
THRESHOLDS = {
    "HbA1c": "≥ 6.5%",
    "Đường huyết lúc đói": "≥ 7.0 mmol/L (126 mg/dL)",
    "Nghiệm pháp dung nạp glucose (OGTT)": "2 giờ ≥ 11.1 mmol/L (200 mg/dL)",
    "Đường huyết ngẫu nhiên": "≥ 11.1 mmol/L kèm triệu chứng",
}

# Section heading keyword -> which labels may be extracted from that section
SECTION_RULES = [
    (["triệu chứng", "dấu hiệu", "biểu hiện", "nhận biết"], {"Symptom"}),
    (["nguyên nhân", "nguy cơ", "đối tượng", "yếu tố", "ai dễ"], {"RiskFactor"}),
    (["biến chứng", "nguy hiểm", "hậu quả", "ảnh hưởng"], {"Complication"}),
    (["chẩn đoán", "xét nghiệm", "phát hiện", "chỉ số", "kiểm tra", "theo dõi"], {"Test"}),
    (["điều trị", "thuốc", "insulin", "kiểm soát"], {"Drug", "Lifestyle"}),
    (["phòng ngừa", "phòng tránh", "ngăn ngừa", "phòng bệnh", "lối sống", "lưu ý"], {"Lifestyle"}),
    (["ăn", "thực phẩm", "dinh dưỡng", "thực đơn", "món", "uống", "kiêng", "tránh"], {"Food"}),
]
# Food polarity is fixed (nutrition guidance), the text only tells us the food is discussed
# for that diabetes type; per-sentence "nên/không nên" detection was too noisy.
FOOD_AVOID = {"Đồ ngọt, bánh kẹo", "Nước ngọt có ga", "Cơm trắng, tinh bột tinh chế",
              "Trái cây nhiều đường", "Rượu bia", "Đồ chiên rán, mỡ động vật", "Thịt chế biến sẵn"}

# Symptom / RiskFactor sections must be about the disease itself. A heading that names another
# topic ("nguyên nhân gây ngứa", "giảm thiểu nguy cơ tim mạch", "biến chứng thận") describes that
# topic's symptoms or causes, not diabetes'.
DISEASE_TERMS = ["tiểu đường", "đái tháo đường", "đtđ", "tuýp", "type", "típ", "bệnh"]
OTHER_TOPIC = ["biến chứng", "thận", "võng mạc", "mắt", "thần kinh", "bàn chân", "tim mạch", "ngứa",
               "gout", "gút", "da", "răng", "nhiễm toan", "ceton", "hạ đường huyết", "thai nhi", "trẻ sinh ra",
               "tai biến", "đột quỵ", "mạch vành", "hôn mê"]
REDUCE_VERBS = ["giảm", "phòng", "tránh", "ngừa", "hạn chế", "kiểm soát"]
STRICT_LABELS = {"Symptom", "RiskFactor"}

RELATION_BY_LABEL = {
    "Symptom": "HAS_SYMPTOM", "RiskFactor": "HAS_RISK_FACTOR", "Complication": "HAS_COMPLICATION",
    "Test": "DIAGNOSED_BY", "Drug": "TREATED_BY", "Lifestyle": "MANAGED_BY",
}
