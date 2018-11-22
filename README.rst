AIO Measures
============

This library allows you to send metrics to your Datadog or Statsd server.
This works on Python >= 3.5 and relies on asyncio.


Installation::

    python -m pip install asynciomeasures


Usage::

    from asynciomeasures import Datadog

    client = Datadog('udp://127.0.0.1:6789')
    client.incr('foo')
    client.decr('bar', tags={'one': 'two'})
    with client.timer('baz'):
        # long process
        pass


The client will send metrics to agent as possible.

Thanks to everyone that contributed.  Re uploaded as pypi with fixes as asynciomeasures.

```sh
pip install asynciomeasures
```

