import { useEffect, useRef } from 'react';

/**
 * Injects an inline SVG overlay so we can animate specific elements by id/class.
 * Expected element selectors in the SVG (optional, animate if present):
 *  - #moon
 *  - #billboard
 *  - #drone
 *  - .car (multiple)
 *  - .bridge-cable (multiple vertical lines)
 */
export default function LineOverlay(): JSX.Element {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    const inject = (svg: string) => {
      if (!cancelled && containerRef.current && svg) {
        containerRef.current.innerHTML = svg;
        containerRef.current.classList.add('line-overlay');

        // Heuristic auto-tagging to enable targeted animations
        try {
          const svgEl = containerRef.current.querySelector('svg');
          if (!svgEl) return;
          const vb = (svgEl as SVGSVGElement).viewBox.baseVal;
          const W =
            vb && vb.width
              ? vb.width
              : svgEl.getBoundingClientRect().width || 4000;
          const H =
            vb && vb.height
              ? vb.height
              : svgEl.getBoundingClientRect().height || 2300;

          const nodes = Array.from(
            svgEl.querySelectorAll<SVGGraphicsElement>(
              'path, line, polyline, polygon, ellipse, circle, rect, g'
            )
          );

          const entries = nodes
            .map(el => {
              let bbox: DOMRect | null = null;
              try {
                bbox = el.getBBox();
              } catch {
                /* some elements may be non-rendered */
              }
              return { el, bbox } as {
                el: SVGGraphicsElement;
                bbox: DOMRect | null;
              };
            })
            .filter(
              e => e.bbox && isFinite(e.bbox!.width) && isFinite(e.bbox!.height)
            );

          // Helpers
          const inBox = (
            b: DOMRect,
            x0: number,
            y0: number,
            x1: number,
            y1: number
          ) => {
            return (
              b.x >= x0 &&
              b.y >= y0 &&
              b.x + b.width <= x1 &&
              b.y + b.height <= y1
            );
          };

          // Detect moon: large near-circular in upper mid-left
          let moonCand = null as {
            el: SVGGraphicsElement;
            bbox: DOMRect;
          } | null;
          for (const e of entries) {
            const b = e.bbox!;
            const aspect = b.width > 0 ? b.height / b.width : 0;
            const area = b.width * b.height;
            if (
              area > W * H * 0.002 &&
              area < W * H * 0.05 &&
              aspect > 0.8 &&
              aspect < 1.25
            ) {
              if (inBox(b, W * 0.25, H * 0.1, W * 0.65, H * 0.55)) {
                if (
                  !moonCand ||
                  area > moonCand.bbox.width * moonCand.bbox.height
                ) {
                  moonCand = { el: e.el, bbox: b };
                }
              }
            }
          }
          if (moonCand) {
            moonCand.el.id = 'moon';
          }

          // Drone: small object near the moon
          if (moonCand) {
            const mx = moonCand.bbox.x + moonCand.bbox.width / 2;
            const my = moonCand.bbox.y + moonCand.bbox.height / 2;
            const radius =
              Math.max(moonCand.bbox.width, moonCand.bbox.height) * 0.8;
            const near = entries
              .filter(e => {
                const b = e.bbox!;
                const cx = b.x + b.width / 2;
                const cy = b.y + b.height / 2;
                const dist = Math.hypot(cx - mx, cy - my);
                const area = b.width * b.height;
                return (
                  area > 50 &&
                  area < 15000 &&
                  dist < radius * 1.6 &&
                  b.width < moonCand!.bbox.width * 0.6
                );
              })
              .sort(
                (a, b) =>
                  a.bbox!.width * a.bbox!.height -
                  b.bbox!.width * b.bbox!.height
              );
            if (near[0]) {
              near[0].el.classList.add('drone');
            }
          }

          // Billboard: large rectangle-ish in upper-right
          const billboard = entries.find(e => {
            const b = e.bbox!;
            const area = b.width * b.height;
            const aspect = b.width > 0 ? b.width / b.height : 0;
            return (
              inBox(b, W * 0.55, 0, W, H * 0.55) &&
              area > W * H * 0.01 &&
              aspect > 1.3
            );
          });
          if (billboard) billboard.el.id = 'billboard';

          // Cars: small-ish groups in lower-left quadrant
          entries.forEach(e => {
            const b = e.bbox!;
            const area = b.width * b.height;
            if (
              b.y > H * 0.7 &&
              b.x < W * 0.45 &&
              area > 200 &&
              area < W * H * 0.0025 &&
              b.width > 8 &&
              b.height > 6
            ) {
              e.el.classList.add('car');
            }
          });

          // Bridge cables: thin, tall lines on left third
          entries.forEach(e => {
            const b = e.bbox!;
            const tall = b.height > b.width * 6;
            if (
              tall &&
              b.x < W * 0.35 &&
              b.height > H * 0.15 &&
              b.width < W * 0.02
            ) {
              e.el.classList.add('bridge-cable');
            }
          });
        } catch (err) {
          console.warn('LineOverlay tagging failed', err);
        }
      }
    };

    // Load from public/overlays at runtime (works both dev and prod)
    fetch(`/overlays/lines.svg?_=${Date.now()}`)
      .then(r => (r.ok ? r.text() : ''))
      .then(svg => {
        if (!svg) {
          console.warn(
            'LineOverlay: /overlays/lines.svg not found or empty. Place your SVG under frontend/public/overlays/lines.svg'
          );
        }
        inject(svg);
      })
      .catch(e => console.warn('LineOverlay: failed to load overlay', e));

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="pointer-events-none absolute inset-0 mix-blend-screen opacity-85"
      aria-hidden
    />
  );
}
