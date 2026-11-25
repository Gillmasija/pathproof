"""Extract static references without executing markup."""
from dataclasses import dataclass, field
from html.parser import HTMLParser


@dataclass(frozen=True)
class Reference:
    value: str
    line: int
    attribute: str


@dataclass
class Document:
    references: list[Reference] = field(default_factory=list)
    ids: set[str] = field(default_factory=set)
    duplicate_ids: list[tuple[str, int]] = field(default_factory=list)
    has_base: bool = False


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.document = Document()
        self.element_ids = set()

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        for key, value in attrs:
            if value is None:
                continue
            if key == "id" or (tag == "a" and key == "name"):
                if key == "id":
                    if value in self.element_ids:
                        self.document.duplicate_ids.append((value, line))
                    self.element_ids.add(value)
                self.document.ids.add(value)
            if tag == "base" and key == "href":
                self.document.has_base = True
            elif key in {"href", "src"}:
                self.document.references.append(Reference(value, line, key))
            if len(self.document.references) + len(self.document.ids) + len(self.document.duplicate_ids) > 20_000:
                raise ValueError("HTML exceeds 20000 extracted entries")

    handle_startendtag = handle_starttag


def parse_html(text):
    parser = SiteParser()
    parser.feed(text)
    parser.close()
    return parser.document
