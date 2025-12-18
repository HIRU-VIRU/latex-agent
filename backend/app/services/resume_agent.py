"""
Resume Generation Agent
=======================
Generates ATS-friendly LaTeX resumes using Gemini with strict grounding.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import structlog

from app.services.gemini_client import gemini_client


logger = structlog.get_logger()


@dataclass
class GenerationResult:
    """Result of resume generation."""
    latex_content: str
    warnings: List[str]
    changes_made: List[str]
    tokens_used: int


# Anti-hallucination system prompt
SYSTEM_PROMPT = """You are a professional resume LaTeX formatter. Your ONLY job is to fill a LaTeX template with provided user data.

CRITICAL RULES - VIOLATION WILL CAUSE ERRORS:

1. GROUNDING REQUIREMENT:
   - ONLY use information explicitly provided in the <user_data> section
   - NEVER invent, assume, or hallucinate ANY information
   - This includes: projects, skills, companies, dates, achievements, metrics, or ANY facts
   
2. MISSING DATA HANDLING:
   - If required data is missing, output "[REQUIRED: field_name]" as placeholder
   - If optional data is missing, omit that section entirely
   - NEVER fill gaps with invented information

3. ONE-PAGE CONSTRAINT:
   - Resume MUST fit on a single page (maximum)
   - Keep descriptions concise and impactful
   - Each project should have EXACTLY 3 single-line bullet points (no more, no less)
   - Use compact LaTeX formatting (smaller margins, tight spacing if needed)
   - Prioritize most important information

4. ALLOWED TRANSFORMATIONS:
   - Rephrase for clarity and ATS optimization (but preserve ALL facts)
   - Condense bullet points to single lines (max 80-100 characters each)
   - Reorder bullet points for impact
   - Adjust formatting to match template structure
   - Fix grammar and spelling
   - Use technical terminology and industry-standard terms
   - Focus on technical implementation details and architecture
   
5. FORBIDDEN TRANSFORMATIONS:
   - Adding metrics not in original data (e.g., "improved by 50%")
   - Adding technologies not listed
   - Inventing project features
   - Creating achievements not mentioned
   - Adding company names or dates not provided

6. LATEX SYNTAX REQUIREMENTS (CRITICAL):
   - Every opening brace { MUST have a matching closing brace }
   - Never use \\\\ at the start of a line or on an empty line
   - Escape special characters: & % $ # _ { } ~ ^ \\
   - Always close all LaTeX commands properly
   - Test: Count your { and } - they MUST be equal

7. OUTPUT FORMAT:
   - Return ONLY valid LaTeX code
   - Preserve all template commands exactly
   - Escape special LaTeX characters: & % $ # _ { } ~ ^

