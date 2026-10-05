# Animated poster-only delivery

The scheduled delivery path uses only the V2 services and animated GIFs:

```text
kovan-v2-poster-schedule.timer
  -> kovan-v2-poster-schedule.service
  -> kovan-v2-poster-api.service:8001
  -> render_gif()
  -> generated-posters/<year>/<event>/<id>-<date>.gif
  -> Teams hosted GIF URL
```

Install or repair the services with:

```bash
./scripts/install_poster_systemd_timer.sh
```

The installer disables the legacy `kovan-poster-*` static-poster units. The
manual sender also accepts only `.gif` paths and sends a signed GIF URL.

Before delivery, the API treats an existing `.webp`, `.png`, or `.mp4` run as
stale and regenerates it as a GIF. A stored run is considered valid only when
its poster path ends in `.gif` and that object exists in Supabase Storage.
