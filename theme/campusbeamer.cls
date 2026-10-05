% Campus Beamer: presentation document class and package setup.
% Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
% SPDX-License-Identifier: GPL-3.0-or-later
%
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program.  If not, see <https://www.gnu.org/licenses/>.
%
% Institution-neutral presentation entry point; geometry stays in the theme.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{campusbeamer}[2026/10/02 Campus Beamer presentation harness]

\RequirePackage{kvoptions}
\SetupKeyvalOptions{family=campusclass,prefix=campusclass@}
\DeclareStringOption[chinese]{language}
\DeclareStringOption[auto]{cjk}
\DeclareStringOption[ieee]{bibstyle}
\DeclareStringOption[none]{bibsorting}
\DeclareStringOption[serif]{mathfont}
\DeclareBoolOption[true]{navigation}
\DeclareStringOption[4.8cm]{cornerwidth}
\DeclareBoolOption[false]{layoutguides}
% Keep Beamer's own options, e.g. handout, usable through the wrapper class.
% Reject the removed bibliography switch rather than silently ignoring it.
\def\campusclass@bibliographyoption{biblatex}
\def\campusclass@passoption#1=#2\@nil{%
  \def\campusclass@optionkey{#1}%
  \ifx\campusclass@optionkey\campusclass@bibliographyoption
    \ClassError{campusbeamer}{Bibliography support is always enabled}%
      {Remove the biblatex option. For a talk without citations, omit bibliography
       resources and the references page.}%
  \else
    \PassOptionsToClass{\CurrentOption}{beamer}%
  \fi
}
\DeclareDefaultOption{\expandafter\campusclass@passoption\CurrentOption=\@nil}
\ProcessKeyvalOptions*

\RequirePackage{iftex}
\ifXeTeX\else
  \ClassError{campusbeamer}{XeLaTeX is required}
    {Compile with make or latexmk -xelatex. The Campus font setup uses XeLaTeX.}
  \expandafter\endinput
\fi
\LoadClass{beamer}

\ifdefstring{\campusclass@language}{chinese}{}{%
  \ifdefstring{\campusclass@language}{english}{}{%
    \ClassError{campusbeamer}{Unknown language '\campusclass@language'}
      {Use language=chinese or language=english.}%
  }%
}
\newif\ifcampusclass@loadcjk
\ifdefstring{\campusclass@cjk}{auto}{%
  \ifdefstring{\campusclass@language}{chinese}
    {\campusclass@loadcjktrue}{\campusclass@loadcjkfalse}%
}{%
  \ifdefstring{\campusclass@cjk}{true}{\campusclass@loadcjktrue}{%
    \ifdefstring{\campusclass@cjk}{false}{\campusclass@loadcjkfalse}{%
      \ClassError{campusbeamer}{Unknown cjk setting '\campusclass@cjk'}
        {Use cjk=auto, cjk=true, or cjk=false.}%
    }%
  }%
}

% Preserve the original preamble's package order and default typography.
\usetheme{campus}
\makeatletter
\ifcampusclass@loadcjk
  \RequirePackage{xeCJK}
\fi
\ifdefstring{\campusclass@mathfont}{serif}{\usefonttheme[onlymath]{serif}}{%
  \ifdefstring{\campusclass@mathfont}{sans}{}{%
    \ClassError{campusbeamer}{Unknown mathfont '\campusclass@mathfont'}
      {Use mathfont=serif or mathfont=sans.}%
  }%
}
\edef\campusclass@loadbibliography{%
  \noexpand\RequirePackage[backend=biber,style=\campusclass@bibstyle,
    giveninits=true,sorting=\campusclass@bibsorting]{biblatex}%
}
\campusclass@loadbibliography

% Bibliography filenames belong to the talk, not to the reusable class.
\newcommand{\campusbibresource}[2][]{%
  \addbibresource[#1]{#2}%
}
\@onlypreamble\campusbibresource

\ifdefstring{\campusclass@language}{english}
  {\campussetlayout{template language=english}}%
  {\campussetlayout{template language=chinese}}%
\ifcampusclass@navigation
  \campussetlayout{section navigation=on}
\else
  \campussetlayout{section navigation=off}
\fi
\edef\campusclass@setcornerwidth{%
  \noexpand\campussetlayout{corner width=\campusclass@cornerwidth}%
}
\campusclass@setcornerwidth
\ifcampusclass@layoutguides
  \campus@layoutguidestrue
\else
  \campus@layoutguidesfalse
\fi

% Carry cover fields in the PDF itself for automatic PPTX export. Hyperref
% produces escaped Unicode PDF strings, including TeX-formatted metadata.
% This adds no visible content and does not require a metadata sidecar file.
\AtBeginDocument{%
  \begingroup
    \let\,\space % Turn visual thin spaces into ordinary metadata spaces.
    \pdfstringdef\campusclass@pdftitle{\inserttitle}%
    \pdfstringdef\campusclass@pdfsubtitle{\insertsubtitle}%
    \pdfstringdef\campusclass@pdfgroup{\@courseLabel}%
    \pdfstringdef\campusclass@pdfadvisor{\@advisor}%
    \pdfstringdef\campusclass@pdfdate{\insertdate}%
    \pdfstringdef\campusclass@pdfcontact{\@IDnumber}%
    \edef\campusclass@docinfo{%
      \noexpand\special{pdf:docinfo <<
        /CampusTitle (\campusclass@pdftitle)
        /CampusSubtitle (\campusclass@pdfsubtitle)
        /CampusGroup (\campusclass@pdfgroup)
        /CampusAdvisor (\campusclass@pdfadvisor)
        /CampusDate (\campusclass@pdfdate)
        /CampusContact (\campusclass@pdfcontact)
        /CampusLanguage (\campusclass@language)
      >>}%
    }%
    \expandafter\AtBeginDvi\expandafter{\campusclass@docinfo}%
  \endgroup
}
\endinput
