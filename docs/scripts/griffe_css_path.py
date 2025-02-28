from typing import Any

from griffe import Extension, Class

class DefaultCSSFormatter(Extension):
    def on_class_members(self, *, cls: Class, **kwargs: Any) -> None:
        if (attr := cls.attributes.get("DEFAULT_CSS")) is not None:
            attr.value = attr.value.replace('\\n', '\n')[1:-1]
