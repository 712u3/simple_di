from typing import Type
import inspect
from graphlib import TopologicalSorter


class ApplicationContext:
    def __init__(self) -> None:
        self._components: dict[Type, list[Type]] = {}
        self._built: bool = False
        self._instances: dict[Type, Type] = {}  # TODO: component_type: component_instance

    def register(self, cls: Type) -> None:
        if self._components.get(cls, None) is not None:
            raise RuntimeError(f'class: {cls} already registered')

        dependencies = self._get_init_params(cls)
        self._components[cls] = dependencies

    def initialize(self) -> None:
        if self._built:
            raise RuntimeError('ApplicationContext already initialized')

        sorter = TopologicalSorter(self._components)
        sorter.prepare()
        while sorter.is_active():
            for node in sorter.get_ready():
                node_params_types = self._get_init_params(node)
                node_params = [self._instances[param] for param in node_params_types]
                self._instances[node] = node(*node_params)

                sorter.done(node)

        self._built = True

    def _get_init_params(self, cls: Type) -> list[Type]:
        if self._components.get(cls, None) is not None:
            return self._components[cls]

        if cls.__init__ == object.__init__:
            return []

        result = []

        init_params = inspect.signature(cls.__init__).parameters
        init_params_iter = iter(init_params.values())
        next(init_params_iter)  # skip self

        for item in init_params_iter:
            if item.annotation == inspect._empty:
                raise AttributeError(f'param: {item} in class: {cls} should has type')
            if self._components.get(item.annotation, None) is None:
                raise AttributeError(f'cant create class: {cls}, dependency {item.annotation} is not registered')
            result.append(item.annotation)

        return result

    def get[T](self, cls: T) -> Type[T]:
        if not self._built:
            raise RuntimeError('ApplicationContext is not initialized')
        return self._instances[cls]


application_context = ApplicationContext()


def component(cls):
    application_context.register(cls)
    return cls


@component
class A:
    def hi(self):
        print('hi')


@component
class C:
    def __init__(self):
        pass


@component
class B:
    def __init__(self, a: A):
        self.a = a


if __name__ == '__main__':
    application_context.initialize()
    a = application_context.get(A)
    a.hi()
