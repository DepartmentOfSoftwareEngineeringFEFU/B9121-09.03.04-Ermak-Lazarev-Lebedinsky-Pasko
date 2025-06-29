"""
ids.py — генератор уникальных идентификаторов.

Определяет базовый класс IDNumerator и метакласс _IDMeta, обеспечивающие
автоматическое назначение ID объектам модели (узлы, балки, силы и т.д.)
с отслеживанием уже использованных значений.

Применяется в structures.py.
"""

from abc import ABCMeta, ABC


class _IDMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        dct['_next_id'] = 1
        dct['_used_ids'] = set()
        return super().__new__(cls, name, bases, dct)


class IDNumerator(ABC, metaclass=_IDMeta):
    def __init__(self, custom_id: int | None = None):
        cls = self.__class__
        if custom_id is not None:
            if custom_id in cls._used_ids:
                raise ValueError(f"ID {custom_id} уже занят в {cls.__name__}")
            self._id = int(custom_id)
        else:
            while cls._next_id in cls._used_ids:
                cls._next_id += 1
            self._id = int(cls._next_id)
            cls._next_id += 1
        cls._used_ids.add(self._id)

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, new_id: int):
        cls = self.__class__
        new_id = int(new_id)
        if new_id == self._id:
            return  # ничего не меняем
        if new_id in cls._used_ids:
            raise ValueError(f"ID {new_id} уже занят в {cls.__name__}")
        # Снимаем старый ID
        if self._id in cls._used_ids:
            cls._used_ids.remove(self._id)
        # Присваиваем новый
        self._id = new_id
        cls._used_ids.add(self._id)


# Пример использования
# class TestClass(IDNumerator):
#     def __init__(self, custom_id: int | None = None):
#         super().__init__(custom_id)


# class AnotherClass(IDNumerator):
#     def __init__(self, custom_id: int | None = None):
#         super().__init__(custom_id)

# if __name__ == "__main__":
#     obj1 = TestClass()
#     obj2 = AnotherClass()
#     obj3 = TestClass()
#     obj4 = TestClass(0)
#     obj5 = TestClass(10)
#     obj5.id = 9

#     print(f"ID объекта 1 (TestClass): {obj1.id}")
#     print(f"ID объекта 2 (AnotherClass): {obj2.id}")
#     print(f"ID объекта 3 (TestClass): {obj3.id}")
#     print(f"ID объекта 4 (TestClass): {obj4.id}")
#     print(f"ID объекта 5 (TestClass): {obj5.id}")