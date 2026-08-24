from core.infra.linux.source_factory import (
    LinuxSourceFactory,
)


def test_factory_creates_sources():
    factory = LinuxSourceFactory()

    sources = factory.create_sources()

    assert len(sources) == 10


def test_factory_creates_unique_source_ids():
    factory = LinuxSourceFactory()

    sources = factory.create_sources()

    source_ids = [
        source.source_id.value
        for source in sources
    ]

    assert len(source_ids) == len(
        set(source_ids)
    )