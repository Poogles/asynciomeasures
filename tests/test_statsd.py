import asynciomeasures
import asyncio
import pytest
from datetime import timedelta

simple = [
    (asynciomeasures.CountingMetric('foo', 1), 'foo:1|c'),
    (asynciomeasures.CountingMetric('foo', -1), 'foo:-1|c'),
    (asynciomeasures.GaugeMetric('foo', 1), 'foo:1|g'),
    (asynciomeasures.GaugeMetric('foo', -1), 'foo:-1|g'),
    (asynciomeasures.HistogramMetric('foo', 42), 'foo:42|h'),
    (asynciomeasures.HistogramMetric('foo', -42), 'foo:-42|h'),
    (asynciomeasures.SetMetric('foo', 'bar'), 'foo:bar|s'),
    (asynciomeasures.TimingMetric('foo', 100), 'foo:100|ms'),
]

one_second = timedelta(seconds=1)
twenty_ms = timedelta(microseconds=20000)

rated = [
    (asynciomeasures.CountingMetric('foo', 1, 0.1), 'foo:1|c|@0.1'),
    (asynciomeasures.GaugeMetric('foo', 1, 0.1), 'foo:1|g|@0.1'),
    (asynciomeasures.SetMetric('foo', 'bar', 0.1), 'foo:bar|s|@0.1'),
    (asynciomeasures.TimingMetric('foo', 100, 0.1), 'foo:100|ms|@0.1'),
    (asynciomeasures.HistogramMetric('foo', -42, 0.1), 'foo:-42|h|@0.1'),

    (asynciomeasures.CountingMetric('foo', 1, one_second), 'foo:1|c|@1'),
    (asynciomeasures.GaugeMetric('foo', 1, one_second), 'foo:1|g|@1'),
    (asynciomeasures.SetMetric('foo', 'bar', one_second), 'foo:bar|s|@1'),
    (asynciomeasures.TimingMetric('foo', 100, one_second), 'foo:100|ms|@1'),
    (asynciomeasures.HistogramMetric('foo', -42, one_second), 'foo:-42|h|@1'),

    (asynciomeasures.CountingMetric('foo', 1, twenty_ms), 'foo:1|c|@0.02'),
    (asynciomeasures.GaugeMetric('foo', 1, twenty_ms), 'foo:1|g|@0.02'),
    (asynciomeasures.SetMetric('foo', 'bar', twenty_ms), 'foo:bar|s|@0.02'),
    (asynciomeasures.TimingMetric('foo', 100, twenty_ms), 'foo:100|ms|@0.02'),
    (asynciomeasures.HistogramMetric('foo', -42, twenty_ms), 'foo:-42|h|@0.02'),
]

tagged = [
    (asynciomeasures.CountingMetric('foo', 1,
                                tags={'bar': 'baz'}), 'foo:1|c|#bar:baz'),
    (asynciomeasures.CountingMetric('foo', -1,
                                tags={'bar': 'baz'}), 'foo:-1|c|#bar:baz'),
    (asynciomeasures.GaugeMetric('foo', 1, tags={
     'bar': 'baz'}), 'foo:1|g|#bar:baz'),
    (asynciomeasures.GaugeMetric('foo', -1,
                             tags={'bar': 'baz'}), 'foo:-1|g|#bar:baz'),
    (asynciomeasures.SetMetric('foo', 'bar', tags={
     'bar': 'baz'}), 'foo:bar|s|#bar:baz'),
    (asynciomeasures.TimingMetric('foo', 100, tags={
     'bar': 'baz'}), 'foo:100|ms|#bar:baz'),
]

whole = simple + rated + tagged


@pytest.mark.parametrize('metric,expected', whole)
def test_formatting(metric, expected):
    handler = asynciomeasures.StatsD(':0')
    assert handler.format(metric) == expected


tags = [
    ({}, {}, ''),
    ({'bar': 'baz'}, {}, '|#bar:baz'),
    ({}, {'bar': 'baz'}, '|#bar:baz'),
    ({'bar': 'baz'}, {'bar': 'qux'}, '|#bar:baz,bar:qux'),
]


