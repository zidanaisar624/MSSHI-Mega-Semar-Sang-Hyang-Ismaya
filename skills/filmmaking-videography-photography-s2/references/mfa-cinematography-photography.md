# S1-S2 MFA Module 2: Cinematography (Videography) & Master Photography
*(Optical Physics, Exposure Science, Lighting Ratios, and Visual Composition)*

## 1. Exposure Science & Sensor Physics

### A. The Exposure Triangle & Reciprocity
Total luminous exposure $H$ reaching the sensor plane is governed by scene luminance $L$, lens T-stop/f-number $N$, and exposure time (shutter speed) $t$:
$$H = \frac{q \cdot L \cdot t}{N^2}$$
1. **Aperture ($N = f/D$)**:
   - Full-stop scale: $f/1.0, f/1.4, f/2.0, f/2.8, f/4.0, f/5.6, f/8.0, f/11, f/16, f/22$.
   - Each full stop halves the light area ($\div 2$) and multiplies Depth of Field.
2. **Shutter Speed & The 180-Degree Shutter Rule (Videography vs. Photography)**:
   - **In Videography / Cinema**: Motion cadence requires a $180^\circ$ rotary shutter equivalent:
     $$t = \frac{1}{2 \times \text{FPS}}$$
     - **24 fps (Cinema Narrative)**: $1/48\text{ s}$ (or $1/50\text{ s}$ in 50Hz PAL/Indonesia regions to prevent AC lighting flicker).
     - **25 fps (PAL Broadcast/YouTube)**: $1/50\text{ s}$.
     - **30 fps (Digital Standard)**: $1/60\text{ s}$.
     - **60 fps / 120 fps (Slow Motion B-Roll)**: $1/120\text{ s}$ or $1/240\text{ s}$.
     - *Creative Override*: $45^\circ - 90^\circ$ shutter ($1/200\text{ s} - 1/500\text{ s}$ at 24fps) creates staccato, hyper-visceral action (*Saving Private Ryan* effect); $270^\circ - 360^\circ$ shutter ($1/24\text{ s}$) creates dreamy step-printed motion blur (*Wong Kar-wai* effect).
   - **In Still Photography**:
     - Handheld sharpness rule: $t \le \frac{1}{\text{Effective Focal Length}}$ (e.g., at least $1/100\text{ s}$ for an 85mm lens).
     - Freeze fast action/sports: $1/1000\text{ s} - 1/4000\text{ s}$.
     - Long-exposure light trails / silky waterfalls: $1\text{ s} - 30\text{ s}$ on tripod with ND filter.
3. **ISO, Dual Native ISO & False Color IRE Mapping**:
   - Keep ISO at the camera's **Base Native ISO** (e.g., ISO 800 and ISO 3200/12800 on dual-native cinema sensors) to preserve maximum dynamic range (14+ stops) above the noise floor.
   - **False Color / IRE Exposure Targets (Rec.709 / Monitoring LUT)**:
     - **0 - 5 IRE (Purple/Blue)**: Crushed black clipping (avoid unless silhouette).
     - **18% Middle Gray**: **38 - 42 IRE (Green)**.
     - **Skin Tones (Key Light Side)**: **55 - 70 IRE (Pink / Light Gray)**.
     - **95 - 100 IRE (Yellow/Red)**: Specular highlight clipping.

---

## 2. Optical Physics, Focal Lengths & Depth of Field

### A. Hyperfocal Distance & Depth of Field Formula
$$H = \frac{f^2}{N \cdot c} + f$$
where $f$ is focal length, $N$ is f-number, and $c$ is the circle of confusion (~$0.03\text{ mm}$ on Full-Frame $36 \times 24\text{ mm}$). When focused at $H$, everything from $H/2$ to infinity ($\infty$) is acceptably sharp.

### B. Psychological Dictionary of Focal Lengths (Full-Frame Equivalent)
| Focal Length | Field of View | Spatial & Psychological Effect | Classic Use Cases |
| :--- | :--- | :--- | :--- |
| **14mm - 20mm** | Ultra-Wide | Expands room scale, exaggerates Z-axis motion speed, distorts facial features at close distance. | Architecture, vast landscapes, psychological disorientation (Emmanuel Lubezki style). |
| **24mm - 28mm** | Wide | Dynamic environmental immersion; keeps background context legible while framing full-body action. | Establishing shots, walk-and-talk gimbal shots, vlogging, dynamic narrative scenes. |
| **35mm** | Master Wide-Normal | The quintessential cinema master lens: wide enough for environment, tight enough for natural faces. | Two-shots, over-the-shoulder (OTS), documentary storytelling, street photography. |
| **50mm** | Standard Normal | Matches human binocular perspective and compression; neutral, honest, unforced intimacy. | Dialogue medium shots, narrative realism (Yasujiro Ozu / anime clubroom framing). |
| **85mm - 105mm** | Portrait Telephoto | Flattering facial proportions, strong background compression, creamy bokeh subject isolation. | Emotional Close-Ups (CU), interviews, product hero shots, portrait photography. |
| **135mm - 200mm+** | Long Telephoto | Extreme Z-axis compression (background looms large behind subject), voyeuristic or epic isolation. | Cinematic compressed street shots, sports/wildlife, high-tension surveillance feel. |

---

## 3. Lighting Science, Inverse Square Law & Classic Setups

### A. The Inverse Square Law of Light Falloff
$$I \propto \frac{1}{d^2}$$
- Placing a softbox **close** to the subject (e.g., $1\text{ m}$ away) creates **rapid falloff** behind the subject (dramatic dark background contrast) and wraps softly around the face (because apparent source size is large).
- Placing a light **far** from the subject (e.g., $4\text{ m}$ away) creates **even illumination** across both the subject and the background (ideal for lighting a whole room evenly).

### B. Five Essential Cinematic Lighting Setups
1. **Three-Point Lighting (Key + Fill + Back/Hair Light)**:
   - **Key Light**: $30^\circ - 45^\circ$ off camera axis, $15^\circ - 30^\circ$ above eye level, diffused through a large softbox/scrim.
   - **Fill Light (or Negative Fill)**: Opposite the Key. Use a bounce card for **2:1** or **4:1** ratio, or a black flag (**Negative Fill**) for **8:1** cinematic shadow depth.
   - **Back / Rim / Kicker Light**: Behind the subject opposite the Key to carve the shoulders and hair out from the background.
2. **Rembrandt Lighting**: Key light positioned high and $45^\circ$ to the side so a small **illuminated triangle** appears on the shadow-side cheek beneath the eye.
3. **Book Lighting (Ultra-Soft Beauty / Mommy ASMR Visual Look)**: Bounce a strong light into a $4\times 4$ white bleached muslin/bounce board, then pass the bounced light through a $4\times 4$ diffusion frame ($1/2$ Grid or Opal). Produces velvety, zero-glare wrap ideal for calm, intimate close-ups.
4. **Chiaroscuro / Low-Key Lighting**: High contrast (**8:1 to 16:1** ratio), hard or snooted key light, deep shadows, smoke/haze for volumetric shafts.
5. **Color Contrast (Teal & Amber / Practical Motivated Lighting)**: Warm `2800K-3200K` practical tungsten lamp as the motivated Key/Rim against a `5600K-6500K` cool ambient room or window fill.
