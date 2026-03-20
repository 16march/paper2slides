#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import exists, join
from os import makedirs
from uuid import uuid4
from random import choice, randint, shuffle, random, uniform
from faker import Faker
from faker.providers import BaseProvider
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from numpy.random import choice as np_choice
from compile_and_annotate_dataset import compile_latex

from page_objects import Author, Figure, Footnote, Formula, LatexDocument, PageObject, Paragraph, Section, Title, Table

### Settings ##

NB_SENTENCE_MIN = 8
NB_SENTENCE_MAX = 16
NB_AUTHOR_MIN = 1
NB_AUTHOR_MAX = 2
NB_PARAGRAPH_MIN = 24
NB_PARAGRAPH_MAX = 36
NB_FIGURE_MIN = 1
NB_FIGURE_MAX = 2
NB_FORMULA_MIN = 1
NB_FORMULA_MAX = 2
NB_FOOTNOTE_MIN = 1
NB_FOOTNOTE_MAX = 2
NB_SECTION_MIN = 5
NB_SECTION_MAX = 7
NB_TABLE_MIN = 1
NB_TABLE_MAX = 2
IM2LATEX_FORMULA = './im2latex_formulae.txt'

## End of Settings ##


class FormulaProvider(BaseProvider):
  def __init__(self, args):
    with open(IM2LATEX_FORMULA, 'r') as f:
      self.formulae = f.readlines()

  def formula(self):
    formula = choice(self.formulae)
    not_compile = ['\\vspace', '\\hspace', 'i n', 'm m', 'c m', '\\renewcommand']

    while any(str in formula for str in not_compile):
      formula = choice(self.formulae)

    return choice(self.formulae)

class FigureProvider(BaseProvider):
  def __make_folder__(self, fdir):
    self.fake = Faker()
    self.folder = 'figures'
    if not exists(join(fdir, self.folder)):
      makedirs(join(fdir, self.folder))

  def figure(self, fdir):
    self.__make_folder__(fdir)
    plots = [self.cos_sin, self.scatter_plot, self.line_plot]
    figure = choice(plots)(fdir)
    plt.close('all')
    plt.style.use('default')
    return figure

  def cos_sin(self, fdir):
    plt.style.use("ggplot")

    t = np.arange(0.0, 2.0, 0.1)
    s = np.sin(2 * np.pi * t) + randint(-2, 2)
    s2 = np.cos(2 * np.pi * t) + randint(-2, 2)
    plt.plot(t, s, "o-", lw=4.1, color=(uniform(0, 1), uniform(0, 1), uniform(0, 1)))
    plt.plot(t, s2, "o-", lw=4.1, color=(uniform(0, 1), uniform(0, 1), uniform(0, 1)))
    plt.title(self.fake.sentence(nb_words=3, variable_nb_words=True)[:-1])
    plt.xlabel(self.fake.word())
    plt.ylabel(self.fake.word())
    plt.grid(True)

    fpath = f'{self.folder}/{uuid4().hex[:8]}.png'
    fpathabs = join(fdir, fpath)
    plt.savefig(fpathabs, bbox_inches='tight')
    return f'./{fpath}'

  def scatter_plot(self, fdir):
    N = randint(40, 80)
    x = np.random.rand(N)
    y = np.random.rand(N)
    colors = np.random.rand(N)
    area = (20 * np.random.rand(N))**2

    plt.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.title(self.fake.sentence(nb_words=3, variable_nb_words=True)[:-1])
    plt.xlabel(self.fake.word())
    plt.ylabel(self.fake.word())

    fpath = f'{self.folder}/{uuid4().hex[:8]}.png'
    fpathabs = join(fdir, fpath)
    plt.savefig(fpathabs, bbox_inches='tight')
    return f'./{fpath}'

  def line_plot(self, fdir):
    x = np.linspace(0, 10)
    plots = [np.sin, np.cos, np.tan]

    for i in range(randint(3, 8)):
      plt.plot(x, choice(plots)(x) + i * x + np.random.randn(50))

    plt.title(self.fake.sentence(nb_words=3, variable_nb_words=True)[:-1])
    plt.xlabel(self.fake.word())
    plt.ylabel(self.fake.word())

    fpath = f'{self.folder}/{uuid4().hex[:8]}.png'
    fpathabs = join(fdir, fpath)
    plt.savefig(fpathabs, bbox_inches='tight')
    return f'./{fpath}'

