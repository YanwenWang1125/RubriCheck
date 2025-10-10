/**
 * Test runner for Student Results component
 * This script sets up test data and runs the Student Results page
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Test data setup
const testData = {
  id: "test_student_result_001",
  essay_text: `The Impact of Social Media on Teen Mental Health

Social media has become an integral part of teenage life, but its effects on mental health are increasingly concerning. While platforms like Instagram and TikTok offer opportunities for connection and self-expression, they also create unrealistic expectations and contribute to anxiety and depression among young people.

Research consistently shows that excessive social media use correlates with higher rates of anxiety and depression in teenagers. A 2023 study by the American Psychological Association found that teens who spend more than three hours daily on social media are twice as likely to experience symptoms of depression compared to their peers who use it less frequently. This correlation suggests that social media platforms may be contributing to mental health challenges rather than alleviating them.

The comparison culture fostered by social media is particularly harmful to teen mental health. When teenagers constantly see curated, filtered images of their peers' lives, they often feel inadequate about their own experiences. This phenomenon, known as "social comparison," leads to decreased self-esteem and increased feelings of loneliness. For example, seeing friends' vacation photos or academic achievements can make teens feel like they're falling behind in life.

However, social media also provides valuable support networks for teenagers facing mental health challenges. Online communities offer safe spaces where teens can share their experiences and find peer support. Many teenagers report that social media has helped them connect with others who understand their struggles, particularly for those dealing with conditions like anxiety or depression.

The key to addressing social media's impact on teen mental health lies in promoting digital literacy and healthy usage habits. Parents and educators should work together to teach teenagers how to use social media mindfully, including recognizing when content is unrealistic or harmful. Schools can implement programs that help students develop critical thinking skills about online content and encourage face-to-face social interactions.

In conclusion, while social media presents both opportunities and challenges for teen mental health, the evidence suggests that its negative effects often outweigh the benefits. By promoting digital literacy and healthy usage patterns, we can help teenagers navigate social media in ways that support rather than undermine their mental wellbeing.`,
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
      evidence_spans: [],
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
      evidence_spans: [],
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
  ]
};

// Convert to backend format for testing
const backendResult = {
  id: testData.id,
  overall: {
    numeric: testData.overall_score / 100, // Convert to 0-1 scale
    letter: testData.letter_grade,
    confidence: 0.85
  },
  items: testData.criteria.map(criterion => ({
    id: criterion.id,
    name: criterion.name,
    weight: criterion.weight,
    score: criterion.score,
    confidence: criterion.confidence,
    evidence_spans: criterion.evidence_spans,
    feedback: criterion.feedback
  }))
};

console.log('🧪 Student Results Test Data Generated');
console.log('📊 Test Data Summary:');
console.log(`   - Overall Score: ${testData.overall_score} (${testData.letter_grade})`);
console.log(`   - Word Count: ${testData.metadata.word_count}`);
console.log(`   - Criteria Count: ${testData.criteria.length}`);
console.log(`   - Evidence Spans: ${testData.criteria.reduce((sum, c) => sum + c.evidence_spans.length, 0)}`);

console.log('\n🎯 Test Scenarios Available:');
console.log('   1. Excellent Student (A grade)');
console.log('   2. Developing Student (D+ grade)');
console.log('   3. Low Confidence Scores');
console.log('   4. Accessibility Features');
console.log('   5. Keyboard Navigation');

console.log('\n📋 Features to Test:');
console.log('   ✅ Evidence highlighting and spotlighting');
console.log('   ✅ Annotated vs Original view toggle');
console.log('   ✅ Keyboard navigation (↑/↓ arrows, Enter)');
console.log('   ✅ Search and filter criteria');
console.log('   ✅ Confidence indicators');
console.log('   ✅ Export functionality (PDF/CSV)');
console.log('   ✅ Accessibility mode');
console.log('   ✅ Responsive design');

console.log('\n🚀 To run the test:');
console.log('   1. Open StudentResultsTestPage.html in a browser');
console.log('   2. Or integrate StudentResults.tsx into your React app');
console.log('   3. Use the test data above to populate the component');

// Save test data to files for easy access
const testDataPath = path.join(__dirname, 'StudentResultsTestData.json');
const backendDataPath = path.join(__dirname, 'BackendTestData.json');

fs.writeFileSync(testDataPath, JSON.stringify(testData, null, 2));
fs.writeFileSync(backendDataPath, JSON.stringify(backendResult, null, 2));

console.log(`\n💾 Test data saved to:`);
console.log(`   - ${testDataPath}`);
console.log(`   - ${backendDataPath}`);

console.log('\n✨ Test setup complete! Ready to test the Student Results component.');
