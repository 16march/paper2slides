#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class PageObject(object):
  def __init__(self, id, content, height=1):
    self.id = id
    self.alignment = 't' #top
    self.height = f'{height}\\textheight'
    self.width = '\\linewidth'
    self.text = content
    self.content = content

  def to_latex(self):
    return f"""\\clipbox{{0pt}}{{
  \\begin{{minipage}}[{self.alignment}][{self.height}]{{{self.width}}}{{
    {self.content}
  }}
  \\end{{minipage}}
}}"""

class Paragraph(PageObject):
  def __init__(self, id, content, height=1):
    super(Paragraph, self).__init__(id, content, height)
    self.type = 'paragraph'
    self.content = f"""
    \\measure[{self.type}_{self.id}]{{{self.text}}}{{
      \\parbox{{\\linewidth}}{{
      \\strut
      \\setlength{{\\parindent}}{{0.7cm}}
      \\indent
      {content}
      \\strut
    }}}}"""
    self.height = ''

class Section(PageObject):
  def __init__(self, id, content, height=1):
    super(Section, self).__init__(id, content, height)
    self.type = 'section'
    self.content = f'\\section{{\\measure[{self.type}_{self.id}]{{{self.text}}}{{{content}}}}}'
    self.height = ''

class Formula(PageObject):
  def __init__(self, id, content, height=1):
    super(Formula, self).__init__(id, content, height)
    self.type = 'formula'
    self.text = 'formula'
    self.content = f'''\\begin{{center}}
      \\strut
      \\measure[{self.type}_{self.id}]{{{self.text}}}{{
        $ {content} $
      }}
      \\strut
    \\end{{center}}
    '''
    self.height = ''

class Figure(PageObject):
  def __init__(self, id, content, height=1):
    super(Figure, self).__init__(id, content, height)
    self.type = 'figure'
    self.content = f'''\\measure[{self.type}_{self.id}]{{{self.text}}}{{
      \\includegraphics[width=0.95\\linewidth]{{{content}}}
    }}
    '''
    self.height = ''

class Table(PageObject):
  def __init__(self, id, content, height=1):
    super(Table, self).__init__(id, content, height)
    self.type = 'table'
    self.text = 'table'
    self.content = f'''\\measure[{self.type}_{self.id}]{{{self.text}}}{{
      {content}
    }}
    '''
    self.height = ''

class Title(PageObject):
  def __init__(self, id, content, height=1):
    super(Title, self).__init__(id, content, height)
    self.type = 'title'
    self.content = f'''\\measure[{self.type}_{self.id}]{{{self.text}}}{{
      \\textbf{{{content}}}
    }}
    '''
    self.height = ''

  def to_latex(self):
    return self.content

class Author(PageObject):
  def __init__(self, id, content, height=1):
    super(Author, self).__init__(id, content, height)
    self.type = 'author'
    
    name, address, mail = content

    author = f'''{name} \\\\ {address} \\\\ \\texttt{{{mail}}}'''

    self.text = f'{name},{address},{mail}'.replace('\\\\', '')

    self.content = f'''\\measure[{self.type}_{self.id}]{{{self.text}}}{{\\parbox{{0.4\\linewidth}}{{
      \\centering
      {author}
    }}}}
    '''
  
  def to_latex(self):
    return self.content

class Footnote(PageObject):
  def __init__(self, id, content, height=1):
    super(Footnote, self).__init__(id, content, height)
    self.type = 'footnote'
    self.content = f'''\\footnotetext[{self.id + 1}]{{\\measure[{self.type}_{self.id}]{{{self.text}}}
      {{{content}}}
    }}
    '''
    self.height = ''

  def to_latex(self):
    return self.content

class LatexDocument(object):
  def __init__(self):
    self.nodes = []
    self.preamble = r""" 
\documentclass[11pt,a4paper, twocolumn]{article}
\usepackage{trimclip}
\usepackage{pgfplots}
\usepackage{amsmath}
\usepackage{zref-savepos}
    """

    self.measure_command = r"""
\makeatletter
\renewcommand\footnoterule{%
  \kern-3\p@
  \moveright1em\vbox{\hrule\@width.4\columnwidth}\nointerlineskip
  \kern2.6\p@}
\makeatother

\makeatletter
\newcommand\dimtomm[1]{%
    \strip@pt\dimexpr 0.351459804\dimexpr#1\relax\relax %
}
\makeatother

\makeatletter
\def\convertto#1#2{\strip@pt\dimexpr #2*65536/\number\dimexpr 1#1}
\makeatother

\newwrite\mywrite
\immediate\openout\mywrite=\jobname.pos\relax
\newlength{\dd}
\newlength{\ww}
\newlength{\hh}
\newcommand{\measure}[3][1]%
   {\zsavepos{#1-ll}% Store the current position as #1-ll
    {#3}% Output the text provided as mandatory argument
    \settodepth{\dd}{#3}% Measure the depth of the mandatory argument
    \settowidth{\ww}{#3}% Measure the width of the mandatory argument
    \settoheight{\hh}{#3}% Measure the height of the mandatory argument
    \immediate\write\mywrite{#1,\dimtomm{\zposx{#1-ll}sp},\dimtomm{\zposy{#1-ll}sp},\convertto{mm}{\the\dd},\convertto{mm}{\the\hh},\convertto{mm}{\the\paperheight},\convertto{mm}{\the\ww},\convertto{mm}{\the\paperwidth},\convertto{mm}{\the\linewidth},"#2"}%
   }
    """

    self.elements = []
    self.title = ''
    self.authors = []

  def add_element(self, element: PageObject):
    self.elements.append(element.to_latex())

  def set_title(self, title: Title):
    self.title = title.to_latex()

  def add_author(self, author: Author):
    self.authors.append(author.to_latex())

  def make_title(self):
    authors = '\\and'.join(self.authors)

    return f'''
\\twocolumn[
  \\begin{{@twocolumnfalse}}
    \\begin{{center}}%
      {{\\LARGE
        {self.title}
      \\par}}
      \\vskip 2em%
      {{\\large
       \\lineskip .75em%
        \\begin{{tabular}}[t]{{c}}%
          {authors}
        \\end{{tabular}}
        \\par}}%
        \\vskip 1.5em%
    \\end{{center}}\\par
  \\end{{@twocolumnfalse}}
]
    '''
  
  def write_document(self, fname):
    with open(fname, 'w') as f:
      tex = (self.preamble
            + self.measure_command
            + '\n\\begin{document}\n\n' 
            + self.make_title()
            + '\n\n'.join(self.elements) 
            + '\n\\end{document}')

      f.write(tex)