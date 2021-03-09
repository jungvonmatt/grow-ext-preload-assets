# grow-ext-preload-assets
Extension for the static-site generator Grow that enables asset preloading from within partials

## Concept
This extension comes in handy if you want add preload tags for critical assets.
See https://web.dev/preload-responsive-images/

## Usage
### Initial setup
1. Create an `extensions.txt` file within your pod.
1. Add to the file: `git+git://github.com/jungvonmatt/grow-ext-preload-assets`
1. Run `grow install`.
1. Add the following section to `podspec.yaml`:

```yaml
ext:
- extensions.inline_text_assets.PreloadAssetsExtension
```

This configuration a bundle to your documents that can be used in your templates with for example

```jinja2
{%- do doc.preload.addAsset({
  'src': 'wolf.jpg',
  'srcset': 'wolf_400px.jpg 400w, wolf_800px.jpg 800w, wolf_1600px.jpg 1600w'
  'sizes': '50vw'
}) -%}
{% endif %}
```

```jinja2
<head>
  {{ doc.preload.emit() }}
  ...
```

```html
<head>
  <link rel="preload" as="image" href="wolf.jpg" imagesrcset="wolf_400px.jpg 400w, wolf_800px.jpg 800w, wolf_1600px.jpg 1600w" imagesizes="50vw">
```