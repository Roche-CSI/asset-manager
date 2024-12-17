from pypager.pager import Pager as PyPager
from pypager.source import GeneratorSource


class Pager:

    def __init__(self, lines: int = 20):
        self.lines = lines

    def paged_print(self, content: str):
        p = PyPager()
        # p.add_source(GeneratorSource(self.generate_pages(content=content)))
        p.add_source(GeneratorSource(generate_a_lot_of_content()))
        self.generate_pages(content=content)
        p.run()

    def generate_pages(self, content: str):
        lines = content.splitlines()
        # print 20 at a time
        print(lines)


def generate_a_lot_of_content():
    """
    This is a function that generates content on the fly.
    It's called when the pager needs to display more content.

    This should yield prompt_toolkit `(style_string, text)` tuples.
    """
    counter = 0
    while True:
        yield [("", 'line: %i\n' % counter)]
        counter += 1


def run():
    p = Pager()
    p.add_source(GeneratorSource(generate_a_lot_of_content()))
    p.run()


if __name__ == '__main__':
    run()
