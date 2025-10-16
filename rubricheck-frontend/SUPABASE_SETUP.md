# Supabase Setup Guide for RubriCheck

This guide will help you set up Supabase authentication and database for RubriCheck.

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in to your account
3. Click "New Project"
4. Choose your organization
5. Enter project details:
   - **Name**: `rubricheck`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your users
6. Click "Create new project"
7. Wait for the project to be created (2-3 minutes)

## 2. Get Project Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (looks like: `https://your-project-id.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

## 3. Configure Environment Variables

1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Update `.env` with your Supabase credentials:
   ```env
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_ANON_KEY=eyJ...your-anon-key
   ```

## 4. Set Up Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy and paste the contents of `supabase-schema.sql`
4. Click "Run" to execute the schema

This will create:
- User profiles table
- Essays table
- Rubrics table
- Evaluations table
- Usage tracking table
- Row Level Security policies
- Default rubric templates

## 5. Configure Authentication

1. In your Supabase dashboard, go to **Authentication** → **Settings**
2. Configure the following:

### Site URL
- Set to `http://localhost:5173` for development
- Set to your production domain for production

### Redirect URLs
Add these URLs:
- `http://localhost:5173/**` (for development)
- `https://your-domain.com/**` (for production)

### Email Templates (Optional)
You can customize the email templates for:
- Confirm signup
- Reset password
- Magic link

## 6. Enable Google OAuth (Optional)

1. Go to **Authentication** → **Providers**
2. Enable **Google**
3. Get credentials from [Google Cloud Console](https://console.cloud.google.com):
   - Create a new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs:
     - `https://your-project-id.supabase.co/auth/v1/callback`
4. Copy Client ID and Client Secret to Supabase

## 7. Test the Setup

1. Start your development server:
   ```bash
   npm run dev
   ```

2. Open `http://localhost:5173`
3. Click "Sign In" in the navbar
4. Try creating an account with email/password
5. Try signing in with Google (if configured)

## 8. Database Management

### Viewing Data
- Go to **Table Editor** in Supabase dashboard
- You can view and edit data in all tables

### Row Level Security
All tables have RLS enabled, meaning:
- Users can only see their own data
- Public rubric templates are visible to everyone
- All operations are secure by default

### Backups
- Supabase automatically backs up your database
- You can also export data from **Settings** → **Database**

## 9. Production Deployment

### Environment Variables
Update your production environment with:
```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Site URL
Update the Site URL in Supabase to your production domain.

### Custom Domain (Optional)
You can set up a custom domain in **Settings** → **Custom Domains**.

## 10. Monitoring and Analytics

### Database
- Monitor queries in **Logs** → **Database**
- View performance metrics in **Reports**

### Authentication
- Monitor auth events in **Logs** → **Auth**
- View user analytics in **Reports**

## Troubleshooting

### Common Issues

1. **"Invalid API key" error**
   - Check that your environment variables are correct
   - Make sure you're using the `anon` key, not the `service_role` key

2. **"Row Level Security" errors**
   - Make sure you've run the schema SQL
   - Check that RLS policies are properly configured

3. **Google OAuth not working**
   - Verify redirect URIs in Google Cloud Console
   - Check that Google provider is enabled in Supabase

4. **Email confirmation not working**
   - Check your email templates in Supabase
   - Verify SMTP settings if using custom email

### Getting Help

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Discord](https://discord.supabase.com)
- [GitHub Issues](https://github.com/supabase/supabase/issues)

## Next Steps

Once authentication is working, you can:
1. Implement user-specific data storage
2. Add subscription management with Stripe
3. Set up usage tracking and limits
4. Add admin dashboard for user management
