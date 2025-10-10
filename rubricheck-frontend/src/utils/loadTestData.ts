// Temporary utility to load test data into the store for development/testing
import { useApp } from '../store'

// Test data matching real backend API response structure
const testEvaluationResult = {
  "overall": {
    "numeric": 76.25,
    "letter": "B or below",
    "confidence": 0.9
  },
  "items": [
    {
      "confidence": 0.8,
      "criterionId": "focus_and_thesis",
        "evidenceSpans": [
          {
            "end": undefined,
            "paraIndex": 0,
            "start": undefined,
            "text": "By taking a look at social media through the eyes of Aristotle's philosophy, we can better understand its effects and how to use it wisely."
          },
          {
            "end": undefined,
            "paraIndex": 1,
            "start": undefined,
            "text": "The important thing is to use it thoughtfully and not let it take over our lives."
          },
          {
            "end": undefined,
            "paraIndex": 0,
            "start": undefined,
            "text": "I pretty much agree with Aristotle's perspective on social media."
          }
        ],
      "justification": "The essay states a clear thesis about using Aristotle's philosophy to evaluate social media and largely maintains that focus. Some repetition and minor drift prevent it from being exceptionally focused.",
      "level": "Good",
      "suggestion": "Revise the introduction to present a single-sentence thesis that previews your main subpoints (balance, relationships, responsible use) and ensure each paragraph's topic sentence ties directly back to that thesis."
    },
    {
      "confidence": 1,
      "criterionId": "organization_and_flow",
      "evidenceSpans": [
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "I agree with Aristotle's idea of balance and his focus on real relationships, but I do"
        },
        {
            "end": undefined,
          "paraIndex": 1,
            "start": undefined,
          "text": "believe that social media has the potential to make the world better as well."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "I only use WeChat to commutate with my friends and"
        }
      ],
      "justification": "The piece follows an intro–background–application–personal reflection–conclusion sequence, but transitions are sometimes abrupt and a sentence is split across paragraphs, disrupting flow.",
      "level": "Fair",
        "suggestion": "Combine the split sentence into one paragraph, add clear topic and concluding sentences for each section, and use explicit transitions (e.g., \"Moreover,\" \"Conversely,\" \"Therefore\") to guide readers between ideas."
    },
    {
      "confidence": 1,
      "criterionId": "evidence_and_support",
      "evidenceSpans": [
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "A lot of times, I spend too much time scrolling, and it distracts me from homework or other important things."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "For example, social media can help people raise awareness about important issues, such as climate change or social justice."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "Aristotle also valued deep friendships and believed that communities are important for a good life."
        }
      ],
      "justification": "Support relies mostly on personal anecdotes and broad claims; it lacks specific references to Aristotle's texts or empirical data. Evidence is relevant but limited in depth and variety.",
      "level": "Fair",
      "suggestion": "Integrate brief quotations or paraphrases from Aristotle (e.g., Nicomachean Ethics on the mean and friendship) and include one or two credible statistics or studies about social media's effects to substantiate claims."
    },
    {
      "confidence": 1,
      "criterionId": "analysis_and_insight",
      "evidenceSpans": [
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "Aristotle believed in finding a balance between extremes."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "this often make people pursuit \"fake happiness\"."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "Aristotle is going to argue that social media weakens real relationships and makes it harder to form honest connections."
        }
      ],
      "justification": "The essay applies Aristotelian balance and friendship to social media and weighs pros and cons, moving beyond mere description. Analysis could be deepened with more precise conceptual links.",
      "level": "Good",
      "suggestion": "Explicitly connect key concepts (eudaimonia, the Golden Mean, and types of friendship) to concrete social media behaviors with brief, specific scenarios to show how virtue is cultivated or undermined online."
    },
    {
      "confidence": 1,
      "criterionId": "style_and_clarity",
      "evidenceSpans": [
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "If Aristotle were to look at the technological aspect of modern world, such as social media. He would evaluate it through ethics, human flourishing, and how is it shaping people's life."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "On one hand, he is going to like how the connects of people are allows them to share ideas much easier."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "Even though social media helps me stay connected easier, but focusing on my online life could make me spend less time in real life."
        }
      ],
      "justification": "While generally understandable (readability 55.1), the writing includes awkward phrasing and occasional wordiness that obscures meaning. Several sentences are cumbersome or redundant.",
      "level": "Fair",
        "suggestion": "Revise sentences for concision and flow (merge fragments, remove redundant words like \"easier\" after \"helps,\" and replace vague phrases with precise wording)."
    },
    {
      "confidence": 1,
      "criterionId": "grammar_and_mechanics",
      "evidenceSpans": [
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "If Aristotle were to look at the technological aspect of modern world, such as social media."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "how is it shaping people's life."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "he is going to like how the connects of people are allows them to share ideas much easier."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "Social media does helps people stay connected; it often focuses on quantity over quality."
        },
        {
            "end": undefined,
          "paraIndex": 0,
            "start": undefined,
          "text": "even if it's might not be exactly what Aristotle had in his mind."
        }
      ],
      "justification": "Frequent grammar issues—fragments, agreement errors, and punctuation—distract from the content, though overall meaning remains clear.",
      "level": "Fair",
        "suggestion": "Proofread to fix fragments and agreement (e.g., remove \"does\" before \"helps,\" change \"it's might\" to \"it might\"), and standardize punctuation; use a grammar checker or read aloud to catch errors."
    }
  ],
  "meta": {
    "categorical_points": null,
    "notes": "Test evaluation data"
  }
}

