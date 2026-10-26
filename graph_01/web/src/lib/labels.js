// Plain-language wording for entity types and relations.

export const TYPES = {
  DiabetesType: { label: 'Diabetes type', plural: 'Diabetes types' },
  Symptom: { label: 'Symptom', plural: 'Symptoms' },
  RiskFactor: { label: 'Risk factor', plural: 'Risk factors' },
  Complication: { label: 'Complication', plural: 'Complications' },
  Test: { label: 'Test', plural: 'Tests' },
  Drug: { label: 'Drug', plural: 'Drugs' },
  DrugClass: { label: 'Drug class', plural: 'Drug classes' },
  Food: { label: 'Food', plural: 'Foods' },
  Lifestyle: { label: 'Lifestyle', plural: 'Lifestyle measures' },
  Organ: { label: 'Organ', plural: 'Organs' },
}

export const typeLabel = (t) => TYPES[t]?.label || t
export const typeClass = (t) => `type-${(t || 'other').toLowerCase()}`

// For a fact seen from one entity: heading when the entity is the subject (out)
// or the object (in) of the relation, plus a sentence for a single fact.
export const RELATIONS = {
  HAS_SYMPTOM: { out: 'Symptoms', in: 'Symptom of', verb: 'has the symptom', back: 'is a symptom of' },
  HAS_RISK_FACTOR: { out: 'Risk factors', in: 'Risk factor for', verb: 'has the risk factor', back: 'is a risk factor for' },
  HAS_COMPLICATION: { out: 'Complications', in: 'Complication of', verb: 'can cause', back: 'can be caused by' },
  DIAGNOSED_BY: { out: 'Diagnosed with', in: 'Used to diagnose', verb: 'is diagnosed with', back: 'is used to diagnose' },
  TREATED_BY: { out: 'Treated with', in: 'Used to treat', verb: 'is treated with', back: 'is used to treat' },
  MANAGED_BY: { out: 'Managed by', in: 'Helps manage', verb: 'is managed by', back: 'helps manage' },
  RECOMMENDS_FOOD: { out: 'Recommended foods', in: 'Recommended for', verb: 'recommends eating', back: 'is recommended for' },
  AVOIDS_FOOD: { out: 'Foods to avoid', in: 'To avoid with', verb: 'advises avoiding', back: 'should be avoided with' },
  HAS_SIDE_EFFECT: { out: 'Side effects', in: 'Side effect of', verb: 'can have the side effect', back: 'is a side effect of' },
  BELONGS_TO_CLASS: { out: 'Drug class', in: 'Drugs in this class', verb: 'belongs to the class', back: 'includes' },
  AFFECTS_ORGAN: { out: 'Affects organ', in: 'Damaged by', verb: 'affects', back: 'is affected by' },
  SUBTYPE_OF: { out: 'Subtype of', in: 'Subtypes', verb: 'is a subtype of', back: 'has the subtype' },
}

export const relHeading = (rel, dir) => RELATIONS[rel]?.[dir] || rel
export const relVerb = (rel, forward = true) =>
  RELATIONS[rel]?.[forward ? 'verb' : 'back'] || rel.toLowerCase().replaceAll('_', ' ')

// Some entity names are stored in decomposed Unicode (e + combining accent); recompose them for display only.
export const nfc = (s) => (typeof s === 'string' ? s.normalize('NFC') : s)

export const fmtInt = (n) => new Intl.NumberFormat('en-US').format(n)
export const articles = (n) => `${fmtInt(n)} article${n === 1 ? '' : 's'}`
