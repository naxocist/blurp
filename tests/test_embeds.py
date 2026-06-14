from types import SimpleNamespace

from blurp.ui.embeds import make_anime_embed, make_timer_embed


def _fake_anime() -> SimpleNamespace:
    jpg = SimpleNamespace(image_url="http://img/x.png")
    images = SimpleNamespace(jpg=jpg)
    genres = [SimpleNamespace(name="Action"), SimpleNamespace(name="Comedy")]
    return SimpleNamespace(
        title="Cowboy Bebop",
        url="http://mal/1",
        images=images,
        genres=genres,
        season="spring",
        year=1998,
        episodes=26,
        score=8.75,
        rank=42,
    )


def test_make_anime_embed_fields():
    embed = make_anime_embed(_fake_anime())

    assert embed.title == "Cowboy Bebop"
    assert embed.url == "http://mal/1"

    field_names = {field.name for field in embed.fields}
    assert {"Genres", "Season", "Length", "Score", "Ranked"} <= field_names


def test_make_timer_embed():
    embed = make_timer_embed("Time left:", 30)
    assert "30 seconds" in embed.title
