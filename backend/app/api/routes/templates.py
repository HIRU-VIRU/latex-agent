"""
Templates Routes
================
LaTeX template management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.models.user import User
from app.models.template import Template
from app.api.deps import get_current_user, get_optional_user


router = APIRouter()


# Pydantic models
class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    latex_content: str
    category: Optional[str] = None
    is_public: bool = False


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latex_content: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    latex_content: str
    category: Optional[str]
    is_system: bool
    is_ats_tested: bool
    is_public: bool
    use_count: int
    preview_image_path: Optional[str]

    class Config:
        from_attributes = True


class TemplateListItem(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    is_system: bool
    is_ats_tested: bool
    use_count: int
    preview_image_path: Optional[str]


# Default system templates
SYSTEM_TEMPLATES = [
    {
        "name": "Classic Professional",
        "description": "Clean, ATS-friendly single-column resume template. Perfect for most job applications.",
        "category": "professional",
        "is_system": True,
        "is_ats_tested": True,
        "latex_content": r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{titlesec}
\usepackage{xcolor}

% Formatting
\pagestyle{empty}
\setlength{\parindent}{0pt}
\titleformat{\section}{\large\bfseries}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{12pt}{6pt}

\begin{document}

% Header
\begin{center}
    {\LARGE\bfseries {{NAME}}}\\[4pt]
    {{EMAIL}} | {{PHONE}} | {{LOCATION}}\\
    \href{{{GITHUB}}}{GitHub} | \href{{{LINKEDIN}}}{LinkedIn}
\end{center}

% Summary
{{?SUMMARY}}
\section{Summary}
{{SUMMARY}}
{{/SUMMARY}}

% Experience
{{?EXPERIENCE}}
\section{Experience}
{{#EXPERIENCE}}
\textbf{{{title}}} \hfill {{dates}}\\
\textit{{{company}}} \hfill {{location}}
\begin{itemize}[leftmargin=*, nosep]
{{#highlights}}
    \item {{.}}
{{/highlights}}
\end{itemize}
{{/EXPERIENCE}}
{{/EXPERIENCE}}

% Projects
{{?PROJECTS}}
\section{Projects}
{{#PROJECTS}}
\textbf{{{title}}} {{?url}}| \href{{{url}}}{Link}{{/url}} \hfill {{dates}}\\
\textit{{{technologies|join:", "}}}
\begin{itemize}[leftmargin=*, nosep]
{{#highlights}}
    \item {{.}}
{{/highlights}}
\end{itemize}
{{/PROJECTS}}
{{/PROJECTS}}

% Skills
{{?SKILLS}}
\section{Skills}
\textbf{Languages:} {{SKILLS.languages|join:", "}}\\
\textbf{Frameworks:} {{SKILLS.frameworks|join:", "}}\\
\textbf{Tools:} {{SKILLS.tools|join:", "}}
{{/SKILLS}}

% Education
{{?EDUCATION}}
\section{Education}
{{#EDUCATION}}
\textbf{{{degree}}} \hfill {{dates}}\\
\textit{{{school}}} \hfill {{location}}
{{/EDUCATION}}
{{/EDUCATION}}

\end{document}
""",
    },
    {
        "name": "Modern Tech",
        "description": "Modern two-column resume template with sidebar for skills. Great for tech roles.",
        "category": "creative",
        "is_system": True,
        "is_ats_tested": True,
        "latex_content": r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=0.5in]{geometry}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{multicol}
\usepackage{fontawesome5}

% Colors
\definecolor{primary}{RGB}{0, 79, 144}
\definecolor{gray}{RGB}{100, 100, 100}

% Formatting
\pagestyle{empty}
\setlength{\parindent}{0pt}
\titleformat{\section}{\large\bfseries\color{primary}}{}{0em}{}[\color{primary}\titlerule]
\titlespacing{\section}{0pt}{10pt}{5pt}

