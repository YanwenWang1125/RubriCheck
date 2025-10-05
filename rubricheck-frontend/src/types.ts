export type RubricLevel = {
  name: string; // e.g., 'Excellent', 'Good', 'Fair', 'Poor'
  description: string;
  points?: number; // optional numeric mapping
};

export type RubricCriterion = {
  id: string;
  name: string;
  weight?: number; // 0..1
  levels: RubricLevel[];
  description?: string;
};

export type Rubric = {
  id: string;
  title: string;
  criteria: RubricCriterion[];
  scaleNote?: string;
};

export type EvaluationItem = {
  criterionId: string;
  level: string;
  justification: string;
  evidenceSpans: { text: string; start?: number; end?: number; paraIndex?: number }[];
  suggestion?: string;
  confidence?: number;
};

export type EvaluationResult = {
  overall: {
    numeric?: number;
    letter?: string;
    confidence?: number;
  };
  items: EvaluationItem[];
  meta?: Record<string, unknown>;
};
