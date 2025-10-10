/**
 * Comprehensive test data for Student Results View
 * Based on the detailed specifications for the Results component
 */

export interface StudentResult {
  id: string;
  essay_text: string;
  overall_score: number;
  letter_grade: string;
  timestamp: string;
  criteria: Criterion[];
  essay_insights: EssayInsights;
  metadata: {
    word_count: number;
    paragraph_count: number;
    reading_time: string;
  };
}

export interface Criterion {
  id: string;
  name: string;
  weight: number;
  score: number;
  level: 'Excellent' | 'Proficient' | 'Meets expectations' | 'Developing' | 'Poor';
  confidence: number;
  evidence_spans: EvidenceSpan[];
  feedback: {
    why: string;
    suggestion: string;
    strengths?: string[];
    areas_for_improvement?: string[];
  };
}

export interface EvidenceSpan {
  start: number;
  end: number;
  paragraph: number;
  text: string;
  relevance_score: number;
}

export interface EssayInsights {
  length_assessment: {
    message: string;
    recommendation: string;
  };
  readability_assessment: {
    message: string;
    grade_level: number;
  };
  structure_assessment: {
    message: string;
    paragraph_flow: string;
  };
  quote_usage: {
    message: string;
    count: number;
  };
}

// Sample essay text with clear structure for testing
const sampleEssay = `The Impact of Social Media on Teen Mental Health

Social media has become an integral part of teenage life, but its effects on mental health are increasingly concerning. While platforms like Instagram and TikTok offer opportunities for connection and self-expression, they also create unrealistic expectations and contribute to anxiety and depression among young people.

Research consistently shows that excessive social media use correlates with higher rates of anxiety and depression in teenagers. A 2023 study by the American Psychological Association found that teens who spend more than three hours daily on social media are twice as likely to experience symptoms of depression compared to their peers who use it less frequently. This correlation suggests that social media platforms may be contributing to mental health challenges rather than alleviating them.

The comparison culture fostered by social media is particularly harmful to teen mental health. When teenagers constantly see curated, filtered images of their peers' lives, they often feel inadequate about their own experiences. This phenomenon, known as "social comparison," leads to decreased self-esteem and increased feelings of loneliness. For example, seeing friends' vacation photos or academic achievements can make teens feel like they're falling behind in life.

However, social media also provides valuable support networks for teenagers facing mental health challenges. Online communities offer safe spaces where teens can share their experiences and find peer support. Many teenagers report that social media has helped them connect with others who understand their struggles, particularly for those dealing with conditions like anxiety or depression.

The key to addressing social media's impact on teen mental health lies in promoting digital literacy and healthy usage habits. Parents and educators should work together to teach teenagers how to use social media mindfully, including recognizing when content is unrealistic or harmful. Schools can implement programs that help students develop critical thinking skills about online content and encourage face-to-face social interactions.

In conclusion, while social media presents both opportunities and challenges for teen mental health, the evidence suggests that its negative effects often outweigh the benefits. By promoting digital literacy and healthy usage patterns, we can help teenagers navigate social media in ways that support rather than undermine their mental wellbeing.`;