@pytest.mark.parametrize('tags,defaults,expected', tags)
def test_tags(tags, defaults, expected):
    metric = asynciomeasures.CountingMetric('foo', 1, tags=tags)
    handler = asynciomeasures.StatsD(':0', tags=defaults)
    assert handler.format(metric) == 'foo:1|c%s' % expected


def test_events():
    event = asynciomeasures.Event('Man down!', 'This server needs assistance.')
    handler = asynciomeasures.StatsD(':0')
    assert handler.format(
        event) == '_e{9,29}Man down!|This server needs assistance.'


checks = [
    (asynciomeasures.Check('srv', 'OK'), '_sc|srv|0'),
    (asynciomeasures.Check('srv', 'warning'), '_sc|srv|1'),
    (asynciomeasures.Check('srv', 'crit'), '_sc|srv|2'),
    (asynciomeasures.Check('srv', 'UNKNOWN'), '_sc|srv|3'),
    (asynciomeasures.Check('srv', 'OK', tags={
     'foo': 'bar'}, message='baz'), '_sc|srv|0|#foo:bar|m:baz'),
]


@pytest.mark.parametrize('check,expected', checks)
def test_checks(check, expected):
    handler = asynciomeasures.StatsD(':0')
    assert handler.format(check) == expected


@asyncio.coroutine
async def fake_server(event_loop, port=None):
    port = port or 0

    class Protocol:

        msg = []

        def connection_made(self, transport):
            self.transport = transport

        def datagram_received(self, data, addr):
            message = data.decode().strip()
            self.msg.extend(message.split())

        def connection_lost(self, *args):
            pass

    transport, protocol = await event_loop.create_datagram_endpoint(
        lambda: Protocol(),
        local_addr=('0.0.0.0', port)
    )
    if port == 0:
        _, port = transport.get_extra_info('sockname')
    return transport, protocol, port


@pytest.mark.asyncio
async def test_client_event(event_loop):
    transport, protocol, port = await fake_server(event_loop)
    client = asynciomeasures.StatsD('udp://127.0.0.1:%s' % port)
    await asyncio.sleep(.4)
    client.event('title', 'text')
    await asyncio.sleep(.1)
    assert '_e{5,4}title|text' in protocol.msg
    transport.close()
    client.close()


@pytest.mark.asyncio
async def test_client(event_loop):
    transport, protocol, port = await fake_server(event_loop)
    client = asynciomeasures.StatsD('udp://127.0.0.1:%s' % port)
    await asyncio.sleep(.4)
    client.incr('example.a')
    client.timing('example.b', 500)
    client.gauge('example.c', 1)
    client.set('example.d', 'bar')
    client.decr('example.e')
    client.counter('example.f', 42)
    client.histogram('example.g', 13)
    await asyncio.sleep(.1)
    assert 'example.a:1|c' in protocol.msg
    assert 'example.b:500|ms' in protocol.msg
    assert 'example.c:1|g' in protocol.msg
    assert 'example.d:bar|s' in protocol.msg
    assert 'example.e:-1|c' in protocol.msg
    assert 'example.f:42|c' in protocol.msg
    assert 'example.g:13|h' in protocol.msg
    transport.close()
    client.close()


@pytest.mark.asyncio
async def test_reliablility(event_loop):
    transport, protocol, port = await fake_server(event_loop)
    client = asynciomeasures.StatsD('udp://127.0.0.1:%s' % port)
    await asyncio.sleep(.4)
    client.incr('example.a')
    await asyncio.sleep(.1)
    assert 'example.a:1|c' in protocol.msg
    transport.close()

    client.incr('example.b')
    await asyncio.sleep(.1)
    assert 'example.b:1|c' not in protocol.msg

    transport, protocol, port = await fake_server(event_loop, port)
    client.incr('example.c')
    await asyncio.sleep(.1)
    assert 'example.c:1|c' in protocol.msg
    transport.close()

    client.close()
