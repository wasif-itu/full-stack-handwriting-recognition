# Handwriting Recognition UI

A mobile-friendly browser UI for the deployed Lambda handwriting recognition API.
Users can take a camera photo on their phone or upload an existing image. The
browser resizes large mobile photos and normalizes bright paper images to the
model's expected dark-background polarity before uploading them to `/predict`.

```bash
npm start
```

Open:

```text
http://127.0.0.1:8088/index.html
```

## Deploy on Vercel

From the repository root:

```bash
npm run build
vercel
```

Vercel uses the root `vercel.json`, runs the build command, and publishes the
generated `dist/` directory.

The API URL is set in `deployment/ui/index.html` as `apiBaseUrl`.
