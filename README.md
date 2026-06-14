# [Blurp](https://discord.com/oauth2/authorize?client_id=1248292283883851919&permissions=2147608640&integration_type=0&scope=bot)

> Anime party-game Discord bot (Pycord). [Invite link](https://discord.com/oauth2/authorize?client_id=1248292283883851919&permissions=2147608640&integration_type=0&scope=bot)

<img src="./assets/Blurp.png" width=200>

## Commands

- General: `/anime` `/expression` `/action` `/art`
- Minigames: `/cycle` `/clues` `/whatnum`

## Develop

```bash
uv sync
# put secrets in .env.development:
#   DISCORD_BOT_TOKEN, MAL_CLIENT_ID, MAL_CLIENT_SECRET, GOOGLE_API_KEY, NAXOCIST_GUILD_ID
make run-dev      # ENV=dev uv run main.py
uv run pytest     # run tests
```

Layout: `main.py` is the entrypoint; everything else lives in `blurp/`
(`config`, `bot`, `cogs/`, `games/`, `services/`, `ui/`). Add a cog file under
`blurp/cogs/` and it loads automatically.

## Deploy (GHCR)

Image: **`ghcr.io/naxocist/blurp:latest`** (stable URL, always the newest build).

Build and push:

```bash
echo $GHCR_PAT | docker login ghcr.io -u naxocist --password-stdin
docker build -t ghcr.io/naxocist/blurp:latest .
docker push ghcr.io/naxocist/blurp:latest
```

Pull and run (secrets are pulled from Doppler at runtime):

```bash
docker pull ghcr.io/naxocist/blurp:latest
docker run -e DOPPLER_TOKEN=<token> ghcr.io/naxocist/blurp:latest
```