const testEssayText = `In today's world, technology plays a huge role in our lives, and one of the most important technologies is social media. Platforms such as Instagram, TikTok, and Twitter have changed our ways of communicating. While social media has many benefits, it also raises questions about its impact on our happiness, relationships, and personal growth. By taking a look at social media through the eyes of Aristotle's philosophy, we can better understand its effects and how to use it wisely.

Aristotle is one of the most impactful philosophers from ancient Greece. He founded a school that emphasized virtue. His philosophy was rooted in understanding the natural world. If Aristotle were to look at the technological aspect of modern world, such as social media. He would evaluate it through ethics, human flourishing, and how is it shaping people's life.

If Aristotle is still alive today, he would have mixed feelings about social media. On one hand, he is going to like how the connects of people are allows them to share ideas much easier. On the other hand, he would likely criticize how it can lead to bad habits and lower our self-esteem. Aristotle believed in finding a balance between extremes. However, on social media people would only post the best side of themselves, which is the best way to get likes, reviews and followers, this often make people pursuit \"fake happiness\". They would go to have \"fun\" just to have something to post on social media, which defeats the purpose of having fun. Aristotle also valued deep friendships and believed that communities are important for a good life. Social media does helps people stay connected; it often focuses on quantity over quality. Online interactions are often shallow, some people might have hundreds of \"friends\" without really knowing any of them. Aristotle is going to argue that social media weakens real relationships and makes it harder to form honest connections.

Social media is a big part of my life. I use it to stay in touch with friends and catch up what is going on in the world. I only use WeChat to commutate with my friends and
sometime post something that I truly felt happy when I am doing it. However, there is one app that I think I am spending too much time on, Tik Tok. A lot of times, I spend too much time scrolling, and it distracts me from homework or other important things. I've also felt pressure to see all the \"perfect\" picture and compare myself to others, which can make me feel insecure. While social media is fun and helpful, it's easy to get caught up in the negatives if I'm not being careful.

I pretty much agree with Aristotle's perspective on social media. His idea of finding balance makes a lot of sense to me. Social media can be great when used in a right way, but it's easy to overuse it and make it into a bad habit. Spending too much time on social media can make you feel jealous, insecure, and even become an addiction, which is going against Aristotle's idea of living a balanced and virtuous life. I also agree with Aristotle's thought on meaningful relationships. Even though social media helps me stay connected easier, but focusing on my online life could make me spend less time in real life. However, I don't completely agree with Aristotle's thoughts about technology. While he might see social media as a distraction, I think it can also be a great tool for something good. For example, social media can help people raise awareness about important issues, such as climate change or social justice. It can bring people together and create communities as well, some of them might even not exist without social media. I believe that if it is used responsibly, social media can for sure help people live a better life, even if it's might not be exactly what Aristotle had in his mind.

Aristotle's philosophy gives us a good way to think about social media and its impact on our lives. His ideas about balance, virtue, and meaningful relationships remind us to use social media responsibly and try to avoid the negativity that it brings. Even though social media can sometimes lead to bad habit, it can be a positive force as well. I agree with Aristotle's idea of balance and his focus on real relationships, but I do

believe that social media has the potential to make the world better as well. The important thing is to use it thoughtfully and not let it take over our lives. By taking Aristotle's advice, we can enjoy the benefits of social media and also living a happy and meaningful life.`

export function loadTestData() {
  const { setResult, setEssayText } = useApp.getState()
  
  console.log('🔄 Loading test data...')
  console.log('📊 Test evaluation result structure:', {
    itemsCount: testEvaluationResult.items?.length,
    overall: testEvaluationResult.overall,
    firstItem: testEvaluationResult.items?.[0]
  })
  console.log('📝 Test essay text length:', testEssayText.length)
  console.log('📝 Test essay text preview:', testEssayText.substring(0, 100))
  
  // Load the test data into the store
  console.log('🔄 Setting result...')
  setResult(testEvaluationResult)
  console.log('🔄 Setting essay text...')
  setEssayText(testEssayText)
  console.log('✅ Both setResult and setEssayText called')
  
  console.log('✅ Test data loaded successfully!')
  console.log('📊 Evaluation result:', testEvaluationResult)
  console.log('📝 Essay text loaded:', testEssayText.length, 'characters')
  console.log('📝 Essay text preview:', testEssayText.substring(0, 100) + '...')
  
  // Verify the data was set
  const { result, essayText } = useApp.getState()
  console.log('🔍 Store verification - result:', result)
  console.log('🔍 Store verification - essayText length:', essayText?.length)
  console.log('🔍 Store verification - essayText preview:', essayText?.substring(0, 100))
  
  // Force a re-render by updating the store again
  setTimeout(() => {
    console.log('🔄 Re-checking store after 1 second...')
    const { result: result2, essayText: essayText2 } = useApp.getState()
    console.log('🔍 Store re-check - result exists:', !!result2)
    console.log('🔍 Store re-check - essayText length:', essayText2?.length)
  }, 1000)
}

// Test function to verify store is working
export function testStore() {
  const { setEssayText, essayText } = useApp.getState()
  console.log('🧪 Testing store...')
  console.log('🧪 Current essayText:', essayText)
  console.log('🧪 Setting test essay text...')
  setEssayText('This is a test essay text.')
  const { essayText: newEssayText } = useApp.getState()
  console.log('🧪 New essayText:', newEssayText)
  return newEssayText
}

// Make it available globally for easy access from browser console
if (typeof window !== 'undefined') {
  (window as any).loadTestData = loadTestData
  ;(window as any).testStore = testStore
  console.log('🧪 Test data utility loaded! Use loadTestData() or testStore() in console or click the "Load Test Data" button.')
}
