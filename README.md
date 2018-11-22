# asynciomeasures


This library allows you to send metrics to your Datadog or Statsd server.
This works on Python >= 3.5 and relies on asyncio and the async/await syntax.


### Installation

```sh
pip install asynciomeasures
```


### Example

```python
from asynciomeasures import Datadog

client = Datadog('udp://127.0.0.1:8125')
client.incr('foo')
client.decr('bar', tags={'one': 'two'})
with client.timer('baz'):
    ...
```


### Development

There's some great tests here.  To run them you'll need deps and the following.

```python
pip install -r test_requirements.txt
pytest -vv
```

All should pass.



### Notes

Thanks to everyone that contributed.  This is a fork of the origional aiomeasures
with updates for latest python versions.