VERIFICATION STEP:
Before outputting, mentally verify each fact against <user_data>. 
If you cannot find the source for a claim, DO NOT include it."""


class ResumeGenerationAgent:
    """
    Agent for generating resumes using Gemini with strict anti-hallucination controls.
    """
    
    def __init__(self):
        pass
    
    async def generate_resume(
        self,
        template_latex: str,
        user_data: Dict[str, Any],
        jd_context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.2,
    ) -> GenerationResult:
        """
        Generate a filled LaTeX resume from template and user data.
        
        Args:
            template_latex: LaTeX template with placeholders
            user_data: User data to fill placeholders
            jd_context: Optional job description context for tailoring
            temperature: LLM temperature (lower = more deterministic)
            
        Returns:
            GenerationResult with LaTeX content and metadata
        """
        # Build the prompt
        prompt = self._build_generation_prompt(
            template=template_latex,
            user_data=user_data,
            jd_context=jd_context,
        )
        
        try:
            response = await gemini_client.generate_content(
                prompt=prompt,
                system_instruction=SYSTEM_PROMPT,
                temperature=temperature,
                max_tokens=8192,
            )
            
            # Extract LaTeX from response (handle potential markdown wrapping)
            latex_content = self._extract_latex(response)
            
            # Validate grounding
            warnings = self._validate_grounding(latex_content, user_data)
            
            return GenerationResult(
                latex_content=latex_content,
                warnings=warnings,
                changes_made=["Filled template with user data"],
                tokens_used=len(response.split()),  # Approximate
            )
            
        except Exception as e:
            logger.error(f"Resume generation failed: {e}")
            raise
    
    def _build_generation_prompt(
        self,
        template: str,
        user_data: Dict[str, Any],
        jd_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build the generation prompt with user data."""
        
        # Format user data section
        user_data_str = self._format_user_data(user_data)
        
        # Format JD context if provided
        jd_str = ""
        if jd_context:
            jd_str = f"""
<jd_context>
Target Role: {jd_context.get('title', 'N/A')}
Company: {jd_context.get('company', 'N/A')}
Key Requirements: {', '.join(jd_context.get('required_skills', [])[:10])}

Use this context to:
- Prioritize skills matching the requirements
- Order projects by relevance
- Tailor language to the role
DO NOT add any information not in user_data.
</jd_context>
"""
        
        prompt = f"""Fill this LaTeX resume template with the provided user data.

<template>
{template}
</template>

<user_data>
{user_data_str}
</user_data>

{jd_str}

CRITICAL FORMATTING REQUIREMENTS:
- Resume MUST fit on ONE PAGE ONLY
- Each project must have EXACTLY 3 bullet points (single line each, max 80-100 characters)
- Keep all descriptions concise and impactful
- Use compact spacing and formatting

LATEX SYNTAX RULES (MUST FOLLOW):
- Every {{ must have a matching }}
- Never start a line with \\\\
- Escape special chars: use \\& \\% \\$ \\# \\_ for & % $ # _
- Close ALL commands: \\command{{text}} not \\command{{text

INSTRUCTIONS:
1. Replace all placeholders ({{{{PLACEHOLDER}}}}) with corresponding user data
2. For {{{{#ARRAY}}}}...{{{{/ARRAY}}}} sections, iterate over the array
3. For each PROJECT bullet point:
   - Use technical terminology (e.g., "Implemented RESTful API", "Architected microservices", "Optimized database queries")
   - Focus on technical implementation and architecture ("Built scalable X using Y", "Integrated Z with A")
   - Each point must fit on ONE LINE (max 80-100 characters)
   - Include specific technologies used (from the project's tech stack)
   - Start with strong action verbs (Developed, Architected, Implemented, Integrated, Optimized, Designed)
   - For project URLs: use \\href{{url}}{{Link}} format, do NOT display full URL text
4. **CRITICAL** For missing/empty data: COMPLETELY DELETE the entire section (including headers and ALL content)
   - Check if WORK EXPERIENCE data exists - if NO, DELETE entire \\section{{Experience}} block
   - Check if EDUCATION data exists - if NO, DELETE entire \\section{{Education}} block  
   - An empty array [] means NO DATA - DELETE that section
   - NEVER leave empty commands with blank arguments
   - DO NOT show placeholders or empty structures
   - Example: if "WORK EXPERIENCE:" is not in user_data, DELETE the Experience section completely
5. For EDUCATION section:
   - Include ALL education entries from the data (if user has 2 education items, show both)
   - Use school, degree, field, dates, location, gpa fields
6. Preserve all LaTeX commands and structure for sections that HAVE data
7. Maintain template alignment - do NOT modify spacing, indentation, or formatting commands
8. Ensure the final output will compile to a single-page PDF
9. VERIFY: Count all braces - they must be balanced!
10. VERIFY: No command has empty blank arguments
11. Return ONLY the filled LaTeX code, no explanations

OUTPUT: Complete, valid LaTeX code ready for compilation (single page)."""

        return prompt
    
    def _format_user_data(self, user_data: Dict[str, Any]) -> str:
        """Format user data for the prompt."""
        import json
        
        # Create a clean representation
        formatted_parts = []
        
        # Personal info
        if "personal" in user_data:
            formatted_parts.append("PERSONAL INFORMATION:")
            for key, value in user_data["personal"].items():
                formatted_parts.append(f"  {key}: {value}")
        
        # Skills
        if "skills" in user_data:
            formatted_parts.append(f"\nSKILLS: {', '.join(user_data['skills'])}")
        
        # Projects
        if "projects" in user_data:
            formatted_parts.append("\nPROJECTS:")
            for i, proj in enumerate(user_data["projects"], 1):
                formatted_parts.append(f"\n  Project {i}:")
                formatted_parts.append(f"    Title: {proj.get('title', 'N/A')}")
                formatted_parts.append(f"    Description: {proj.get('description', 'N/A')}")
                if proj.get("technologies"):
                    formatted_parts.append(f"    Technologies: {', '.join(proj['technologies'])}")
                if proj.get("highlights"):
                    formatted_parts.append(f"    Achievements:")
                    for h in proj["highlights"]:
                        formatted_parts.append(f"      - {h}")
                if proj.get("url"):
                    formatted_parts.append(f"    URL: {proj['url']}")
                if proj.get("dates"):
                    formatted_parts.append(f"    Dates: {proj['dates']}")
        
        # Experience
        if "experience" in user_data and user_data["experience"]:
            formatted_parts.append("\nWORK EXPERIENCE:")
            for i, exp in enumerate(user_data["experience"], 1):
                formatted_parts.append(f"\n  Experience {i}:")
                formatted_parts.append(f"    Company: {exp.get('company', 'N/A')}")
                formatted_parts.append(f"    Title: {exp.get('title', 'N/A')}")
                formatted_parts.append(f"    Dates: {exp.get('dates', 'N/A')}")
                if exp.get('location'):
                    formatted_parts.append(f"    Location: {exp.get('location')}")
                if exp.get("highlights"):
                    formatted_parts.append(f"    Responsibilities:")
                    for h in exp["highlights"]:
                        formatted_parts.append(f"      - {h}")
        
        # Education
        if "education" in user_data and user_data["education"]:
            formatted_parts.append("\nEDUCATION:")
            for i, edu in enumerate(user_data["education"], 1):
                formatted_parts.append(f"\n  Education {i}:")
                formatted_parts.append(f"    School: {edu.get('school', 'N/A')}")
                formatted_parts.append(f"    Degree: {edu.get('degree', 'N/A')}")
                if edu.get('field'):
                    formatted_parts.append(f"    Field: {edu.get('field')}")
                formatted_parts.append(f"    Dates: {edu.get('dates', 'N/A')}")
                if edu.get('location'):
                    formatted_parts.append(f"    Location: {edu.get('location')}")
                if edu.get('gpa'):
                    formatted_parts.append(f"    GPA: {edu.get('gpa')}")
        
        # Any additional fields
        for key, value in user_data.items():
            if key not in {"personal", "skills", "projects", "experience", "education"}:
                if isinstance(value, list):
                    formatted_parts.append(f"\n{key.upper()}: {', '.join(str(v) for v in value)}")
                else:
                    formatted_parts.append(f"\n{key.upper()}: {value}")
        
        return "\n".join(formatted_parts)
    
    def _extract_latex(self, response: str) -> str:
        """Extract LaTeX content from response, handling markdown wrapping."""
        content = response.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```latex"):
            content = content[8:]
        elif content.startswith("```"):
            content = content[3:]
        
        # Remove trailing markdown if present
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        # Validate balanced braces
        if not self._validate_braces(content):
            logger.warning("Generated LaTeX has unbalanced braces!")
            # Try to find and log the issue
            open_count = content.count('{')
            close_count = content.count('}')
            logger.warning(f"Open braces: {open_count}, Close braces: {close_count}")
        
        # Remove sections containing placeholders
        content = self._remove_placeholder_sections(content)
        
        return content
    
    def _validate_braces(self, latex: str) -> bool:
        """Validate that all braces are balanced in LaTeX."""
        stack = []
        for i, char in enumerate(latex):
            if char == '{':
                # Check if it's escaped
                if i > 0 and latex[i-1] == '\\' and i > 1 and latex[i-2] == '\\':
                    continue  # \\{ is escaped
                stack.append(i)
            elif char == '}':
                if i > 0 and latex[i-1] == '\\' and i > 1 and latex[i-2] == '\\':
                    continue  # \\} is escaped
                if not stack:
                    return False
                stack.pop()
        return len(stack) == 0
    
    def _remove_placeholder_sections(self, latex: str) -> str:
        """Remove any LaTeX sections that contain [REQUIRED:] placeholders."""
        import re
        
        # Find the position of the first section and end of document
        first_section_match = re.search(r'\\section\{', latex)
        if not first_section_match:
            return latex  # No sections found
        
        doc_end_match = re.search(r'\\end\{document\}', latex)
        if not doc_end_match:
            return latex  # No end of document found
        
        # Split the document
        doc_start = latex[:first_section_match.start()]
        doc_end = latex[doc_end_match.start():]
        sections_text = latex[first_section_match.start():doc_end_match.start()]
        
        # Find all sections with their content
        section_pattern = r'(\\section\{[^}]+\}.*?)(?=\\section\{|$)'
        sections = re.findall(section_pattern, sections_text, re.DOTALL)
        
        # Filter out sections containing placeholders
        cleaned_sections = []
        for section in sections:
            if '[REQUIRED:' in section:
                # Extract section name for logging
                section_name_match = re.search(r'\\section\{([^}]+)\}', section)
                section_name = section_name_match.group(1) if section_name_match else 'Unknown'
                logger.info(f"Removed section '{section_name}' containing placeholders")
            else:
                cleaned_sections.append(section)
        
        # Reconstruct the document
        return doc_start + ''.join(cleaned_sections) + doc_end
    
    def _validate_grounding(
        self,
        latex: str,
        user_data: Dict[str, Any],
    ) -> List[str]:
        """
        Validate that generated content is grounded in user data.
        Returns list of warnings for potentially ungrounded content.
        """
        warnings = []
        
        # Check for placeholder markers that weren't filled
        import re
        unfilled = re.findall(r'\[REQUIRED: ([^\]]+)\]', latex)
        if unfilled:
            warnings.extend([f"Missing required field: {f}" for f in unfilled])
        
        # Check for common hallucination patterns
        hallucination_patterns = [
            (r'\d+%', "percentage"),
            (r'\$[\d,]+', "dollar amount"),
            (r'\d+x', "multiplier"),
        ]
        
        for pattern, desc in hallucination_patterns:
            matches = re.findall(pattern, latex)
            if matches:
                # Check if these values exist in user data
                user_data_str = str(user_data)
                for match in matches:
                    if match not in user_data_str:
                        warnings.append(f"Potential ungrounded {desc}: {match}")
        
        return warnings
    
    async def tailor_project_description(
        self,
        project: Dict[str, Any],
        jd_keywords: List[str],
    ) -> Dict[str, Any]:
        """
        Tailor a project description for a specific job.
        Only rephrases - does not add new information.
        
        Args:
            project: Project data dict
            jd_keywords: Keywords from job description
            
        Returns:
            Project with tailored description and highlights
        """
        prompt = f"""Tailor this project for a job requiring: {', '.join(jd_keywords[:10])}

PROJECT:
Title: {project.get('title')}
Description: {project.get('description')}
Technologies: {', '.join(project.get('technologies', []))}
Highlights:
{chr(10).join('- ' + h for h in project.get('highlights', []))}

RULES:
1. ONLY rephrase existing content - DO NOT add new facts
2. Emphasize technologies that match job keywords
3. Keep same meaning, just optimize wording
4. Preserve all technical accuracy

Return JSON with "description" and "highlights" (array) keys."""

        try:
            result = await gemini_client.generate_json(
                prompt=prompt,
                system_instruction="You are a resume optimizer. Rephrase content for relevance but NEVER add information not present in the original.",
                temperature=0.3,
            )
            
            return {
                **project,
                "description": result.get("description", project.get("description")),
                "highlights": result.get("highlights", project.get("highlights", [])),
            }
        except Exception as e:
            logger.error(f"Project tailoring failed: {e}")
            return project


# Global instance
resume_agent = ResumeGenerationAgent()
