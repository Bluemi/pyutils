from typing import List, Dict, Any, Sequence, Callable, TypeVar


def main():
    table = Table(('A', 'b', 'c'))
    table.line(A=3.141, b='hello')
    table.line(A=202.71828182, b='world')
    table.line(A=2.1, c='blabla')
    table.line(A='long string', b='something')
    print(table)


class StringFormatter:
    def __init__(self, float_precision: int = 3):
        t = TypeVar('t')
        float_fmt_string = f'{{:<.{float_precision}f}}'
        self.formatters: Dict[t, Callable[[t], str]] = {
            float: float_fmt_string.format
        }

    def __call__(self, value):
        formatter = self.formatters.get(type(value))
        if formatter is not None:
            return formatter(value)
        return str(value)


class Table:
    def __init__(self, headers: Sequence[str], float_precision: int = 3, column_space: int = 2):
        self._headers: Sequence[str] = headers
        self._normed_headers: List[str] = [Table._norm_header(h) for h in headers]
        self._lines: List[Dict[str, Any]] = []
        self._column_space = column_space
        self._string_formatter = StringFormatter(float_precision=float_precision)

    def line(self, **kwargs):
        for key in kwargs:
            if key not in self._normed_headers:
                raise KeyError(f'Add value for header "{key}", but this header does not exist. '
                               f'Valid headers are: {', '.join(self._normed_headers)}')
        self._lines.append(kwargs)

    def __repr__(self):
        column_width = {nh: len(h) for nh, h in zip(self._normed_headers, self._headers)}
        sep = ' ' * self._column_space
        longest_float = {nh: 0 for nh in self._normed_headers}
        for line in self._lines:
            for header, value in line.items():
                str_value = self._string_formatter(value)
                column_width[header] = max(column_width[header], len(str_value))
                if isinstance(value, float):
                    longest_float[header] = max(longest_float[header], len(str_value))

        header_line = sep.join(h.ljust(column_width[nh]) for nh, h in zip(self._normed_headers, self._headers))
        lines = [header_line]

        for line in self._lines:
            str_line = []
            for header in self._normed_headers:
                col_width = column_width[header]
                if header in line:
                    value = line[header]

                    str_value = self._string_formatter(value)
                    if isinstance(value, float):
                        str_value = str_value.rjust(longest_float[header])
                    str_line.append(str_value.ljust(col_width))
                else:
                    str_line.append(' ' * col_width)
            lines.append(sep.join(str_line))
        return '\n'.join(lines)

    @staticmethod
    def _norm_header(header):
        return header.replace(' ', '_')


if __name__ == '__main__':
    main()
