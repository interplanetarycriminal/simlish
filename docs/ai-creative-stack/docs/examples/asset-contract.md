# Example asset contract

This proposal illustrates a handoff for an interactive product model.

| Field | Value |
| --- | --- |
| Producer | Artist using Blender |
| Consumer | Three.js scene using GLTFLoader |
| Editable source | assets/source/product.blend |
| Delivery artifact | assets/web/product.glb |
| Geometry | Meters, named root, target triangle budget recorded in brief |
| Materials | Embedded textures with compression accepted by consumer |
| Validation | Load a sample in the web build and inspect scale, lighting, materials and animation clip names |
| Fallback | Static WebP with descriptive alternative text |
| Provenance | Author, approved license, source revision and export command or settings in release manifest |

This is file interchange. Embed textures where possible and gate additional decoders on performance and browser coverage.
