# KG quality check

`python kg/evaluate.py` draws 50 of the 307 extracted triples (`source = vinmec`, seed 42) with the first evidence sentence from a section the extractor used. Each triple was judged against all its example pages; labels are in `manual_audit.csv` (`correct`, `error_type`).

**Precision: 48 / 50 = 0.96**

| Error | Triple | Cause |
|---|---|---|
| Fact belongs to a complication, not the disease | Đái tháo đường HAS_RISK_FACTOR Rối loạn mỡ máu | Pages list it as a risk factor for kidney / eye complications |
| Fact belongs to a complication, not the disease | Đái tháo đường HAS_SYMPTOM Đau bụng | Symptom of ketoacidosis / gastrointestinal neuropathy |

Other observations:

- Heading keywords are too broad: "nguy cơ" also matches "giảm thiểu nguy cơ tim mạch", "nguyên nhân" matches "nguyên nhân gây ngứa". The fact was still true in the sample because other supporting pages stated it, but individual pages can be weak evidence (#4, #5, #16).
- Facts are correct with respect to the Vinmec text, not checked against clinical guidelines (e.g. #34 "sụt cân" as a gestational-diabetes symptom is stated by the source but is not typical).
- Precision only; recall (facts in the text that the fixed vocabulary misses) is not measured.

## After tightening heading rules

`about_disease()` in `kg/extract.py`: a Symptom / RiskFactor section must be generic (≤ 5 words) or name diabetes, and must not name another topic (`OTHER_TOPIC` in `kg/vocab.py`: complications, stroke, coronary disease, itching, gout, …) or "giảm/phòng … nguy cơ". Complication sections no longer yield symptoms.

345 → 339 triples. Removed:

| Triple | Judgement |
|---|---|
| Đái tháo đường type 1 HAS_SYMPTOM Tê bì tay chân | correct removal (neuropathy complication) |
| Đái tháo đường type 2 HAS_SYMPTOM Vã mồ hôi | correct removal (hypoglycaemia symptom) |
| Tiền đái tháo đường HAS_RISK_FACTOR Tuổi cao (sample #5) | true fact lost, support fell below 2 |
| Tiền đái tháo đường HAS_RISK_FACTOR Tăng huyết áp (sample #15) | true fact lost, support fell below 2 |
| Đái tháo đường HAS_RISK_FACTOR Dùng corticoid kéo dài | true fact lost |
| Đái tháo đường type 2 HAS_RISK_FACTOR Hút thuốc lá | true fact lost |

The two sample errors stay in the graph with much less support (16 → 3 and 18 → 6 pages): the remaining pages do state them under real diabetes headings ("Nguyên nhân và yếu tố nguy cơ gây bệnh tiểu đường: Rối loạn mỡ máu"; abdominal pain in symptom lists for diabetes in children). They are now correct with respect to the source, so the noise left is in weak *support*, not in wrong facts.

Trade-off: stricter rules give cleaner evidence per page but lose recall on rare facts; `support` on every relationship lets queries filter weak facts (`WHERE r.support >= 3`).