class TableProvider(BaseProvider):
  def __init__(self, args):
    self.fake = Faker()

  def table(self):
    nb_column = randint(2, 5)
    nb_row = randint(3, 8)
    array = np.random.rand(nb_row, nb_column)
    vectorize = np.vectorize(lambda x: f'{x*100:.2f}')
    array = vectorize(array)
    headers = [self.fake.word() for _ in range(nb_column)]
    return tabulate(array, headers, tablefmt='latex')

class AuthorProvider(BaseProvider):
  def __init__(self, args):
    self.fake = Faker()

  def author(self):
    profile = self.fake.simple_profile()
    profile['address'] = profile['address'].split('\n')[0]
    return (profile['name'], profile['address'], profile['mail'])

def randomize_params():
  params = {
    'nb_sentences': randint(NB_SENTENCE_MIN, NB_SENTENCE_MAX)
  }

  return params

def generate_docs(fake, args):
  docs = LatexDocument()

  title = Title(0, fake.sentence(nb_words=6, variable_nb_words=True)[:-1])
  docs.set_title(title)

  for i in range(randint(NB_AUTHOR_MIN, NB_AUTHOR_MAX)):
    docs.add_author(Author(i, fake.author()))

  paragraphs = []
  for i in range(randint(NB_PARAGRAPH_MIN, NB_PARAGRAPH_MAX)):
    params = randomize_params()
    content = fake.paragraph(nb_sentences=params['nb_sentences'], variable_nb_sentences=True)
    height = len(content) / 1000
    paragraph = Paragraph(i, content, height=height)
    paragraphs.append(paragraph)
  
  figures = []
  for i in range(randint(NB_FIGURE_MIN, NB_FIGURE_MAX)):
    figures.append(Figure(i, fake.figure(args.out_dir)))

  tables = []
  for i in range(randint(NB_TABLE_MIN, NB_TABLE_MAX)):
    tables.append(Table(i, fake.table()))

  formulas = []
  for i in range(randint(NB_FORMULA_MIN, NB_FORMULA_MAX)):
    formulas.append(Formula(i, fake.formula()))

  footnotes = []
  for i in range(randint(NB_FOOTNOTE_MIN, NB_FOOTNOTE_MAX)):
    footnote_text = fake.sentence(nb_words=5, variable_nb_words=True)[:-1]
    footnotes.append(Footnote(i, footnote_text))

  elements = paragraphs + figures + tables + formulas + footnotes
  shuffle(elements)

  nb_elements = len(elements)
  nb_section = randint(NB_SECTION_MIN, NB_SECTION_MAX)
  nb_objects_per_session = round(nb_elements / nb_section)
  for i in range(nb_section):
    section = fake.sentence(nb_words=3, variable_nb_words=True)[:-1]
    docs.add_element(Section(i, section))
    els = elements[i*nb_objects_per_session:i*nb_objects_per_session+nb_objects_per_session]
    if i == nb_section - 1:
      els = elements[i*nb_objects_per_session:]
    for el in els:
      docs.add_element(el)

  return docs

def main():
    args = parse_args()

    fake = Faker()
    fake.add_provider(FormulaProvider)
    fake.add_provider(FigureProvider)
    fake.add_provider(TableProvider)
    fake.add_provider(AuthorProvider)

    makedirs(args.out_dir, exist_ok=True)

    for i in range(args.n):
      fname = f'latex_dataset{i + args.start}.tex'
      generate_docs(fake, args).write_document(join(args.out_dir, fname))
      pdf, _ = compile_latex(fname, args.out_dir, compile_twice=False)
      while (pdf is None):
        generate_docs(fake, args).write_document(join(args.out_dir, fname))
        pdf, _ = compile_latex(fname, args.out_dir)

def parse_args():
  from argparse import ArgumentParser

  parser = ArgumentParser()
  parser.add_argument('-n',
                      dest='n',
                      type=int,
                      help='number of latex files to be generated')
  parser.add_argument('--start',
                      dest='start',
                      type=int,
                      default=0,
                      help='Starting number (for resuming generation)')
  parser.add_argument('--out_dir',
                      dest='out_dir',
                      help='Output directory')
  return parser.parse_args()

if __name__ == "__main__":
    main()