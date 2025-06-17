'''Column of Section.

In most cases, one section per page. But in case multi-columns page, sections are used
to distinguish these different layouts.

.. note::
    Currently, support at most two columns.

::

    {
        'bbox': (x0, y0, x1, y1),
        'blocks': [{
            ... # block instances
        }, ...],
        'shapes': [{
            ... # shape instances
        }, ...]
    }
'''

from ..common.Collection import Collection
from ..layout.Layout import Layout
from ..layout.Blocks import Blocks
from ..shape.Shape import Shape, Fill, Stroke
from ..text.Line import Line
from ..table.Cell import Cell
from ..table.Row import Row
from ..table.TableBlock import TableBlock
from ..common.share import (BlockType, TextAlignment, lower_round, rgb_value, is_list_item)


class Column(Layout):
    '''Column of Section.'''

    def __init__(self, data:dict = None):
        super(Column, self).__init__(data)
        self.settings = {}

    @property
    def working_bbox(self): return self.bbox

    def parse(self, **settings):
        self.settings.update(**settings)
        return super(Column, self).parse(**settings)

    def add_elements(self, elements:Collection):
        '''Add candidate elements, i.e. lines or shapes, to current column.'''
        blocks = [e for e in elements if isinstance(e, Line)]
        shapes = [e for e in elements if isinstance(e, Shape)]
        self.assign_blocks(blocks)
        self.assign_shapes(shapes)


    def make_docx(self, doc):
        '''Create Section Column in docx.

        Args:
            doc (Document): ``python-docx`` document object
        '''
        blocks = Blocks(parent = self)
        blocks.extend(self.blocks)
        for shape in self.shapes:
            block = self.convert_to_block(shape)
            if block:
                blocks.append(block)
        blocks.sort_in_reading_order_plus()
        blocks.parse_spacing(self.settings['line_separate_threshold'],
            self.settings['line_break_width_ratio'],
            self.settings['line_break_free_space_ratio'],
            self.settings['lines_left_aligned_threshold'],
            self.settings['lines_right_aligned_threshold'],
            self.settings['lines_center_aligned_threshold'])

        blocks.make_docx(doc)

    def convert_to_block(self, shape: Shape):
        '''Convert a Shape to Block instance, e.g. TextBlock or ImageBlock.

        Args:
            shape (Shape): The source shape to convert.

        Returns:
            Block: A converted block instance.
        '''
        if isinstance(shape, Fill):
            if shape.color == rgb_value([1, 1, 1]):
                # ignore white fill shape
                return None
            shape = shape.to_stroke(self.bbox.width)

        if isinstance(shape, Stroke):
            table = TableBlock({
                'bbox': shape.bbox,
                'allignment': TextAlignment.LEFT,
                'line_space_type': 0,
            }, parent = self)
            row = Row()
            row.height = shape.bbox.height

            cell = Cell({
                'bbox': shape.bbox,
                'bg_color': shape.color,
            })
            row.append(cell)
            table.append(row)

            return table

        return None