\begin{document}

% Header
\begin{center}
    {\Huge\bfseries\color{primary} {{NAME}}}\\[8pt]
    {\color{gray}
    \faEnvelope\ {{EMAIL}} \quad
    \faPhone\ {{PHONE}} \quad
    \faMapMarker\ {{LOCATION}}\\[4pt]
    \faGithub\ \href{{{GITHUB}}}{GitHub} \quad
    \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn}
    {{?WEBSITE}}\quad \faGlobe\ \href{{{WEBSITE}}}{Portfolio}{{/WEBSITE}}
    }
\end{center}

\vspace{8pt}

% Two column layout
\begin{multicols}{2}

% Left column - Experience & Projects
\section{Experience}
{{#EXPERIENCE}}
\textbf{{{title}}}\\
{\color{gray}\textit{{{company}}} | {{dates}}}
\begin{itemize}[leftmargin=*, nosep, topsep=3pt]
{{#highlights}}
    \item {{.}}
{{/highlights}}
\end{itemize}
\vspace{6pt}
{{/EXPERIENCE}}

\section{Projects}
{{#PROJECTS}}
\textbf{{{title}}} {{?url}}{\small\href{{{url}}}{\faExternalLink*}}{{/url}}\\
{\color{gray}\textit{{{technologies|join:", "}}}}
\begin{itemize}[leftmargin=*, nosep, topsep=3pt]
{{#highlights}}
    \item {{.}}
{{/highlights}}
\end{itemize}
\vspace{6pt}
{{/PROJECTS}}

\columnbreak

% Right column - Skills & Education
\section{Technical Skills}
{{#SKILL_CATEGORIES}}
\textbf{{{name}}}\\
{{skills|join:", "}}\\[6pt]
{{/SKILL_CATEGORIES}}

\section{Education}
{{#EDUCATION}}
\textbf{{{degree}}}\\
{\color{gray}{{school}}\\
{{dates}}}
\vspace{6pt}
{{/EDUCATION}}

{{?CERTIFICATIONS}}
\section{Certifications}
{{#CERTIFICATIONS}}
\textbf{{{name}}}\\
{\color{gray}{{issuer}} | {{date}}}\\[4pt]
{{/CERTIFICATIONS}}
{{/CERTIFICATIONS}}

\end{multicols}

\end{document}
""",
    },
    {
        "name": "Minimal Academic",
        "description": "Simple, clean academic CV template. Ideal for research and academic positions.",
        "category": "academic",
        "is_system": True,
        "is_ats_tested": True,
        "latex_content": r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=1in]{geometry}
\usepackage{enumitem}
\usepackage{hyperref}

% Formatting
\pagestyle{empty}
\setlength{\parindent}{0pt}

\newcommand{\sectiontitle}[1]{%
    \vspace{12pt}
    {\large\textsc{#1}}
    \vspace{4pt}
    \hrule
    \vspace{8pt}
}

\begin{document}

% Header
\begin{center}
    {\Large\textbf{{{NAME}}}}\\[6pt]
    {{EMAIL}} | {{PHONE}}\\
    {{LOCATION}}
\end{center}

\sectiontitle{Education}
{{#EDUCATION}}
\textbf{{{degree}}} \hfill {{dates}}\\
{{school}}, {{location}}\\
{{?gpa}}GPA: {{gpa}}{{/gpa}}
\vspace{8pt}
{{/EDUCATION}}

\sectiontitle{Research Experience}
{{#EXPERIENCE}}
\textbf{{{title}}} \hfill {{dates}}\\
{{company}}, {{location}}
\begin{itemize}[leftmargin=*, nosep]
{{#highlights}}
    \item {{.}}
{{/highlights}}
\end{itemize}
\vspace{6pt}
{{/EXPERIENCE}}

\sectiontitle{Projects}
{{#PROJECTS}}
\textbf{{{title}}} \hfill {{dates}}\\
{{description}}
\vspace{6pt}
{{/PROJECTS}}

\sectiontitle{Skills}
{{SKILLS|join:", "}}

{{?PUBLICATIONS}}
\sectiontitle{Publications}
{{#PUBLICATIONS}}
{{authors}}. ``{{title}}.'' \textit{{{venue}}}, {{year}}.\\[4pt]
{{/PUBLICATIONS}}
{{/PUBLICATIONS}}

\end{document}
""",
    },
]


# Routes
@router.get("", response_model=List[TemplateListItem])
async def list_templates(
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None,
):
    """List available templates (system + user's own)."""
    query = select(Template)
    
    if current_user:
        # System templates + user's templates + public templates
        query = query.where(
            or_(
                Template.is_system == True,
                Template.user_id == current_user.id,
                Template.is_public == True,
            )
        )
    else:
        # Only system and public templates
        query = query.where(
            or_(Template.is_system == True, Template.is_public == True)
        )
    
    if category:
        query = query.where(Template.category == category)
    
    query = query.order_by(Template.is_system.desc(), Template.use_count.desc())
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return [
        TemplateListItem(
            id=str(t.id),
            name=t.name,
            description=t.description,
            category=t.category,
            is_system=t.is_system,
            is_ats_tested=t.is_ats_tested,
            use_count=t.use_count,
            preview_image_path=t.preview_image_path,
        )
        for t in templates
    ]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific template."""
    result = await db.execute(
        select(Template).where(Template.id == uuid.UUID(template_id))
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check access
    if not template.is_system and not template.is_public:
        if not current_user or template.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        description=template.description,
        latex_content=template.latex_content,
        category=template.category,
        is_system=template.is_system,
        is_ats_tested=template.is_ats_tested,
        is_public=template.is_public,
        use_count=template.use_count,
        preview_image_path=template.preview_image_path,
    )


@router.post("", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new custom template."""
    template = Template(
        user_id=current_user.id,
        name=template_data.name,
        description=template_data.description,
        latex_content=template_data.latex_content,
        category=template_data.category,
        is_public=template_data.is_public,
        is_system=False,
        is_ats_tested=False,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        description=template.description,
        latex_content=template.latex_content,
        category=template.category,
        is_system=template.is_system,
        is_ats_tested=template.is_ats_tested,
        is_public=template.is_public,
        use_count=template.use_count,
        preview_image_path=template.preview_image_path,
    )


@router.patch("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    update_data: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a template (only own templates)."""
    result = await db.execute(
        select(Template).where(
            Template.id == uuid.UUID(template_id),
            Template.user_id == current_user.id,
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template.is_system:
        raise HTTPException(status_code=403, detail="Cannot modify system templates")
    
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        description=template.description,
        latex_content=template.latex_content,
        category=template.category,
        is_system=template.is_system,
        is_ats_tested=template.is_ats_tested,
        is_public=template.is_public,
        use_count=template.use_count,
        preview_image_path=template.preview_image_path,
    )


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a template (only own templates)."""
    result = await db.execute(
        select(Template).where(
            Template.id == uuid.UUID(template_id),
            Template.user_id == current_user.id,
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template.is_system:
        raise HTTPException(status_code=403, detail="Cannot delete system templates")
    
    await db.delete(template)
    await db.commit()
    
    return {"message": "Template deleted"}


@router.post("/init-system")
async def init_system_templates(
    db: AsyncSession = Depends(get_db),
):
    """Initialize system templates (admin only, run once)."""
    for tmpl_data in SYSTEM_TEMPLATES:
        # Check if exists
        result = await db.execute(
            select(Template).where(
                Template.name == tmpl_data["name"],
                Template.is_system == True,
            )
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            template = Template(**tmpl_data)
            db.add(template)
    
    await db.commit()
    
    return {"message": f"Initialized {len(SYSTEM_TEMPLATES)} system templates"}
