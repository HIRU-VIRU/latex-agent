# User Profile Enhancement - Experience & Education Arrays

## Changes Made

### 1. Database Schema Updates

Added two new JSON columns to the `users` table:

- **`experience`**: Array of work experience entries
  ```json
  [
    {
      "company": "Company Name",
      "title": "Job Title",
      "dates": "Jan 2020 - Present",
      "location": "City, State (optional)",
      "highlights": [
        "Achievement 1",
        "Achievement 2",
        "Achievement 3"
      ]
    }
  ]
  ```

- **`education`**: Array of education entries
  ```json
  [
    {
      "school": "University Name",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "dates": "2018 - 2022",
      "location": "City, State (optional)",
      "gpa": "3.8/4.0 (optional)"
    }
  ]
  ```

### 2. API Updates

Updated profile endpoints to support experience and education arrays:

- **GET `/api/auth/profile`**: Now returns `experience` and `education` arrays
- **PUT `/api/auth/profile`**: Accepts `experience` and `education` for updates
- **POST `/api/auth/upload-resume`**: Extracts multiple experience and education entries from uploaded resumes

### 3. Resume Generation Improvements

Enhanced the resume generation agent with better project descriptions:

- **Technical terminology**: Uses industry-standard technical terms
- **Implementation focus**: Emphasizes technical implementation and architecture
- **Action verbs**: Starts bullet points with strong action verbs (Developed, Architected, Implemented, Integrated, Optimized, Designed)
- **One-line constraint**: Each bullet point fits on a single line (80-100 characters max)
- **Technology mention**: Includes specific technologies from the project's tech stack
- **Template alignment**: Preserves template formatting and alignment

### 4. Migration

Run the migration to add the new columns:

```bash
cd backend
python scripts/run_migration.py
```

Or manually run the SQL:
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS experience JSONB;
ALTER TABLE users ADD COLUMN IF NOT EXISTS education JSONB;
```

## Usage Examples

### Adding Experience via API

```bash
curl -X PUT http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "experience": [
      {
        "company": "Tech Corp",
        "title": "Senior Software Engineer",
        "dates": "Jan 2022 - Present",
        "location": "San Francisco, CA",
        "highlights": [
          "Architected microservices handling 10M+ requests/day",
          "Implemented CI/CD pipeline reducing deployment time by 60%",
          "Led team of 5 engineers on core platform features"
        ]
      },
      {
        "company": "StartupXYZ",
        "title": "Software Engineer",
        "dates": "Jun 2019 - Dec 2021",
        "highlights": [
          "Built RESTful API using FastAPI and PostgreSQL",
          "Optimized database queries improving response time by 40%"
        ]
      }
    ]
  }'
```

### Adding Education via API

```bash
curl -X PUT http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "education": [
      {
        "school": "Stanford University",
        "degree": "Master of Science",
        "field": "Computer Science",
        "dates": "2017 - 2019",
        "gpa": "3.9/4.0"
      },
      {
        "school": "UC Berkeley",
        "degree": "Bachelor of Science",
        "field": "Computer Engineering",
        "dates": "2013 - 2017",
        "gpa": "3.7/4.0"
      }
    ]
  }'
```

## Frontend Integration

The frontend should update the profile form to support:

1. **Experience Section**: Add/edit/delete multiple experience entries with company, title, dates, location, and highlights
2. **Education Section**: Add/edit/delete multiple education entries with school, degree, field, dates, location, and GPA
3. **Array Management**: UI to add, remove, and reorder entries

## Backward Compatibility

The legacy single education fields (`institution`, `degree`, `field_of_study`, `graduation_year`) are preserved for backward compatibility but the new `education` array should be used for multiple entries.
