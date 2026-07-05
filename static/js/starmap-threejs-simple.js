// Three.js Starmap Implementation - Clean Version
import * as THREE from 'three';

class ThreeJSStarmap {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.starField = null;
        this.currentStars = [];
        this.animationId = null;
        this.keys = {};
        this.fictionalExoplanets = [];
        this.realExoplanets = [];
        this.nations = [];
        this.nationFilter = null;      // Set of star IDs for nation filter (nation 1)
        this.nationFilter2 = null;     // Set of star IDs for nation 2 (compare mode)
        this.nationFilterId = null;    // nation id behind nationFilter (for era ownership checks)
        this.nationFilterId2 = null;
        this.eraYear = null;           // Current era year (null = no era filter)
        this.ownershipByStar = null;   // Map star_id → [{nation_id, era_start, era_end}] (era territory)
        this.politicalView = false;
        this.flyAnimation = null;
        this.points = null;
        this.clock = new THREE.Clock();
        this.constellationsGroup = null;
        this.habitableZoneGroup = null;

        if (typeof THREE === 'undefined') {
            console.error('❌ Three.js not loaded');
            return;
        }

        this.init();
    }

    async init() {
        console.log('🚀 Initializing Three.js starmap...');

        this.container = document.getElementById('threejs-container');
        if (!this.container) {
            console.error('❌ Three.js container not found');
            return false;
        }

        try {
            this.setupScene();
            this.setupCamera();
            this.setupRenderer();
            await this.setupControls();
            this.setupLighting();

            this.loadStars().then(() => {
                console.log('✅ Stars loaded');
            });

            this.animate();
            console.log('✅ Three.js starmap initialized successfully');
            return true;

        } catch (error) {
            console.error('❌ Error initializing Three.js starmap:', error);
            return false;
        }
    }

    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000011);
        this.starField = new THREE.Group();
        this.scene.add(this.starField);

        // Initialize overlay groups
        this.nationsGroup = new THREE.Group();
        this.tradeRoutesGroup = new THREE.Group();
        this.stellarRegionsGroup = new THREE.Group();
        this.exoplanetGroup = new THREE.Group();
        this.scene.add(this.nationsGroup);
        this.scene.add(this.tradeRoutesGroup);
        this.scene.add(this.stellarRegionsGroup);
        this.scene.add(this.exoplanetGroup);

        this.constellationsGroup = new THREE.Group();
        this.scene.add(this.constellationsGroup);

        this.habitableZoneGroup = new THREE.Group();
        this.scene.add(this.habitableZoneGroup);

        // Name labels for notable systems (discovery systems + fictional stars)
        this.labelsGroup = new THREE.Group();
        this.scene.add(this.labelsGroup);

        // Create galactic axes and star interaction
        this.createGalacticAxes();
        this.setupStarInteraction();

    }

    setupCamera() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 10000);
        this.camera.position.set(0, 0, 10);
    }

    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.domElement.style.position = 'absolute';
        this.renderer.domElement.style.top = '0';
        this.renderer.domElement.style.left = '0';

        while (this.container.firstChild) {
            this.container.removeChild(this.container.firstChild);
        }
        this.container.appendChild(this.renderer.domElement);
    }

    async setupControls() {
        try {
            const { OrbitControls } = await import('three/examples/jsm/controls/OrbitControls');
            this.controls = new OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.1;
            this.controls.enablePan = true;
            this.controls.enableZoom = true;
            this.controls.enableRotate = true;
            this.controls.minDistance = 0.1;
            this.controls.maxDistance = 1000;
            this.controls.target.set(0, 0, 0);
        } catch (error) {
            console.warn('⚠️ OrbitControls not available, using fallback:', error);
            this.controls = {
                update: () => {},
                target: new THREE.Vector3(0, 0, 0),
                enableDamping: true,
                dampingFactor: 0.1
            };
        }
    }

    setupLighting() {
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
    }

    async loadStars() {
        try {
            console.log('🌟 Loading stars...');

            const [starsResponse, fictionalResponse] = await Promise.all([
                fetch('/api/v1/stars?limit=50000&mag_limit=15'),
                fetch('/api/v1/fictional-stars')
            ]);

            const starsData = await starsResponse.json();
            const fictionalData = await fictionalResponse.json();

            let allStars = [];
            if (starsData.success && starsData.data) {
                allStars = [...starsData.data];
                console.log(`✅ Loaded ${starsData.data.length} astronomical stars`);
            }

            if (fictionalData.success && fictionalData.data) {
                const fictionalStars = this.processFictionalStars(fictionalData.data);
                allStars = [...allStars, ...fictionalStars];
                console.log(`✅ Loaded ${fictionalStars.length} fictional stars`);
            }

            if (allStars.length > 0) {
                console.log(`✅ Total stars loaded: ${allStars.length}`);
                this.createStars(allStars);
                this.createStarLabels();
            } else {
                console.error('❌ No stars loaded from any source');
            }
        } catch (error) {
            console.error('❌ Error loading stars:', error);
        }
    }

    processFictionalStars(fictionalRawData) {
        console.log('🎭 Processing fictional stars...', fictionalRawData.length);

        return fictionalRawData.map((star, index) => {
            const starName = star.fictional_name || star.proper || star.name || this.generateStarNameFromCatalog(star);
            return {
                id: star.id || 999990 + index,
                name: starName,
                fictional_name: star.fictional_name || starName,
                fictional_description: star.fictional_description || '',
                x: parseFloat(star.x) || 0,
                y: parseFloat(star.y) || 0,
                z: parseFloat(star.z) || 0,
                magnitude: parseFloat(star.magnitude || star.mag) || 8.0,
                spectral_class: star.spectral_class || star.spect || 'G2V',
                constellation: star.con || star.constellation,
                distance: parseFloat(star.distance || star.dist) || 10.0,
                catalog_ids: this.buildCatalogIds(star),
                nation_id: star.nation_id || '',
                era_start: star.era_start || null,
                era_end: star.era_end || null,
                is_fictional: true,
            };
        });
    }

    generateStarNameFromCatalog(star) {
        const catalogs = [
            star.hd && `HD ${star.hd}`,
            star.hip && `HIP ${star.hip}`,
            star.gl && `Gliese ${star.gl}`,
            star.bayer && star.bayer,
            star.flam && `${star.flam} ${star.con || ''}`
        ].filter(Boolean);
        return catalogs[0] || `Star ${star.id || Math.floor(Math.random() * 100000)}`;
    }

    buildCatalogIds(star) {
        const catalogIds = [];
        if (star.hip) catalogIds.push(`HIP ${star.hip}`);
        if (star.hd) catalogIds.push(`HD ${star.hd}`);
        if (star.bayer) catalogIds.push(star.bayer);
        return catalogIds;
    }


    // Spectral class → RGB color mapping (approximate black-body colours)
    static _spectralColor(spectralClass) {
        const key = (spectralClass || 'G')[0].toUpperCase();
        const map = {
            O: [0.60, 0.70, 1.00],
            B: [0.70, 0.85, 1.00],
            A: [0.95, 0.97, 1.00],
            F: [1.00, 1.00, 0.85],
            G: [1.00, 0.92, 0.60],
            K: [1.00, 0.75, 0.40],
            M: [1.00, 0.45, 0.25],
        };
        return map[key] || [1.0, 1.0, 1.0];
    }

    createStars(stars) {
        // Dispose previous geometry / material
        while (this.starField.children.length > 0) {
            const child = this.starField.children[0];
            this.starField.remove(child);
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
        }
        if (this.starMaterial) {
            this.starMaterial.dispose();
            this.starMaterial = null;
        }

        const validStars = stars.filter(star =>
            star.x != null && !isNaN(star.x) &&
            star.y != null && !isNaN(star.y) &&
            star.z != null && !isNaN(star.z)
        );

        this.currentStars = validStars;

        const positions    = new Float32Array(validStars.length * 3);
        const magnitudes   = new Float32Array(validStars.length);
        const colors       = new Float32Array(validStars.length * 3);
        const filterValues = new Float32Array(validStars.length);
        const nationColors = new Float32Array(validStars.length * 3);
        filterValues.fill(1.0);

        validStars.forEach((star, i) => {
            positions[i * 3]     = star.x * 10;
            positions[i * 3 + 1] = star.y * 10;
            positions[i * 3 + 2] = star.z * 10;

            magnitudes[i] = (star.magnitude != null && !isNaN(star.magnitude))
                ? star.magnitude : 8.0;

            const [r, g, b] = ThreeJSStarmap._spectralColor(star.spectral_class);
            colors[i * 3]     = r;
            colors[i * 3 + 1] = g;
            colors[i * 3 + 2] = b;
            // Nation colors default to spectral colors; updated by setPoliticalView()
            nationColors[i * 3]     = r;
            nationColors[i * 3 + 1] = g;
            nationColors[i * 3 + 2] = b;
        });

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position',    new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('magnitude',   new THREE.Float32BufferAttribute(magnitudes, 1));
        geometry.setAttribute('starColor',   new THREE.Float32BufferAttribute(colors, 3));
        geometry.setAttribute('aFilter',     new THREE.Float32BufferAttribute(filterValues, 1));
        geometry.setAttribute('aNationColor',new THREE.Float32BufferAttribute(nationColors, 3));

        // ── GPU Shader (LOD + spectral colours, no texture uploads on filter) ──
        const vertexShader = `
            attribute float magnitude;
            attribute vec3  starColor;
            attribute float aFilter;
            attribute vec3  aNationColor;
            uniform float   uMagLimit;
            uniform float   uCameraDistance;
            uniform bool    uPoliticalView;
            varying vec3    vColor;
            varying float   vAlpha;
            varying float   vFilter;
            varying vec3    vNationColor;

            void main() {
                vColor       = starColor;
                vFilter      = aFilter;
                vNationColor = aNationColor;

                // Hide stars dimmer than the current magnitude limit
                float visible = step(magnitude, uMagLimit);

                // LOD: brighter stars are larger; point size scales with camera proximity
                float brightness = max(0.0, uMagLimit - magnitude);
                float sz = (2.0 + brightness * 3.0) * (50.0 / max(uCameraDistance, 1.0));
                sz = clamp(sz, 0.5, 14.0);

                gl_PointSize = sz * visible;
                gl_Position  = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                vAlpha = visible * (0.4 + brightness * 0.6);
            }
        `;

        const fragmentShader = `
            varying vec3  vColor;
            varying float vAlpha;
            varying float vFilter;
            varying vec3  vNationColor;
            uniform bool  uPoliticalView;

            void main() {
                vec2  coord = gl_PointCoord - 0.5;
                float dist  = length(coord);
                if (dist > 0.5) discard;
                float alpha = smoothstep(0.5, 0.0, dist) * vAlpha;
                if (alpha < 0.01) discard;
                vec3 finalColor = uPoliticalView ? vNationColor : vColor;
                gl_FragColor = vec4(finalColor, alpha * max(vFilter, 0.15));
            }
        `;

        const initialMag = parseFloat(document.getElementById('magLimit')?.value ?? '8');

        this.starMaterial = new THREE.ShaderMaterial({
            vertexShader,
            fragmentShader,
            uniforms: {
                uMagLimit:       { value: initialMag },
                uCameraDistance: { value: 10.0 },
                uPoliticalView:  { value: false },
            },
            transparent: true,
            depthWrite: false,
        });

        this.points = new THREE.Points(geometry, this.starMaterial);
        this.starField.add(this.points);
        console.log(`Created ${validStars.length} stars with GPU shader LOD`);
    }

    setupStarInteraction() {
        this.raycaster = new THREE.Raycaster();
        this.raycaster.params.Points.threshold = 0.5;
        this.raycaster.params.Line.threshold = 1.5;   // world units — makes thin route lines clickable
        this.mouse = new THREE.Vector2();
        this.intersects = [];
        this.highlightedStar = null;

        this.container.addEventListener('click', (event) => this.onMouseClick(event));
        this.container.addEventListener('mousemove', (event) => this.onMouseMove(event));
        this.container.addEventListener('mouseout', () => this.onMouseOut());

        // Respond to window resize
        window.addEventListener('resize', () => this.resize());

        // Wire magnitude slider → shader uniform (instant, no API call)
        const slider = document.getElementById('magLimit');
        const label  = document.getElementById('magValue');
        if (slider) {
            slider.addEventListener('input', () => {
                const val = parseFloat(slider.value);
                if (label) label.textContent = val.toFixed(1);
                if (this.starMaterial) {
                    this.starMaterial.uniforms.uMagLimit.value = val;
                }
            });
        }

        this.setupKeyboardNavigation();
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Ignore WASD when the user is typing in an input or textarea
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            this.keys[e.code] = true;
            // Prevent spacebar from scrolling the page
            if (e.code === 'Space') e.preventDefault();
        });
        document.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });
        // Clear all keys when the window loses focus to prevent stuck keys
        window.addEventListener('blur', () => {
            this.keys = {};
        });
    }

    processKeyboardInput() {
        if (!this.camera || !this.controls) return;

        // Speed scales with distance from target so it feels natural at any zoom level
        const dist  = this.camera.position.distanceTo(this.controls.target);
        const speed = dist * 0.02;

        const forward = new THREE.Vector3()
            .subVectors(this.controls.target, this.camera.position)
            .normalize();
        const worldUp = new THREE.Vector3(0, 1, 0);
        const right   = new THREE.Vector3().crossVectors(forward, worldUp).normalize();
        const up      = new THREE.Vector3().crossVectors(right, forward).normalize();

        let moved = false;

        if (this.keys['KeyW'] || this.keys['ArrowUp']) {
            this.camera.position.addScaledVector(forward, speed);
            this.controls.target.addScaledVector(forward, speed);
            moved = true;
        }
        if (this.keys['KeyS'] || this.keys['ArrowDown']) {
            this.camera.position.addScaledVector(forward, -speed);
            this.controls.target.addScaledVector(forward, -speed);
            moved = true;
        }
        if (this.keys['KeyA'] || this.keys['ArrowLeft']) {
            this.camera.position.addScaledVector(right, -speed);
            this.controls.target.addScaledVector(right, -speed);
            moved = true;
        }
        if (this.keys['KeyD'] || this.keys['ArrowRight']) {
            this.camera.position.addScaledVector(right, speed);
            this.controls.target.addScaledVector(right, speed);
            moved = true;
        }
        if (this.keys['KeyQ']) {
            this.camera.position.addScaledVector(up, speed);
            this.controls.target.addScaledVector(up, speed);
            moved = true;
        }
        if (this.keys['KeyE']) {
            this.camera.position.addScaledVector(up, -speed);
            this.controls.target.addScaledVector(up, -speed);
            moved = true;
        }
        // Spacebar = pan world Y+ (up), ShiftLeft = pan world Y- (down)
        if (this.keys['Space']) {
            this.camera.position.y += speed;
            this.controls.target.y  += speed;
            moved = true;
        }
        if (this.keys['ShiftLeft'] || this.keys['ShiftRight']) {
            this.camera.position.y -= speed;
            this.controls.target.y  -= speed;
            moved = true;
        }

        if (moved && this.controls.update) this.controls.update();
    }

    takeScreenshot() {
        // Force a render so the buffer is current, then export
        this.render();
        const dataURL = this.renderer.domElement.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = dataURL;
        a.download = `starmap-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    // ── Wiki / Top-down export ────────────────────────────────────────────────

    generateWikiView(titleText = null) {
        // Fly to top-down view, hide UI, render clean map, download PNG + wiki markup
        const camOffset = 800;
        const target    = (this.controls && this.controls.target)
            ? this.controls.target.clone()
            : new THREE.Vector3(0, 0, 0);

        // Snap camera directly above target (Y-up = galactic north)
        this.flyAnimation = {
            startPos:    this.camera.position.clone(),
            endPos:      new THREE.Vector3(target.x, target.y + camOffset, target.z),
            startTarget: this.controls.target.clone(),
            endTarget:   target.clone(),
            duration:    1200,
            startTime:   performance.now(),
        };

        // After fly animation completes, render & export
        setTimeout(() => {
            // Hide axes, turn on trade routes for the map
            if (this.axesHelper) this.axesHelper.visible = false;
            if (this.axisLabels) this.axisLabels.forEach(l => l.visible = false);

            this.render();

            const dataURL = this.renderer.domElement.toDataURL('image/png');
            const inUniverYear = this.eraYear || 2750;
            const title = titleText || 'Felgenland Starmap';
            const wikiMarkup = `{{:starmap:${title.toLowerCase().replace(/ /g,'_')}_${inUniverYear}.png|${title} — In-universe date: ${inUniverYear}}}

/* Exported by Starmap tool. Era: ${inUniverYear}. */
`;
            // Download PNG
            const a = document.createElement('a');
            a.href = dataURL;
            a.download = `wiki-starmap-${inUniverYear}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            // Copy wiki markup
            if (navigator.clipboard) {
                navigator.clipboard.writeText(wikiMarkup).then(() => {
                    console.log('✅ DokuWiki markup copied to clipboard');
                });
            }

            // Restore axes visibility
            const axesCheck = document.getElementById('galacticDirectionsOverlay');
            const showAxes  = axesCheck ? axesCheck.checked : false;
            if (this.axesHelper) this.axesHelper.visible = showAxes;
            if (this.axisLabels) this.axisLabels.forEach(l => l.visible = showAxes);

            // Notify user
            const banner = document.getElementById('wikiExportBanner');
            if (banner) {
                banner.textContent = `✅ Wiki map saved as "wiki-starmap-${inUniverYear}.png". DokuWiki markup copied to clipboard.`;
                banner.style.display = 'block';
                setTimeout(() => { banner.style.display = 'none'; }, 5000);
            }
        }, 1400);
    }

    onMouseClick(event) {

        const rect = this.container.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);

        if (this.starField && this.starField.children.length > 0) {
            this.intersects = this.raycaster.intersectObjects(this.starField.children, true);

            if (this.intersects.length > 0) {
                const intersect = this.intersects[0];
                const pointIndex = intersect.index;

                if (pointIndex >= 0 && pointIndex < this.currentStars.length) {
                    const clickedStar = this.currentStars[pointIndex];
                    // Ignore stars filtered out by the magnitude shader
                    const magLimit = this.starMaterial
                        ? this.starMaterial.uniforms.uMagLimit.value
                        : 15;
                    if (clickedStar.magnitude > magLimit) return;
                    console.log('⭐ Star clicked:', clickedStar);
                    this.displayStarDetails(clickedStar);
                    this.highlightStar(clickedStar);
                    return;
                }
            }
        }

        // No star hit — try trade route lines (only when the overlay is shown)
        if (this.tradeRoutesGroup?.visible && this.tradeRoutesGroup.children.length) {
            const hits = this.raycaster.intersectObjects(
                this.tradeRoutesGroup.children.filter(c => c.visible), false);
            if (hits.length > 0) {
                const route = hits[0].object.userData;
                if (route?.type === 'trade_route') this.displayRouteDetails(route);
            }
        }
    }

    /** Show a trade route's lore in the details panel. */
    displayRouteDetails({ data: route, fromStar, toStar }) {
        const detailsPanel = document.getElementById('starDetails');
        const detailsContent = document.getElementById('starDetailsContent');
        if (!detailsPanel || !detailsContent) return;

        const esc = (s) => { const d = document.createElement('div');
            d.appendChild(document.createTextNode(String(s ?? ''))); return d.innerHTML; };
        const nation = this.nations.find(n => (n._id || n.id) === route.nation_id);
        const color = nation ? ((nation.appearance && nation.appearance.color) || nation.color || '#888888') : '#888888';
        const safeColor = /^#[0-9A-Fa-f]{6}$/.test(color) ? color : '#888888';
        const starName = (s) => {
            if (!s) return 'Unknown';
            const colonized = (this.eraYear == null) || (s.discovery_year == null) || (this.eraYear >= s.discovery_year);
            return (colonized && s.fictional_name) || s.name || `Star ${s.id}`;
        };
        const dx = (fromStar && toStar)
            ? Math.hypot(fromStar.x - toStar.x, fromStar.y - toStar.y, fromStar.z - toStar.z)
            : null;

        const rows = [
            ['Type', route.route_type], ['Category', (route.category || '').replace(/_/g, ' ')],
            ['Frequency', route.frequency],
            ['Active', route.era_start != null ? `${route.era_start} – ${route.era_end ?? 'present'}` : null],
            ['Length', dx != null ? `${dx.toFixed(2)} pc (${(dx * 3.262).toFixed(1)} ly)` : null],
        ].filter(([, v]) => v);

        detailsContent.innerHTML = `
            <h6 class="mb-1" style="color:${safeColor}">🚢 ${esc(route.name || route.id || 'Trade Route')}</h6>
            <div class="small text-muted mb-2">
                ${esc(starName(fromStar))} ⟶ ${esc(starName(toStar))}
            </div>
            ${nation ? `
            <div class="mb-2 px-2 py-1 rounded d-flex align-items-center gap-2"
                 style="border-left:3px solid ${safeColor}; background:rgba(0,0,0,0.4)">
                <span style="width:8px;height:8px;border-radius:50%;background:${safeColor};display:inline-block;"></span>
                <span class="small fw-bold">${esc(nation.name)}</span>
            </div>` : ''}
            ${rows.map(([k, v]) => `
            <div class="d-flex justify-content-between py-1" style="border-bottom:1px solid rgba(255,255,255,0.06)">
                <small class="text-muted">${k}</small><small>${esc(v)}</small>
            </div>`).join('')}
            <div class="mt-2 d-flex gap-2">
                ${fromStar ? `<button class="btn btn-sm btn-outline-info py-0" style="font-size:0.7rem"
                    onclick='window.threejsFlyToStarId(${Number(fromStar.id)})'>📍 ${esc(starName(fromStar))}</button>` : ''}
                ${toStar ? `<button class="btn btn-sm btn-outline-info py-0" style="font-size:0.7rem"
                    onclick='window.threejsFlyToStarId(${Number(toStar.id)})'>📍 ${esc(starName(toStar))}</button>` : ''}
            </div>`;
        detailsPanel.style.display = 'block';
    }

    onMouseMove(event) {
        const rect = this.container.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);

        if (this.starField && this.starField.children.length > 0) {
            this.intersects = this.raycaster.intersectObjects(this.starField.children, true);

            if (this.intersects.length > 0) {
                const intersect = this.intersects[0];
                const pointIndex = intersect.index;

                if (pointIndex >= 0 && pointIndex < this.currentStars.length) {
                    const hoveredStar = this.currentStars[pointIndex];
                    const magLimit = this.starMaterial
                        ? this.starMaterial.uniforms.uMagLimit.value
                        : 15;
                    if (hoveredStar.magnitude > magLimit) return;

                    if (this.highlightedStar !== hoveredStar) {
                        this.clearStarHighlights();
                        this.highlightedStar = hoveredStar;
                        this.showStarTooltip(hoveredStar, event);
                    }
                }
            } else {
                this.clearStarHighlights();
                this.highlightedStar = null;
                // Pointer cursor over clickable route lines
                if (this.tradeRoutesGroup?.visible && this.tradeRoutesGroup.children.length) {
                    const hits = this.raycaster.intersectObjects(
                        this.tradeRoutesGroup.children.filter(c => c.visible), false);
                    this.container.style.cursor = hits.length ? 'pointer' : '';
                } else if (this.container.style.cursor) {
                    this.container.style.cursor = '';
                }
            }
        }
    }

    onMouseOut() {
        this.clearStarHighlights();
        this.highlightedStar = null;
    }

    displayStarDetails(star) {

        if (typeof window !== 'undefined' && window.app && window.app.selectStar) {
            window.app.selectStar(star);
        } else {
            this.createStarDetailsPanel(star);
        }
    }

    createStarDetailsPanel(star) {

        const detailsPanel = document.getElementById('starDetails');
        if (!detailsPanel) return;

        const detailsContent = document.getElementById('starDetailsContent');
        if (!detailsContent) return;

        const colonized = (this.eraYear == null)
            || (star.discovery_year == null)
            || (this.eraYear >= star.discovery_year);
        const starName = (colonized && star.fictional_name) || star.name || 'Unknown Star';
        const primaryName = star.name || (colonized ? star.fictional_name : null) || 'Unknown Star';
        const dist = star.distance ?? star.dist;

        // Look up nation — era-aware (ownership intervals or discovery_year gate)
        const holderId = this._nationIdAt(star);
        const nation = holderId
            ? this.nations.find(n => (n._id || n.id) === holderId)
            : null;
        const nationColor = nation ? ((nation.appearance && nation.appearance.color) || nation.color || '#888888') : null;

        // Find trade routes through this star
        const connectedRoutes = [];
        if (this.tradeRoutesGroup) {
            this.tradeRoutesGroup.children.forEach(child => {
                const r = child.userData?.data;
                if (!r) return;
                const fromId = r.endpoints?.from?.star_id;
                const toId   = r.endpoints?.to?.star_id;
                if (fromId === star.id || toId === star.id) {
                    connectedRoutes.push(r);
                }
            });
        }

        const discTag = star.discovery_number != null
            ? `<span class="badge bg-secondary ms-1" title="Discovery order">#${star.discovery_number}</span>` : '';
        const eraTag = star.discovery_year != null
            ? `<span class="badge ms-1" style="background:rgba(80,160,80,0.22);color:#88cc88;border:1px solid rgba(80,160,80,0.45);font-size:0.62rem;" title="Year colonized">⬡ ${star.discovery_year}</span>`
            : '';
        let html = `
            <h6 class="text-primary mb-1">${starName}${discTag}${eraTag}</h6>
            ${starName !== primaryName ? `<p class="small text-muted mb-1">${primaryName}</p>` : ''}
        `;

        // Nation badge
        if (nation && nationColor) {
            const safeColor = /^#[0-9A-Fa-f]{6}$/.test(nationColor) ? nationColor : '#888888';
            html += `
                <div class="mb-2 px-2 py-1 rounded d-flex align-items-center gap-2"
                     style="border-left:3px solid ${safeColor}; background:rgba(0,0,0,0.4)">
                    <span style="width:8px;height:8px;border-radius:50%;background:${safeColor};flex-shrink:0;display:inline-block;"></span>
                    <div>
                        <span class="small fw-bold">${nation.name}</span>
                        <br><small class="text-muted" style="font-size:0.7rem">${nation.government?.type || ''}</small>
                    </div>
                </div>
            `;
        }

        html += `
            <div class="row g-1 mb-2">
                <div class="col-6">
                    <small class="text-muted">Magnitude</small><br>
                    <span class="text-info">${star.magnitude != null ? star.magnitude.toFixed(2) : '—'}</span>
                </div>
                <div class="col-6">
                    <small class="text-muted">Type</small><br>
                    <span class="text-warning">${star.spectral_class || '—'}</span>
                </div>
                <div class="col-6">
                    <small class="text-muted">Distance</small><br>
                    <span class="text-success">${dist != null ? parseFloat(dist).toFixed(1) + ' pc' : '—'}</span>
                </div>
                <div class="col-6">
                    <small class="text-muted">Constellation</small><br>
                    <span class="text-success" style="font-size:0.8rem">${star.constellation || '—'}</span>
                </div>
            </div>

            <div class="mb-2">
                <small class="text-muted">Galactic coords (pc)</small><br>
                <small class="text-secondary font-monospace">
                    X ${star.x != null ? star.x.toFixed(2) : '?'} &nbsp;
                    Y ${star.y != null ? star.y.toFixed(2) : '?'} &nbsp;
                    Z ${star.z != null ? star.z.toFixed(2) : '?'}
                </small>
            </div>
        `;

        // Era info
        if (star.era_start || star.era_end) {
            html += `
                <div class="mb-2">
                    <small class="text-muted">Saga Era</small><br>
                    <small class="text-warning">${star.era_start || '?'} – ${star.era_end || '?'}</small>
                </div>
            `;
        }

        // Fictional description collapsible
        if (star.fictional_description) {
            html += `
                <div class="mb-2">
                    <button class="btn btn-sm btn-outline-secondary w-100 py-0"
                            style="font-size:0.75rem"
                            onclick="this.nextElementSibling.classList.toggle('d-none')">
                        📖 Saga Lore ▾
                    </button>
                    <div class="d-none mt-1 p-2 rounded" style="background:rgba(255,255,255,0.05);font-size:0.78rem">
                        ${star.fictional_description}
                    </div>
                </div>
            `;
        }

        // Trade routes through this star
        if (connectedRoutes.length > 0) {
            html += `<div class="mb-2"><small class="text-muted">Trade Routes (${connectedRoutes.length})</small>`;
            for (const r of connectedRoutes) {
                const color = r.route_type === 'Primary Trade' ? 'text-success' : 'text-secondary';
                html += `<div class="d-flex align-items-center gap-1 mt-1">
                    <span class="${color}" style="font-size:0.7rem">●</span>
                    <small style="font-size:0.75rem">${r.name || r.id || 'Route'}</small>
                    ${r.route_type ? `<small class="text-muted ms-auto" style="font-size:0.65rem">${r.route_type}</small>` : ''}
                </div>`;
            }
            html += '</div>';
        }

        // Known worlds — check both real and fictional exoplanets, dedup by name (fictional wins)
        const starNames = new Set([star.proper_name, star.fictional_name, star.name, star.bayer].filter(Boolean));
        const starPlanets = [];
        const _seenPlanetNames = new Set();
        for (const p of [...this.fictionalExoplanets, ...this.realExoplanets]) {
            if (starNames.has(p.host_star_name) || starNames.has(p.host_star)) {
                if (!_seenPlanetNames.has(p.name)) {
                    _seenPlanetNames.add(p.name);
                    starPlanets.push(p);
                }
            }
        }
        if (starPlanets.length > 0) {
            // Sort: main planets by orbit, then insert moons right after their parent
            const moons = starPlanets.filter(p => p.parent_planet);
            const mainPlanets = starPlanets.filter(p => !p.parent_planet);
            mainPlanets.sort((a, b) => (a.semi_major_axis_au || a.orbit || 99) - (b.semi_major_axis_au || b.orbit || 99));
            const orderedPlanets = [];
            for (const pl of mainPlanets) {
                orderedPlanets.push(pl);
                for (const m of moons) {
                    if (m.parent_planet === pl.name) orderedPlanets.push(m);
                }
            }
            // Any orphan moons (parent not in list) at end
            for (const m of moons) {
                if (!orderedPlanets.includes(m)) orderedPlanets.push(m);
            }
            const moonCount = moons.length;
            const planetCount = mainPlanets.length;
            html += `<div class="mt-2"><small class="text-muted">Known Worlds (${planetCount} planet${planetCount !== 1 ? 's' : ''}${moonCount ? `, ${moonCount} moon${moonCount !== 1 ? 's' : ''}` : ''})</small>`;
            for (const planet of orderedPlanets) {
                const ptype = planet.planet_type || '';
                const typeColor = {
                    'Earth-like': 'text-success', 'Rocky Moon': 'text-success',
                    'Gas Giant': 'text-warning', 'Ice Giant': 'text-info',
                    'Hot Neptune': 'text-danger', 'Hot Rocky': 'text-danger',
                    'Rocky': 'text-secondary', 'Ice/Rocky': 'text-info',
                    'Terrestrial': 'text-light', 'Super-Earth': 'text-success',
                }[ptype] || 'text-muted';
                const sma = planet.semi_major_axis_au || planet.orbit;
                const habMark = (planet.potentially_habitable === 1 || planet.is_habitable) ? ' 🌱' : '';
                const moonMark = planet.parent_planet ? ` <span class="text-muted" title="Moon of ${planet.parent_planet}">🌙</span>` : '';
                const indent = planet.parent_planet ? 'ms-3' : '';
                const mapBtn = planet.map_url
                    ? `<button class="btn btn-sm btn-outline-secondary py-0 ms-1" style="font-size:0.65rem"
                              onclick="window.openPlanetMap(${JSON.stringify(planet.map_url)}, ${JSON.stringify(planet.name)})">🗺 Map</button>`
                    : '';
                html += `
                <div class="mt-1 p-2 rounded ${indent}" style="background:rgba(0,0,0,0.4)">
                    <div class="d-flex justify-content-between align-items-start">
                        <small>
                            <span class="text-info fw-bold">${planet.name}${habMark}${moonMark}</span>
                            ${ptype ? `<span class="${typeColor} ms-2">${ptype}</span>` : ''}
                            ${sma ? `<span class="text-muted ms-2">${parseFloat(sma).toFixed(2)} AU</span>` : ''}
                        </small>
                        ${mapBtn}
                    </div>
                    ${planet.description ? `<small class="text-muted" style="font-size:0.72rem">${planet.description}</small>` : ''}
                </div>`;
            }
            html += `</div>`;
        }

        // Province browser shortcuts for Union worlds hosted at this star
        const PROVINCE_WORLDS = { 48941: ['Stahlburgh', 'Eisenwald'], 46945: ['Hansaburgh'], 999999: ['Brandstadt'], 43464: ['Lochiel'] };
        const hostedWorlds = PROVINCE_WORLDS[star.id];
        if (hostedWorlds && window.openProvinceBrowser) {
            html += `<div class="mt-2 d-flex gap-1 flex-wrap">` + hostedWorlds.map(w =>
                `<button class="btn btn-sm btn-outline-warning py-0" style="font-size:0.7rem"
                     onclick='window.openProvinceBrowser(${JSON.stringify(w)})'>🏙 ${w} Provinces</button>`
            ).join('') + `</div>`;
        }

        // System map + star ID row
        html += `
        <div class="mt-2 d-flex justify-content-between align-items-center">
            <small class="text-secondary">ID: ${star.id || '—'}</small>
            <button class="btn btn-sm btn-outline-info py-0"
                    style="font-size:0.72rem"
                    onclick='window.openSystemMap(${JSON.stringify(star)})'>
                🪐 System Map
            </button>
        </div>`;

        detailsContent.innerHTML = html;
        detailsPanel.style.display = 'block';
    }

    highlightStar(star) {
        this.clearStarHighlights();

        if (!star || star.x == null || star.y == null || star.z == null) return;

        const geometry = new THREE.SphereGeometry(0.5, 16, 16);
        const material = new THREE.MeshBasicMaterial({
            color: 0xFFD700,
            transparent: true,
            opacity: 0.8
        });

        const highlight = new THREE.Mesh(geometry, material);
        highlight.position.set(star.x * 10, star.y * 10, star.z * 10);
        highlight.userData = { type: 'star_highlight', star: star };

        this.scene.add(highlight);

        // Show habitable zone rings around the selected star
        this.showHabitableZoneRing(star);

        console.log('✨ Highlighted star:', star.fictional_name || star.name);
    }

    clearStarHighlights() {
        const highlights = [];
        this.scene.children.forEach(child => {
            if (child.userData && child.userData.type === 'star_highlight') {
                highlights.push(child);
            }
        });
        highlights.forEach(h => {
            this.scene.remove(h);
            if (h.geometry) h.geometry.dispose();
            if (h.material) h.material.dispose();
        });
        // Also clear HZ rings
        this.clearHabitableZoneRings();
    }

    showStarTooltip(star, event) {

        let tooltip = document.getElementById('starTooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'starTooltip';
            tooltip.style.cssText = `
                position: fixed;
                background: rgba(0,0,0,0.85);
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                z-index: 1000;
                border: 1px solid #444;
                max-width: 200px;
            `;
            document.body.appendChild(tooltip);
        }

        const colonized = (this.eraYear == null)
            || (star.discovery_year == null)
            || (this.eraYear >= star.discovery_year);
        const starName = (colonized && star.fictional_name) || star.name || 'Unknown Star';
        const magnitude = star.magnitude != null ? star.magnitude.toFixed(2) : '—';
        const spectral = star.spectral_class || '—';

        // Look up nation for tooltip — era-aware
        const tooltipHolderId = this._nationIdAt(star);
        const nation = tooltipHolderId
            ? this.nations.find(n => (n._id || n.id) === tooltipHolderId)
            : null;
        const nationName = nation ? nation.name : '';
        const nationColor = nation ? ((nation.appearance && nation.appearance.color) || '#888') : '';
        const safeColor = /^#[0-9A-Fa-f]{6}$/.test(nationColor) ? nationColor : '#888';

        const discNum = star.discovery_number != null ? ` <span style="color:#aaa;font-size:10px">#${star.discovery_number}</span>` : '';
        tooltip.innerHTML = `
            <strong>${starName}</strong>${discNum}<br>
            <span style="color:#7cf">Mag:</span> ${magnitude} &nbsp;
            <span style="color:#fc7">Type:</span> ${spectral}
            ${nationName ? `<br><span style="color:${safeColor}">■</span> ${nationName}` : ''}
        `;

        tooltip.style.left = (event.pageX + 12) + 'px';
        tooltip.style.top  = (event.pageY +  8) + 'px';
        tooltip.style.display = 'block';

        clearTimeout(this.tooltipTimeout);
        this.tooltipTimeout = setTimeout(() => {
            if (tooltip) tooltip.style.display = 'none';
        }, 2500);
    }

    createGalacticAxes() {
        this.axesHelper = new THREE.AxesHelper(100);
        this.scene.add(this.axesHelper);
        this.createAxisLabels();
    }

    createAxisLabels() {
        const labelTexts = ['X+', 'Y+', 'Z+'];
        const positions = [
            new THREE.Vector3(110, 0, 0),
            new THREE.Vector3(0, 110, 0),
            new THREE.Vector3(0, 0, 110)
        ];
        const colors = [0xff0000, 0x00ff00, 0x0000ff];

        this.axisLabels = [];
        labelTexts.forEach((text, i) => {
            const canvas = document.createElement('canvas');
            canvas.width = 128;
            canvas.height = 64;
            const context = canvas.getContext('2d');
            context.font = '48px Arial';
            context.fillStyle = `#${colors[i].toString(16).padStart(6, '0')}`;
            context.fillText(text, 10, 50);

            const texture = new THREE.CanvasTexture(canvas);
            const material = new THREE.SpriteMaterial({ map: texture });
            const sprite = new THREE.Sprite(material);
            sprite.position.copy(positions[i]);
            sprite.scale.set(10, 5, 1);

            this.axisLabels.push(sprite);
            this.scene.add(sprite);
        });
    }

    // ── Star name labels ─────────────────────────────────────────────────────
    // Persistent labels for notable systems: the 14 discovery systems and
    // fictional stars. Era-aware — before a system's colonization year the
    // label falls back to the astronomical name (or hides if there is none).

    _makeLabelTexture(text, color = '#d5e5ff') {
        const canvas = document.createElement('canvas');
        canvas.width = 512; canvas.height = 96;
        const ctx = canvas.getContext('2d');
        ctx.font = '600 40px "Segoe UI", Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.shadowColor = 'rgba(0,0,0,0.95)';
        ctx.shadowBlur = 12;
        ctx.fillStyle = color;
        ctx.fillText(text, 256, 50);
        return new THREE.CanvasTexture(canvas);
    }

    createStarLabels() {
        while (this.labelsGroup.children.length > 0) {
            const c = this.labelsGroup.children[0];
            this.labelsGroup.remove(c);
            c.material?.map?.dispose();
            c.material?.dispose();
        }

        const notable = this.currentStars.filter(s =>
            s.fictional_name || s.discovery_number != null);

        const placed = new Set();   // avoid stacked duplicates (e.g. binary companions sharing a name)
        for (const star of notable) {
            const postName = star.fictional_name || star.name;
            const key = `${postName}@${Math.round(star.x)},${Math.round(star.y)},${Math.round(star.z)}`;
            if (placed.has(key)) continue;
            placed.add(key);
            const preName = star.proper_name || (star.is_fictional ? null : star.name);
            if (!postName) continue;

            const texPost = this._makeLabelTexture(postName, star.is_fictional ? '#8fffd0' : '#d5e5ff');
            // Only build a second texture when the pre-colonization name differs
            const texPre = (preName && preName !== postName)
                ? this._makeLabelTexture(preName, '#9aa8c0')
                : (star.discovery_year != null ? null : texPost);

            const material = new THREE.SpriteMaterial({
                map: texPost, transparent: true, depthWrite: false, opacity: 0.92,
            });
            const sprite = new THREE.Sprite(material);
            sprite.position.set(star.x * 10, star.y * 10 + 2.2, star.z * 10);
            sprite.scale.set(14, 2.6, 1);
            sprite.userData = { star, texPre, texPost, passesFilter: true };
            this.labelsGroup.add(sprite);
        }
        this.updateStarLabels();
        console.log(`🏷 Created ${this.labelsGroup.children.length} star labels`);
    }

    /** Mirror of _recomputeFilter's per-star logic for label visibility. */
    _starPassesFilter(star) {
        if (this.nationFilter || this.nationFilter2) {
            const holder = this._nationIdAt(star);
            const matches = (set, id) => {
                if (!set) return false;
                if (this.ownershipByStar?.has(star.id)) return holder === id;
                return holder != null && set.has(star.id);
            };
            if (!matches(this.nationFilter, this.nationFilterId) &&
                !matches(this.nationFilter2, this.nationFilterId2)) return false;
        }
        if (this.eraYear != null && (star.era_start != null || star.era_end != null)) {
            if ((star.era_start != null && this.eraYear < star.era_start) ||
                (star.era_end != null && this.eraYear > star.era_end)) return false;
        }
        return true;
    }

    /** Re-evaluate label text (pre/post colonization) + filter state. */
    updateStarLabels() {
        this.labelsGroup.children.forEach(sp => {
            const { star, texPre, texPost } = sp.userData;
            const colonized = (this.eraYear == null)
                || (star.discovery_year == null)
                || (this.eraYear >= star.discovery_year);
            const tex = colonized ? texPost : texPre;
            sp.userData.eraVisible = !!tex && this._starPassesFilter(star);
            if (tex && sp.material.map !== tex) {
                sp.material.map = tex;
                sp.material.needsUpdate = true;
            }
        });
    }

    // Era-dependent territory: ownership intervals loaded from /api/v1/star-ownership.
    async loadOwnership() {
        try {
            const response = await fetch('/api/v1/star-ownership');
            const data = await response.json();
            if (data.success && Array.isArray(data.data) && data.data.length) {
                this.ownershipByStar = new Map();
                for (const row of data.data) {
                    if (!this.ownershipByStar.has(row.star_id)) this.ownershipByStar.set(row.star_id, []);
                    this.ownershipByStar.get(row.star_id).push(row);
                }
                // Keep intervals sorted so "latest" lookups are cheap
                for (const list of this.ownershipByStar.values()) {
                    list.sort((a, b) => a.era_start - b.era_start);
                }
                if (this.politicalView) this._refreshNationColors();
                return true;
            }
            return false;
        } catch (error) {
            console.warn('🗺 loadOwnership failed:', error);
            return false;
        }
    }

    /**
     * Which nation holds this star at the given year (default: current eraYear)?
     * Prefers ownership intervals when the star has them; otherwise falls back
     * to the static star.nation_id gated by discovery_year.
     */
    _nationIdAt(star, year = this.eraYear) {
        const intervals = this.ownershipByStar?.get(star.id ?? star._id);
        if (intervals && intervals.length) {
            if (year == null) {
                // No era filter → present-day view: only an interval reaching
                // the end of the timeline counts. A closed final interval
                // means the holder left (e.g. a liberated client state).
                const iv = intervals.find(v => v.era_end >= 3000);
                return iv ? iv.nation_id : null;
            }
            const iv = intervals.find(v => year >= v.era_start && year <= v.era_end);
            return iv ? iv.nation_id : null;
        }
        if (year != null && star.discovery_year != null && year < star.discovery_year) return null;
        return star.nation_id || null;
    }

    // Overlay Loading Methods
    async loadNations() {
        console.log('🏛️ loadNations called - loading nations overlay...');
        try {
            const response = await fetch('/api/v1/nations');
            const data = await response.json();

            if (data.success && data.data) {
                console.log(`🎯 Creating nations for ${data.data.length} nations`);
                this.createNationsOverlay(data.data);
                this.nations = data.data;
                return true;
            }
            return false;
        } catch (error) {
            console.warn('🏛️ loadNations failed:', error);
            return false;
        }
    }

    createNationsOverlay(nations) {
        // Clear existing nation objects
        while (this.nationsGroup.children.length > 0) {
            const child = this.nationsGroup.children[0];
            this.nationsGroup.remove(child);
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
        }

        nations.forEach((nation, index) => {

            if (nation.territories && nation.territories.length > 0) {
                // Find all stars that belong to this nation
                const nationStars = [];
                nation.territories.forEach(territoryId => {
                    const star = this.currentStars.find(s => s.id === territoryId);
                    if (star && star.x !== undefined) {
                        nationStars.push(star);
                    }
                });

                if (nationStars.length > 0) {
                    console.log(`🏛️ ${nation.name}: Found ${nationStars.length} stars`);
                    this.createTerritoryBoundary(nation, nationStars, index);
                } else {
                    console.warn(`⚠️ Could not find coordinates for nation stars: ${nation.name}`);
                }
            }
        });

        console.log(`✅ Created nations overlay with ${this.nationsGroup.children.length} territory boundaries`);
    }

    createTerritoryBoundary(nation, nationStars, index) {
        let nationColor = new THREE.Color().setHSL(index / 10, 0.8, 0.6);

        if (nation.appearance && nation.appearance.color) {
            nationColor = new THREE.Color(nation.appearance.color);
        }

        if (nationStars.length === 1) {
            // Single star - create a sphere around it
            this.createSingleStarTerritory(nation, nationStars[0], nationColor);
        } else {
            // Multiple stars - create boundary that encompasses all
            this.createMultiStarTerritory(nation, nationStars, nationColor);
        }

        console.log(`🏛️ Added territory boundary: ${nation.name} (${nationStars.length} stars)`);
    }

    createSingleStarTerritory(nation, star, color) {
        // Influence sphere around a single-system nation. Needs to read at
        // galaxy zoom next to the multi-star boundaries, so ~2.4 pc radius
        // (stars are plotted at 10 units/pc).
        let sphereRadius = 16.0;

        // Slightly larger for full interstellar polities vs trade outposts
        if (nation._id === 'protelani_republic' || nation._id === 'dorsai_republic') {
            sphereRadius = 24.0;
        }

        const geometry = new THREE.SphereGeometry(sphereRadius, 16, 16);
        const material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.3,
            wireframe: true
        });

        const sphere = new THREE.Mesh(geometry, material);
        sphere.position.set(star.x * 10, star.y * 10, star.z * 10);
        sphere.userData = { type: 'nation_territory', data: nation, stars: [star] };

        this.nationsGroup.add(sphere);
    }

    createMultiStarTerritory(nation, nationStars, color) {
        // Calculate the center of all nation stars
        let centerX = 0, centerY = 0, centerZ = 0;
        nationStars.forEach(star => {
            centerX += star.x;
            centerY += star.y;
            centerZ += star.z;
        });
        centerX /= nationStars.length;
        centerY /= nationStars.length;
        centerZ /= nationStars.length;

        // Calculate the maximum distance from center to any star
        let maxDistance = 0;
        nationStars.forEach(star => {
            const distance = Math.sqrt(
                Math.pow(star.x - centerX, 2) +
                Math.pow(star.y - centerY, 2) +
                Math.pow(star.z - centerZ, 2)
            );
            maxDistance = Math.max(maxDistance, distance);
        });

        // Create boundary sphere encompassing all stars with some padding
        const boundaryRadius = (maxDistance + 2.0) * 10; // Add padding and scale
        const geometry = new THREE.SphereGeometry(boundaryRadius, 16, 16);
        const material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.2,
            wireframe: true
        });

        const sphere = new THREE.Mesh(geometry, material);
        sphere.position.set(centerX * 10, centerY * 10, centerZ * 10);
        sphere.userData = { type: 'nation_territory', data: nation, stars: nationStars };

        this.nationsGroup.add(sphere);

        // Add connections between stars in the same nation
        this.createStarConnections(nationStars, color, nation);
    }

    createStarConnections(stars, color, nation) {
        // Create lines connecting all stars within the nation
        for (let i = 0; i < stars.length; i++) {
            for (let j = i + 1; j < stars.length; j++) {
                const points = [
                    new THREE.Vector3(stars[i].x * 10, stars[i].y * 10, stars[i].z * 10),
                    new THREE.Vector3(stars[j].x * 10, stars[j].y * 10, stars[j].z * 10)
                ];

                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const material = new THREE.LineBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: 0.4
                });

                const line = new THREE.Line(geometry, material);
                // Store nation + both endpoints so filterByEra() can check discovery_year
                line.userData = {
                    type: 'nation_connection',
                    data: nation,
                    starA: stars[i],
                    starB: stars[j],
                };
                this.nationsGroup.add(line);
            }
        }
    }

    async loadTradeRoutes() {
        console.log('🚛 loadTradeRoutes called - loading trade routes overlay...');
        try {
            const response = await fetch('/api/v1/trade-routes');
            const data = await response.json();

            if (data.success && data.data) {
                console.log(`🎯 Creating trade routes for ${data.data.length} routes`);
                this.createTradeRoutesOverlay(data.data);
                return true;
            }
            return false;
        } catch (error) {
            console.warn('🚛 loadTradeRoutes failed:', error);
            return false;
        }
    }

    /**
     * Visual style for a trade route: color follows the controlling nation,
     * dash rhythm and flow speed follow the route's role —
     * military supply lines pulse fast and staccato, bulk logistics crawl.
     */
    _routeStyle(route) {
        const nation = this.nations.find(n => (n._id || n.id) === route.nation_id);
        const hex = nation ? ((nation.appearance && nation.appearance.color) || nation.color) : null;
        const color = (hex && /^#[0-9A-Fa-f]{6}$/.test(hex)) ? parseInt(hex.slice(1), 16) : 0x888888;

        const t = route.route_type || '';
        if (/Military|Defense/.test(t)) {
            return { color, dashSize: 2, gapSize: 2, opacity: 0.9, flowSpeed: 14 };
        }
        if (/Primary|Internal|Colonial|Neutral|Multi/.test(t)) {
            return { color, dashSize: 4, gapSize: 2, opacity: 0.8, flowSpeed: 8 };
        }
        // Supply / mining / frontier / administrative logistics
        return { color, dashSize: 3, gapSize: 3.5, opacity: 0.55, flowSpeed: 3.5 };
    }

    createTradeRoutesOverlay(routes) {
        // Clear existing trade route objects
        while (this.tradeRoutesGroup.children.length > 0) {
            const child = this.tradeRoutesGroup.children[0];
            this.tradeRoutesGroup.remove(child);
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
        }

        routes.forEach((route, index) => {
            if (route.endpoints && route.endpoints.from && route.endpoints.to) {
                const fromStar = this.currentStars.find(star => star.id === route.endpoints.from.star_id);
                const toStar = this.currentStars.find(star => star.id === route.endpoints.to.star_id);

                if (fromStar && toStar) {
                    const points = [
                        new THREE.Vector3(fromStar.x * 10, fromStar.y * 10, fromStar.z * 10),
                        new THREE.Vector3(toStar.x * 10, toStar.y * 10, toStar.z * 10)
                    ];

                    const geometry = new THREE.BufferGeometry().setFromPoints(points);

                    // Style: color = controlling nation, dash rhythm + flow speed = route class
                    const style = this._routeStyle(route);
                    const material = new THREE.LineDashedMaterial({
                        color: style.color,
                        dashSize: style.dashSize,
                        gapSize:  style.gapSize,
                        transparent: true,
                        opacity: style.opacity,
                    });

                    const line = new THREE.Line(geometry, material);
                    // computeLineDistances() is required for LineDashedMaterial
                    line.computeLineDistances();
                    // Keep the pristine distances: the flow animation shifts the
                    // lineDistance attribute against these each frame.
                    const distAttr = line.geometry.attributes.lineDistance;
                    line.userData = {
                        type: 'trade_route', data: route,
                        flowSpeed: style.flowSpeed,
                        fromStar, toStar,
                        baseLineDistances: Array.from(distAttr.array),
                    };

                    this.tradeRoutesGroup.add(line);
                }
            }
        });

        console.log(`✅ Created trade routes overlay with ${this.tradeRoutesGroup.children.length} lines`);
    }

    async loadStellarRegions() {
        console.log('🌌 loadStellarRegions called - loading stellar regions overlay...');
        try {
            const response = await fetch('/api/v1/stellar-regions');
            const data = await response.json();

            if (data.success && data.data) {
                console.log(`🎯 Creating stellar regions for ${data.data.length} regions`);
                this.createStellarRegionsOverlay(data.data);
                return true;
            }
            return false;
        } catch (error) {
            console.warn('🌌 loadStellarRegions failed:', error);
            return false;
        }
    }

    createStellarRegionsOverlay(regions) {
        // Clear existing stellar region objects
        while (this.stellarRegionsGroup.children.length > 0) {
            const child = this.stellarRegionsGroup.children[0];
            this.stellarRegionsGroup.remove(child);
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
        }

        regions.forEach((region, index) => {

            if (region.center && region.x_range && region.y_range && region.z_range) {
                const geometry = new THREE.BoxGeometry(
                    (region.x_range[1] - region.x_range[0]) * 10,
                    (region.y_range[1] - region.y_range[0]) * 10,
                    (region.z_range[1] - region.z_range[0]) * 10
                );

                let color = new THREE.Color().setHSL((index * 0.618) % 1, 0.7, 0.5);
                if (region.color && Array.isArray(region.color) && region.color.length >= 3) {
                    color = new THREE.Color(region.color[0] / 255, region.color[1] / 255, region.color[2] / 255);
                }

                const material = new THREE.MeshBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: 0.15,
                    wireframe: true
                });

                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(
                    region.center[0] * 10,
                    region.center[1] * 10,
                    region.center[2] * 10
                );
                mesh.userData = { type: 'stellar_region', data: region };

                this.stellarRegionsGroup.add(mesh);
                console.log(`🌌 Added stellar region: ${region.name}`);
            }
        });

        console.log(`✅ Created stellar regions overlay with ${this.stellarRegionsGroup.children.length} regions`);
    }

    async loadExoplanets() {
        console.log('🪐 loadExoplanets called - loading real + fictional exoplanets...');
        try {
            const [realRes, fictionalRes] = await Promise.all([
                fetch('/api/v1/exoplanets'),
                fetch('/api/v1/fictional-exoplanets'),
            ]);
            const realData      = await realRes.json();
            const fictionalData = await fictionalRes.json();

            const allPlanets = [];

            if (realData.success && realData.data) {
                // Normalise host_star field for overlay lookup
                const normalised = realData.data.map(p => ({
                    ...p,
                    host_star: p.host_star_name || p.host_star,
                }));
                this.realExoplanets = normalised;   // ← stored for system map lookup
                allPlanets.push(...normalised);
            }

            if (fictionalData.success && fictionalData.data) {
                // Normalise: createExoplanetsOverlay reads planet.host_star
                const normalised = fictionalData.data.map(p => ({
                    ...p,
                    host_star: p.host_star_name || p.host_star,
                }));
                this.fictionalExoplanets = normalised;
                allPlanets.push(...normalised);
            }

            if (allPlanets.length > 0) {
                console.log(`🎯 Creating exoplanets overlay for ${allPlanets.length} planets`);
                this.createExoplanetsOverlay(allPlanets);
            }
            return true;
        } catch (error) {
            console.warn('🪐 loadExoplanets failed:', error);
            return false;
        }
    }

    createExoplanetsOverlay(exoplanets) {
        // Clear existing exoplanet objects
        while (this.exoplanetGroup.children.length > 0) {
            const child = this.exoplanetGroup.children[0];
            this.exoplanetGroup.remove(child);
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
        }

        const planetStars = exoplanets.reduce((acc, planet) => {
            const starKey = planet.host_star || planet.star_id;
            if (!acc[starKey]) acc[starKey] = [];
            acc[starKey].push(planet);
            return acc;
        }, {});

        Object.keys(planetStars).forEach(hostStarName => {
            const hostStar = this.currentStars.find(star =>
                star.name === hostStarName ||
                star.fictional_name === hostStarName ||
                star.id === parseInt(hostStarName) ||
                (star.catalog_ids && star.catalog_ids.includes(hostStarName))
            );

            if (hostStar) {
                this.createPlanetsForStar(hostStar, planetStars[hostStarName]);
            }
        });

        console.log(`✅ Created exoplanets overlay with ${this.exoplanetGroup.children.length} planets`);
    }

    createPlanetsForStar(hostStar, planets) {
        planets.forEach((planet, index) => {
            const orbitRadius = 1 + (index * 0.5);
            const angle = (index / planets.length) * Math.PI * 2;

            const planetX = hostStar.x * 10 + Math.cos(angle) * orbitRadius * 10;
            const planetY = hostStar.y * 10 + Math.sin(angle) * 0.1 * orbitRadius * 10;
            const planetZ = hostStar.z * 10 + Math.sin(angle) * orbitRadius * 10;

            const geometry = new THREE.SphereGeometry(0.3, 8, 8);
            const material = new THREE.MeshBasicMaterial({
                color: 0x4CAF50,
                transparent: true,
                opacity: 0.8
            });

            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.set(planetX, planetY, planetZ);
            sphere.userData = { type: 'exoplanet', data: { ...planet, hostStar } };

            this.exoplanetGroup.add(sphere);
        });
    }



    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());

        this.processKeyboardInput();

        // Smooth fly-to animation
        if (this.flyAnimation) {
            const fa = this.flyAnimation;
            const elapsed = performance.now() - fa.startTime;
            const t = Math.min(elapsed / fa.duration, 1);
            const ease = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
            this.camera.position.lerpVectors(fa.startPos, fa.endPos, ease);
            this.controls.target.lerpVectors(fa.startTarget, fa.endTarget, ease);
            if (t >= 1) this.flyAnimation = null;
        }

        if (this.controls && this.controls.update) {
            this.controls.update();
        }

        // Keep LOD shader uniform in sync with camera distance
        if (this.starMaterial) {
            const target = (this.controls && this.controls.target)
                ? this.controls.target
                : new THREE.Vector3(0, 0, 0);
            this.starMaterial.uniforms.uCameraDistance.value =
                this.camera.position.distanceTo(target);
        }

        // Animate trade route dashes (flowing pulses). Core LineDashedMaterial
        // has no dashOffset uniform, so flow is done by sliding the lineDistance
        // attribute: mod(vLineDistance, totalSize) shifts → dashes march along.
        const delta = this.clock.getDelta();
        this._dashFlowOffset = (this._dashFlowOffset || 0) + delta;
        this.tradeRoutesGroup.children.forEach(child => {
            const base = child.userData?.baseLineDistances;
            if (!base || !child.material?.isLineDashedMaterial) return;
            const speed = child.userData.flowSpeed ?? 3.0;
            const attr = child.geometry.attributes.lineDistance;
            const cycle = child.material.dashSize + child.material.gapSize;
            const off = (this._dashFlowOffset * speed) % cycle;
            // Subtract so dashes travel from the origin star toward the destination
            for (let i = 0; i < base.length; i++) attr.array[i] = base[i] - off;
            attr.needsUpdate = true;
        });

        // Star labels: scaled with distance for constant on-screen size, and
        // eased opacity instead of a hard visibility pop — labels fade out
        // across the 330–430 unit band and fade in/out on era changes.
        if (this.labelsGroup.visible && this.labelsGroup.children.length) {
            const camPos = this.camera.position;
            const ease = Math.min(1, delta * 6);
            this.labelsGroup.children.forEach(sp => {
                const d = camPos.distanceTo(sp.position);
                const distFactor = 1 - Math.max(0, Math.min(1, (d - 330) / 100));
                const target = (sp.userData.eraVisible === false) ? 0 : 0.92 * distFactor;
                const o = sp.material.opacity + (target - sp.material.opacity) * ease;
                sp.material.opacity = o;
                sp.visible = o > 0.02;
                if (sp.visible) {
                    const w = Math.max(3, Math.min(16, d * 0.05));
                    sp.scale.set(w, w * 0.19, 1);
                }
            });
        }

        this.render();
    }

    render() {
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    // ── Nation / Political-view methods ──────────────────────────────────────

    /** Recompute aFilter from nation filter(s) + era filter combined. */
    _recomputeFilter() {
        const filterAttr = this.points?.geometry?.attributes?.aFilter;
        if (!filterAttr) return;

        for (let i = 0; i < this.currentStars.length; i++) {
            const star = this.currentStars[i];

            // Nation filter(s): 1.0 if matches nation1 OR nation2 (or no filter)
            let nf = 1.0;
            if (this.nationFilter || this.nationFilter2) {
                const holder = this._nationIdAt(star);   // null = unheld at this era
                const matches = (set, id) => {
                    if (!set) return false;
                    // Stars with ownership intervals match by current holder, so
                    // territory that changes hands follows the era. Others use
                    // the static membership set.
                    if (this.ownershipByStar?.has(star.id)) return holder === id;
                    return holder != null && set.has(star.id);
                };
                nf = (matches(this.nationFilter, this.nationFilterId) ||
                      matches(this.nationFilter2, this.nationFilterId2)) ? 1.0 : 0.0;
            }

            // Era filter: 1.0 if the star exists in the current era, 0.0 otherwise
            let ef = 1.0;
            if (this.eraYear != null) {
                const es = star.era_start;
                const ee = star.era_end;
                if (es != null || ee != null) {
                    const inEra = (es == null || this.eraYear >= es) &&
                                  (ee == null || this.eraYear <= ee);
                    ef = inEra ? 1.0 : 0.0;
                }
            }

            filterAttr.array[i] = Math.min(nf, ef);
        }
        filterAttr.needsUpdate = true;
        this.updateStarLabels();
    }

    filterByNation(nationId) {
        this.nationFilter2 = null;  // clear compare-mode second filter
        this.nationFilterId2 = null;
        if (!nationId) {
            this.nationFilter = null;
            this.nationFilterId = null;
        } else {
            const nation = this.nations.find(n => (n._id || n.id) === nationId);
            const memberIds = new Set(
                (nation?.territories || []).map(t => t.star_id ?? t)
            );
            this.nationFilter = memberIds;
            this.nationFilterId = nationId;
        }
        this._recomputeFilter();
    }

    filterByEra(year) {
        this.eraYear = (year == null || isNaN(year)) ? null : parseInt(year);
        this._recomputeFilter();
        if (this.politicalView) this._refreshNationColors();

        // Filter trade routes by era (era_start/era_end on each route)
        if (this.tradeRoutesGroup) {
            this.tradeRoutesGroup.children.forEach(child => {
                if (this.eraYear == null) { child.visible = true; return; }
                const route = child.userData?.data;
                if (!route) return;
                const rs = route.era_start, re = route.era_end;
                child.visible = (rs == null || this.eraYear >= rs) &&
                                (re == null || this.eraYear <= re);
            });
        }

        // Also dim/show nation overlays by era
        if (this.nationsGroup) {
            this.nationsGroup.children.forEach(child => {
                if (this.eraYear == null) { child.visible = true; return; }
                const type   = child.userData?.type;
                const nation = child.userData?.data;

                if (type === 'nation_territory') {
                    // Check nation founding year first
                    const ns = nation?.era_start, ne = nation?.era_end;
                    const nationFounded = (ns == null || this.eraYear >= ns) &&
                                         (ne == null || this.eraYear <= ne);
                    if (!nationFounded) { child.visible = false; return; }
                    // Also require the earliest territory star to be colonized
                    const stars = child.userData?.stars || [];
                    const minDisc = stars.reduce((mn, s) =>
                        (s.discovery_year != null && s.discovery_year < mn) ? s.discovery_year : mn,
                        Infinity);
                    child.visible = (minDisc === Infinity || this.eraYear >= minDisc);

                } else if (type === 'nation_connection') {
                    // Check nation founding year
                    const ns = nation?.era_start;
                    if (ns != null && this.eraYear < ns) { child.visible = false; return; }
                    // Show line only when BOTH endpoint stars are colonized
                    const dyA = child.userData?.starA?.discovery_year;
                    const dyB = child.userData?.starB?.discovery_year;
                    child.visible = (dyA == null || this.eraYear >= dyA) &&
                                    (dyB == null || this.eraYear >= dyB);

                } else {
                    child.visible = true;
                }
            });
        }
    }

    /** Rebuild aNationColor attribute respecting current eraYear + discovery_year. */
    _refreshNationColors() {
        if (!this.points) return;
        const colorMap = {};
        for (const n of this.nations) {
            const hex = (n.appearance && n.appearance.color) || n.color || '#888888';
            if (!/^#[0-9A-Fa-f]{6}$/.test(hex)) continue;
            colorMap[n._id || n.id] = [
                parseInt(hex.slice(1, 3), 16) / 255,
                parseInt(hex.slice(3, 5), 16) / 255,
                parseInt(hex.slice(5, 7), 16) / 255,
            ];
        }
        const attr = this.points.geometry.attributes.aNationColor;
        const sc   = this.points.geometry.attributes.starColor;
        for (let i = 0; i < this.currentStars.length; i++) {
            const star = this.currentStars[i];
            const nid = this._nationIdAt(star);
            const c = nid ? (colorMap[nid] || null) : null;
            if (c) {
                attr.setXYZ(i, c[0], c[1], c[2]);
            } else {
                // Uncolonized or no nation — fall back to spectral color
                attr.setXYZ(i, sc.getX(i), sc.getY(i), sc.getZ(i));
            }
        }
        attr.needsUpdate = true;
    }

    setPoliticalView(enabled) {
        this.politicalView = enabled;
        if (this.starMaterial) {
            this.starMaterial.uniforms.uPoliticalView.value = enabled;
        }
        if (enabled) this._refreshNationColors();
    }

    /** Set the camera orbit target (star-coords) and position the camera above it. */
    setCameraCenter(cx, cy, cz) {
        if (!this.controls || !this.camera) return;
        this.controls.target.set(cx * 10, cy * 10, cz * 10);
        this.camera.position.set(cx * 10, cy * 10 + 200, cz * 10 + 200);
        this.controls.update();
    }

    // ── Camera fly-to animation ──────────────────────────────────────────────

    flyToStar(star, offsetDistance = 25) {
        if (!star || star.x == null) return;
        const endTarget = new THREE.Vector3(star.x * 10, star.y * 10, star.z * 10);
        const dir = this.camera.position.clone()
            .sub(this.controls.target).normalize();
        const endPos = endTarget.clone().addScaledVector(dir, offsetDistance);
        this.flyAnimation = {
            startPos:    this.camera.position.clone(),
            endPos,
            startTarget: this.controls.target.clone(),
            endTarget,
            t:           0,
            duration:    1500,
            startTime:   performance.now(),
        };
    }

    applyQuickView({ nationId, target, cameraOffset, magLimit, showTradeRoutes, showNations }) {
        // Fly camera to target (target coords are in parsec space)
        this.flyToStar({ x: target.x, y: target.y, z: target.z }, cameraOffset ?? 30);

        // Nation filter
        this.filterByNation(nationId || null);

        // Overlay visibility
        if (showTradeRoutes != null) this.tradeRoutesGroup.visible = showTradeRoutes;
        if (showNations != null)     this.nationsGroup.visible = showNations;

        // Magnitude limit
        if (magLimit != null && this.starMaterial) {
            this.starMaterial.uniforms.uMagLimit.value = magLimit;
        }
    }

    // ── Habitable Zone rings (3D indicator around selected star) ─────────────

    /**
     * Estimate luminosity (solar = 1) from spectral class if not known.
     */
    static _spectralLuminosity(spec) {
        const cls = (spec || 'G')[0].toUpperCase();
        return { O: 50000, B: 800, A: 8, F: 1.8, G: 1, K: 0.35, M: 0.04 }[cls] ?? 1;
    }

    clearHabitableZoneRings() {
        while (this.habitableZoneGroup.children.length > 0) {
            const child = this.habitableZoneGroup.children[0];
            this.habitableZoneGroup.remove(child);
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
        }
    }

    showHabitableZoneRing(star) {
        this.clearHabitableZoneRings();
        if (!star || star.x == null) return;

        // Catalog luminosities are visual-band and understate cool stars
        // (M ~4x, K ~2x); apply the same rough bolometric correction the
        // system map uses. The spectral fallback is already bolometric-ish.
        const spec = (star.spectral_class || 'G').trim().toUpperCase();
        const subRaw = parseFloat(spec.slice(1));
        const sub = Number.isFinite(subRaw) ? Math.min(subRaw, 9) : 5;
        const BOL = ({ M: 3.0 + 0.7 * sub, K: 1.1 + 0.13 * sub, G: 1.1 })[spec.charAt(0)] ?? 1.0;
        const L = star.luminosity
            ? star.luminosity * BOL
            : ThreeJSStarmap._spectralLuminosity(star.spectral_class);
        // Habitable zone radii in AU, then convert to parsecs (1 AU = 1/206265 pc)
        // At galaxy scale (1 pc = 10 Three.js units) these are microscopic, so we show
        // a stylized scaled ring that signals "this star has a habitable zone."
        // Visual scale: inner ≈ 0.8 units, outer ≈ 1.6 units around the star.
        const baseInner = 0.8;
        const baseOuter = 1.6 + Math.log10(Math.max(L, 0.01)) * 0.4;
        const starPos = new THREE.Vector3(star.x * 10, star.y * 10, star.z * 10);

        // Inner hot-zone ring (orange)
        const hotGeo = new THREE.RingGeometry(baseInner * 0.5, baseInner, 48);
        const hotMat = new THREE.MeshBasicMaterial({ color: 0xff6600, transparent: true, opacity: 0.35, side: THREE.DoubleSide });
        const hotRing = new THREE.Mesh(hotGeo, hotMat);
        hotRing.rotation.x = -Math.PI / 2;
        hotRing.position.copy(starPos);
        this.habitableZoneGroup.add(hotRing);

        // Habitable zone ring (green)
        const hzGeo = new THREE.RingGeometry(baseInner, baseOuter, 48);
        const hzMat = new THREE.MeshBasicMaterial({ color: 0x00cc44, transparent: true, opacity: 0.3, side: THREE.DoubleSide });
        const hzRing = new THREE.Mesh(hzGeo, hzMat);
        hzRing.rotation.x = -Math.PI / 2;
        hzRing.position.copy(starPos);
        this.habitableZoneGroup.add(hzRing);

        // Outer cold-zone ring (blue)
        const coldGeo = new THREE.RingGeometry(baseOuter, baseOuter * 1.5, 48);
        const coldMat = new THREE.MeshBasicMaterial({ color: 0x4488ff, transparent: true, opacity: 0.2, side: THREE.DoubleSide });
        const coldRing = new THREE.Mesh(coldGeo, coldMat);
        coldRing.rotation.x = -Math.PI / 2;
        coldRing.position.copy(starPos);
        this.habitableZoneGroup.add(coldRing);
    }

    // ── Constellation lines ───────────────────────────────────────────────────

    async loadConstellations() {
        console.log('✨ loadConstellations called...');
        try {
            const resp = await fetch('/static/data/constellation_lines.json');
            const data = await resp.json();
            this.createConstellationsOverlay(data);
            return true;
        } catch (e) {
            console.warn('✨ loadConstellations failed:', e);
            return false;
        }
    }

    createConstellationsOverlay(constellations) {
        while (this.constellationsGroup.children.length > 0) {
            const child = this.constellationsGroup.children[0];
            this.constellationsGroup.remove(child);
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
        }

        // Build HIP → star lookup
        const hipMap = new Map();
        for (const star of this.currentStars) {
            if (star.hip) hipMap.set(Math.round(star.hip), star);
        }

        const lineMat = new THREE.LineBasicMaterial({
            color: 0x334488,
            transparent: true,
            opacity: 0.6,
        });

        let drawnLines = 0;
        for (const con of constellations) {
            for (const [hipA, hipB] of con.pairs) {
                const starA = hipMap.get(hipA);
                const starB = hipMap.get(hipB);
                if (!starA || !starB) continue;
                const pts = [
                    new THREE.Vector3(starA.x * 10, starA.y * 10, starA.z * 10),
                    new THREE.Vector3(starB.x * 10, starB.y * 10, starB.z * 10),
                ];
                const geo = new THREE.BufferGeometry().setFromPoints(pts);
                const line = new THREE.Line(geo, lineMat.clone());
                line.userData = { type: 'constellation_line', constellation: con.name };
                this.constellationsGroup.add(line);
                drawnLines++;
            }
        }
        console.log(`✅ Constellation overlay: ${drawnLines} lines from ${constellations.length} constellations`);
    }

    // ── Compare Two Nations ───────────────────────────────────────────────────

    /**
     * Filter stars to show nation1 AND nation2 at full brightness,
     * everything else dimmed.  Pass null for either to clear that slot.
     */
    filterByNations(nationId1, nationId2) {
        if (!nationId1 && !nationId2) {
            this.nationFilter  = null;
            this.nationFilter2 = null;
            this.nationFilterId  = null;
            this.nationFilterId2 = null;
        } else {
            const resolve = (id) => {
                if (!id) return null;
                const n = this.nations.find(n => (n._id || n.id) === id);
                if (!n) return null;
                return new Set((n.territories || []).map(t => t.star_id ?? t));
            };
            this.nationFilter  = resolve(nationId1);
            this.nationFilter2 = resolve(nationId2);
            this.nationFilterId  = this.nationFilter  ? nationId1 : null;
            this.nationFilterId2 = this.nationFilter2 ? nationId2 : null;
        }
        this._recomputeFilter();
    }

    dispose() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.starField) {
            while (this.starField.children.length > 0) {
                const child = this.starField.children[0];
                this.starField.remove(child);
                if (child.geometry) child.geometry.dispose();
                if (child.material) child.material.dispose();
            }
        }
    }

    setVisible(visible) {
        if (this.starField) {
            this.starField.visible = visible;
        }
        if (this.renderer && this.renderer.domElement) {
            this.renderer.domElement.style.display = visible ? 'block' : 'none';
        }
    }

    resize() {
        if (!this.container || !this.renderer || !this.camera) return;
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.renderer.setSize(width, height);
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
    }
}

// Export as both ES6 module and global (for compatibility)
export { ThreeJSStarmap };

// Also make available globally for HTML script access
if (typeof window !== 'undefined') {
    window.ThreeJSStarmap = ThreeJSStarmap;
}
