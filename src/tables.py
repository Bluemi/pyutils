import enum
from typing import List, Dict, Any, Sequence, Callable, Tuple


def main():
    table = Table(('A', 'b', 'c'), header_effect=Effect.blue)
    table.line(A=Effect.green(3.141), b=Effect.yellow('hello'))
    table.line(A=Effect.cyan(202.71828182), b=Effect.red('world'))
    table.line(A=Effect.bold(Effect.magenta(2.1)), c=Effect.underline('blabla'))
    table.line(A='long string', b='something')
    print(table)


class Color(enum.Enum):
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


class Effect:
    def __init__(self, color: Color, value):
        self.color = color
        self.value = value

    @staticmethod
    def red(value: Any):
        return Effect(Color.RED, value)

    @staticmethod
    def green(value: Any):
        return Effect(Color.GREEN, value)

    @staticmethod
    def blue(value: Any):
        return Effect(Color.BLUE, value)

    @staticmethod
    def magenta(value: Any):
        return Effect(Color.MAGENTA, value)

    @staticmethod
    def cyan(value: Any):
        return Effect(Color.CYAN, value)

    @staticmethod
    def yellow(value: Any):
        return Effect(Color.YELLOW, value)

    @staticmethod
    def bold(value: Any):
        return Effect(Color.BOLD, value)

    @staticmethod
    def underline(value: Any):
        return Effect(Color.UNDERLINE, value)
    

class Table:
    def __init__(
            self, headers: Sequence[Any], float_precision: int = 3, column_space: int = 2,
            header_effect: Callable[[Any], Effect] | None = None
    ):
        if header_effect is not None:
            headers = [header_effect(h) for h in headers]
        self._string_formatter = StringFormatter(float_precision=float_precision)
        self._headers: Sequence[Tuple[str, int]] = [self._string_formatter(h, 0) for h in headers]
        self._normed_headers: List[str] = [self._norm_header(h) for h in headers]
        self._lines: List[Dict[str, Any]] = []
        self._column_space = column_space

    def line(self, **kwargs):
        for key in kwargs:
            if key not in self._normed_headers:
                raise KeyError(f'Add value for header "{key}", but this header does not exist. '
                               f'Valid headers are: {', '.join(self._normed_headers)}')
        self._lines.append(kwargs)

    def __repr__(self):
        column_width = {nh: h[1] for nh, h in zip(self._normed_headers, self._headers)}
        sep = ' ' * self._column_space
        longest_float = {nh: 0 for nh in self._normed_headers}
        for line in self._lines:
            for header, value in line.items():
                str_len = self._string_formatter(value, 0)[1]
                column_width[header] = max(column_width[header], str_len)
                if isinstance(value, float):
                    longest_float[header] = max(longest_float[header], str_len)

        header_line = sep.join(
            Table.ljust(h, l, column_width[nh]) for nh, (h, l) in zip(self._normed_headers, self._headers)
        )
        lines = [header_line]

        for line in self._lines:
            str_line = []
            for header in self._normed_headers:
                col_width = column_width[header]
                if header in line:
                    value = line[header]
                    str_value, str_len = self._string_formatter(value, longest_float[header])
                    str_line.append(Table.ljust(str_value, str_len, col_width))
                else:
                    str_line.append(' ' * col_width)
            lines.append(sep.join(str_line))
        return '\n'.join(lines)

    def _norm_header(self, header):
        header, _header_len = self._string_formatter(header, 0, ignore_effects=True)
        return header.replace(' ', '_')

    @staticmethod
    def ljust(value: str, current_length: int, length: int):
        return value + ' ' * (length - current_length)


class StringFormatter:
    def __init__(self, float_precision: int = 3):
        self._float_fmt_string = f'{{:<.{float_precision}f}}'
        self.formatters: Dict[Any, Callable[[Any, int, bool], Tuple[str, int]]] = {
            float: self._format_float,
            Effect: self._format_effect
        }

    def __call__(self, value, longest_float_hint: int, ignore_effects=False):
        formatter = self.formatters.get(type(value))
        if formatter is not None:
            return formatter(value, longest_float_hint, ignore_effects)
        str_value = str(value)
        return str_value, len(str_value)

    def _format_float(self, value: float, longest_float_hint: int, _ignore_effects: bool):
        str_value = self._float_fmt_string.format(value).rjust(longest_float_hint)
        return str_value, len(str_value)

    def _format_effect(self, effect: Effect, longest_float_hint, ignore_effects: bool):
        str_content, len_content = self(effect.value, longest_float_hint)
        if ignore_effects:
            return str_content, len_content
        return effect.color.value + str_content + Color.ENDC.value, len_content


if __name__ == '__main__':
    main()
