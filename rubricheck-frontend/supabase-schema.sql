-- RubriCheck Database Schema
-- Run this in your Supabase SQL editor

-- Enable Row Level Security
ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'educator')),
  stripe_customer_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create essays table
CREATE TABLE IF NOT EXISTS essays (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  file_type TEXT CHECK (file_type IN ('pdf', 'docx', 'txt')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create rubrics table
CREATE TABLE IF NOT EXISTS rubrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  criteria JSONB NOT NULL,
  is_template BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create evaluations table
CREATE TABLE IF NOT EXISTS evaluations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  essay_id UUID REFERENCES essays(id) ON DELETE CASCADE,
  rubric_id UUID REFERENCES rubrics(id) ON DELETE CASCADE,
  results JSONB NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create usage_tracking table
CREATE TABLE IF NOT EXISTS usage_tracking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  month_year TEXT NOT NULL, -- Format: '2024-01'
  essays_count INTEGER DEFAULT 0,
  evaluations_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, month_year)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_essays_user_id ON essays(user_id);
CREATE INDEX IF NOT EXISTS idx_essays_created_at ON essays(created_at);
CREATE INDEX IF NOT EXISTS idx_rubrics_user_id ON rubrics(user_id);
CREATE INDEX IF NOT EXISTS idx_rubrics_is_template ON rubrics(is_template);
CREATE INDEX IF NOT EXISTS idx_evaluations_user_id ON evaluations(user_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_essay_id ON evaluations(essay_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_rubric_id ON evaluations(rubric_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_status ON evaluations(status);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_month_year ON usage_tracking(month_year);

-- Row Level Security Policies

-- User profiles: Users can only access their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON user_profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (auth.uid() = user_id);

-- Essays: Users can only access their own essays
CREATE POLICY "Users can view own essays" ON essays
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own essays" ON essays
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own essays" ON essays
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own essays" ON essays
  FOR DELETE USING (auth.uid() = user_id);

-- Rubrics: Users can access their own rubrics and public templates
CREATE POLICY "Users can view own rubrics" ON rubrics
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view public templates" ON rubrics
  FOR SELECT USING (is_template = TRUE);

CREATE POLICY "Users can insert own rubrics" ON rubrics
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own rubrics" ON rubrics
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own rubrics" ON rubrics
  FOR DELETE USING (auth.uid() = user_id);

-- Evaluations: Users can only access their own evaluations
CREATE POLICY "Users can view own evaluations" ON evaluations
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own evaluations" ON evaluations
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own evaluations" ON evaluations
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own evaluations" ON evaluations
  FOR DELETE USING (auth.uid() = user_id);

-- Usage tracking: Users can only access their own usage data
CREATE POLICY "Users can view own usage" ON usage_tracking
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own usage" ON usage_tracking
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own usage" ON usage_tracking
  FOR UPDATE USING (auth.uid() = user_id);

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE essays ENABLE ROW LEVEL SECURITY;
ALTER TABLE rubrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

-- Function to automatically create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (user_id, subscription_tier)
  VALUES (NEW.id, 'free');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create user profile when a new user signs up
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add updated_at triggers
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_essays_updated_at
  BEFORE UPDATE ON essays
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_rubrics_updated_at
  BEFORE UPDATE ON rubrics
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_evaluations_updated_at
  BEFORE UPDATE ON evaluations
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Insert some default rubric templates
INSERT INTO rubrics (name, criteria, is_template, user_id) VALUES
(
  'General Essay Rubric',
  '{
    "criteria": [
      {
        "id": "focus_and_thesis",
        "name": "Focus & Thesis",
        "description": "Clear thesis statement and focused argument",
        "weight": 20,
        "levels": [
          {"level": "Excellent", "score": 5, "description": "Clear, compelling thesis with strong focus"},
          {"level": "Proficient", "score": 4, "description": "Clear thesis with good focus"},
          {"level": "Meets expectations", "score": 3, "description": "Thesis present but could be clearer"},
          {"level": "Developing", "score": 2, "description": "Thesis unclear or weak focus"},
          {"level": "Poor", "score": 1, "description": "No clear thesis or unfocused"}
        ]
      },
      {
        "id": "organization_and_flow",
        "name": "Organization & Flow",
        "description": "Logical structure and smooth transitions",
        "weight": 20,
        "levels": [
          {"level": "Excellent", "score": 5, "description": "Excellent organization with smooth transitions"},
          {"level": "Proficient", "score": 4, "description": "Good organization with clear transitions"},
          {"level": "Meets expectations", "score": 3, "description": "Adequate organization"},
          {"level": "Developing", "score": 2, "description": "Poor organization or weak transitions"},
          {"level": "Poor", "score": 1, "description": "No clear organization"}
        ]
      },
      {
        "id": "evidence_and_support",
        "name": "Evidence & Support",
        "description": "Relevant evidence and strong support for claims",
        "weight": 20,
        "levels": [
          {"level": "Excellent", "score": 5, "description": "Strong, relevant evidence throughout"},
          {"level": "Proficient", "score": 4, "description": "Good evidence with minor gaps"},
          {"level": "Meets expectations", "score": 3, "description": "Adequate evidence"},
          {"level": "Developing", "score": 2, "description": "Limited or weak evidence"},
          {"level": "Poor", "score": 1, "description": "Little to no evidence"}
        ]
      },
      {
        "id": "analysis_and_insight",
        "name": "Analysis & Insight",
        "description": "Depth of analysis and critical thinking",
        "weight": 20,
        "levels": [
          {"level": "Excellent", "score": 5, "description": "Deep analysis with original insights"},
          {"level": "Proficient", "score": 4, "description": "Good analysis with some insights"},
          {"level": "Meets expectations", "score": 3, "description": "Adequate analysis"},
          {"level": "Developing", "score": 2, "description": "Surface-level analysis"},
          {"level": "Poor", "score": 1, "description": "Little to no analysis"}
        ]
      },
      {
        "id": "style_and_clarity",
        "name": "Style & Clarity",
        "description": "Clear writing style and effective communication",
        "weight": 20,
        "levels": [
          {"level": "Excellent", "score": 5, "description": "Clear, engaging style"},
          {"level": "Proficient", "score": 4, "description": "Clear style with minor issues"},
          {"level": "Meets expectations", "score": 3, "description": "Generally clear"},
          {"level": "Developing", "score": 2, "description": "Unclear at times"},
          {"level": "Poor", "score": 1, "description": "Unclear or confusing"}
        ]
      }
    ]
  }',
  TRUE,
  '00000000-0000-0000-0000-000000000000' -- System user ID for templates
);