export const studentTestResult: StudentResult = {
  id: "test_student_result_001",
  essay_text: sampleEssay,
  overall_score: 78.5,
  letter_grade: "B+",
  timestamp: "2024-01-15T14:30:00Z",
  metadata: {
    word_count: 324,
    paragraph_count: 6,
    reading_time: "2-3 minutes"
  },
  criteria: [
    {
      id: "thesis",
      name: "Thesis & Argument",
      weight: 25,
      score: 4.2,
      level: "Proficient",
      confidence: 0.89,
      evidence_spans: [
        {
          start: 45,
          end: 120,
          paragraph: 1,
          text: "Social media has become an integral part of teenage life, but its effects on mental health are increasingly concerning. While platforms like Instagram and TikTok offer opportunities for connection and self-expression, they also create unrealistic expectations and contribute to anxiety and depression among young people.",
          relevance_score: 0.95
        }
      ],
      feedback: {
        why: "Your thesis clearly states the main argument about social media's dual impact on teen mental health. It's specific and appears early in the introduction.",
        suggestion: "Consider making your thesis even more specific by mentioning the key factors you'll analyze (comparison culture, support networks, digital literacy).",
        strengths: ["Clear position statement", "Early placement in essay", "Addresses complexity of the issue"],
        areas_for_improvement: ["Could be more specific about key points to be covered"]
      }
    },
    {
      id: "evidence",
      name: "Evidence & Analysis",
      weight: 30,
      score: 3.8,
      level: "Meets expectations",
      confidence: 0.92,
      evidence_spans: [
        {
          start: 180,
          end: 280,
          paragraph: 2,
          text: "Research consistently shows that excessive social media use correlates with higher rates of anxiety and depression in teenagers. A 2023 study by the American Psychological Association found that teens who spend more than three hours daily on social media are twice as likely to experience symptoms of depression compared to their peers who use it less frequently.",
          relevance_score: 0.88
        },
        {
          start: 350,
          end: 420,
          paragraph: 3,
          text: "The comparison culture fostered by social media is particularly harmful to teen mental health. When teenagers constantly see curated, filtered images of their peers' lives, they often feel inadequate about their own experiences.",
          relevance_score: 0.91
        }
      ],
      feedback: {
        why: "You provide solid research evidence and explain how it supports your argument. The APA study adds credibility to your claims.",
        suggestion: "Add more analysis after presenting evidence. Explain WHY the correlation exists and what it means for teenagers specifically.",
        strengths: ["Strong research citation", "Relevant statistics", "Clear connection to argument"],
        areas_for_improvement: ["Need deeper analysis of evidence", "Could use more diverse sources"]
      }
    },
    {
      id: "organization",
      name: "Organization & Structure",
      weight: 20,
      score: 4.0,
      level: "Proficient",
      confidence: 0.85,
      evidence_spans: [
        {
          start: 45,
          end: 65,
          paragraph: 1,
          text: "Social media has become an integral part of teenage life, but its effects on mental health are increasingly concerning.",
          relevance_score: 0.82
        },
        {
          start: 500,
          end: 520,
          paragraph: 5,
          text: "The key to addressing social media's impact on teen mental health lies in promoting digital literacy and healthy usage habits.",
          relevance_score: 0.87
        }
      ],
      feedback: {
        why: "Your essay follows a logical structure with clear topic sentences and smooth transitions between paragraphs.",
        suggestion: "Consider adding transitional phrases between paragraphs to make the flow even smoother.",
        strengths: ["Logical progression", "Clear topic sentences", "Good paragraph structure"],
        areas_for_improvement: ["Could use stronger transitions", "Some paragraphs could be more connected"]
      }
    },
    {
      id: "style",
      name: "Style & Mechanics",
      weight: 15,
      score: 3.5,
      level: "Meets expectations",
      confidence: 0.78,
      evidence_spans: [
        {
          start: 280,
          end: 320,
          paragraph: 2,
          text: "This correlation suggests that social media platforms may be contributing to mental health challenges rather than alleviating them.",
          relevance_score: 0.75
        }
      ],
      feedback: {
        why: "Your writing is generally clear and grammatically correct, with varied sentence structures.",
        suggestion: "Watch for run-on sentences and consider breaking some longer sentences into shorter, more impactful ones.",
        strengths: ["Clear communication", "Good vocabulary", "Mostly correct grammar"],
        areas_for_improvement: ["Some sentence length issues", "Minor punctuation errors"]
      }
    },
    {
      id: "conclusion",
      name: "Conclusion",
      weight: 10,
      score: 4.5,
      level: "Excellent",
      confidence: 0.94,
      evidence_spans: [
        {
          start: 580,
          end: 650,
          paragraph: 6,
          text: "In conclusion, while social media presents both opportunities and challenges for teen mental health, the evidence suggests that its negative effects often outweigh the benefits. By promoting digital literacy and healthy usage patterns, we can help teenagers navigate social media in ways that support rather than undermine their mental wellbeing.",
          relevance_score: 0.96
        }
      ],
      feedback: {
        why: "Your conclusion effectively summarizes the main points and provides a clear call to action. It ties back to your thesis perfectly.",
        suggestion: "This is excellent! You might consider adding a brief mention of specific steps parents and educators can take.",
        strengths: ["Strong summary", "Clear call to action", "Ties back to thesis", "Forward-looking"],
        areas_for_improvement: ["Could be slightly more specific about next steps"]
      }
    }
  ],
  essay_insights: {
    length_assessment: {
      message: "Your essay is well within the expected length range for this assignment.",
      recommendation: "Consider adding one more supporting example to strengthen your argument."
    },
    readability_assessment: {
      message: "Your writing is accessible to a general audience while maintaining academic tone.",
      grade_level: 11
    },
    structure_assessment: {
      message: "Your essay follows a clear five-paragraph structure with logical flow.",
      paragraph_flow: "Strong progression from problem identification to solution proposal."
    },
    quote_usage: {
      message: "You effectively integrate research evidence without over-relying on quotes.",
      count: 1
    }
  }
};

// Additional test cases for different scenarios
export const excellentStudentResult: StudentResult = {
  ...studentTestResult,
  id: "excellent_student_001",
  overall_score: 95.0,
  letter_grade: "A",
  criteria: studentTestResult.criteria.map(criterion => ({
    ...criterion,
    score: 4.5 + Math.random() * 0.5,
    level: "Excellent" as const,
    confidence: 0.95
  }))
};

export const developingStudentResult: StudentResult = {
  ...studentTestResult,
  id: "developing_student_001",
  overall_score: 65.0,
  letter_grade: "D+",
  criteria: studentTestResult.criteria.map(criterion => ({
    ...criterion,
    score: 2.0 + Math.random() * 1.5,
    level: "Developing" as const,
    confidence: 0.70
  }))
};

// Test data for accessibility features
export const accessibilityTestResult: StudentResult = {
  ...studentTestResult,
  id: "accessibility_test_001",
  criteria: studentTestResult.criteria.map(criterion => ({
    ...criterion,
    confidence: 0.45, // Low confidence for testing confidence indicators
    feedback: {
      ...criterion.feedback,
      why: "This is a test case for low confidence scoring to demonstrate the confidence indicator feature in the UI.",
      suggestion: "This suggestion appears when the system has low confidence in its assessment."
    }
  }))
};
