FROM texlive/texlive:latest-minimal

# Install additional packages commonly needed for resumes
RUN tlmgr install \
    latexmk \
    geometry \
    hyperref \
    fontspec \
    titlesec \
    enumitem \
    fancyhdr \
    xcolor \
    parskip \
    multicol \
    tabularx \
    booktabs \
    graphicx \
    fontawesome5 \
    academicons \
    multirow \
    makecell \
    array \
    ragged2e \
    etoolbox \
    ifthen \
    xstring \
    setspace

# Disable shell escape for security
RUN echo "shell_escape = f" >> /usr/local/texlive/*/texmf.cnf

# Create non-root user
RUN useradd -m -s /bin/bash latex
USER latex

WORKDIR /data

# Default command
CMD ["pdflatex", "-interaction=nonstopmode"]
