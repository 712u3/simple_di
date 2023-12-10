# simple_di
simple dependency injection

requires python3.12

```bash
pip install 'git+https://github.com/712u3/simple_di.git@master'
```

```py
# -----------------------------
# service1.py

from simple_di import component

@component
class Service1:
    def foo(self):
        print(123)

# -----------------------------
# service2.py

from simple_di import component
from services.service1 import Service1

@component
class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1

# -----------------------------
# main.py

from services.service2 import Service2
from simple_di import application_context

if __name__ == '__main__':
    application_context.initialize()
    service2 = application_context.get(Service2)
    service2.service1.foo()
```
