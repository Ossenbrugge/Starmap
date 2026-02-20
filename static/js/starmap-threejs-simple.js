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
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
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
                x: parseFloat(star.x) || 0,
                y: parseFloat(star.y) || 0,
                z: parseFloat(star.z) || 0,
                magnitude: parseFloat(star.magnitude || star.mag) || 8.0,
                spectral_class: star.spectral_class || star.spect || 'G2V',
                constellation: star.con || star.constellation,
                distance: parseFloat(star.distance || star.dist) || 10.0,
                catalog_ids: this.buildCatalogIds(star),
                is_fictional: true,
                fictional_description: this.generateFictionalDescription(starName)
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

    generateFictionalDescription(starName) {
        if (starName.includes('Tiefe-Grenze')) {
            return 'Tiefe-Grenze Tor serves as the gateway to deep space exploration.';
        }
        return 'A frontier system in the Felgenland Saga universe.';
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

        const positions  = new Float32Array(validStars.length * 3);
        const magnitudes = new Float32Array(validStars.length);
        const colors     = new Float32Array(validStars.length * 3);

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
        });

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position',  new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('magnitude', new THREE.Float32BufferAttribute(magnitudes, 1));
        geometry.setAttribute('starColor', new THREE.Float32BufferAttribute(colors, 3));

        // ── GPU Shader (LOD + spectral colours, no texture uploads on filter) ──
        const vertexShader = `
            attribute float magnitude;
            attribute vec3  starColor;
            uniform float   uMagLimit;
            uniform float   uCameraDistance;
            varying vec3    vColor;
            varying float   vAlpha;

            void main() {
                vColor = starColor;

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

            void main() {
                vec2  coord = gl_PointCoord - 0.5;
                float dist  = length(coord);
                if (dist > 0.5) discard;
                float alpha = smoothstep(0.5, 0.0, dist) * vAlpha;
                if (alpha < 0.01) discard;
                gl_FragColor = vec4(vColor, alpha);
            }
        `;

        const initialMag = parseFloat(document.getElementById('magLimit')?.value ?? '8');

        this.starMaterial = new THREE.ShaderMaterial({
            vertexShader,
            fragmentShader,
            uniforms: {
                uMagLimit:       { value: initialMag },
                uCameraDistance: { value: 10.0 },
            },
            transparent: true,
            depthWrite: false,
        });

        const points = new THREE.Points(geometry, this.starMaterial);
        this.starField.add(points);
        console.log(`Created ${validStars.length} stars with GPU shader LOD`);
    }

    setupStarInteraction() {
        this.raycaster = new THREE.Raycaster();
        this.raycaster.params.Points.threshold = 0.5;
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
                }
            }
        }
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

        const starName = star.fictional_name || star.name || 'Unknown Star';
        const primaryName = star.name || star.fictional_name || 'Unknown Star';

        let html = `
            <h6 class="text-primary">${starName}</h6>
            ${starName !== primaryName ? `<p class="small text-muted">${primaryName}</p>` : ''}

            <div class="row">
                <div class="col-6">
                    <strong>Magnitude:</strong><br>
                    <span class="text-info">${star.magnitude ? star.magnitude.toFixed(2) : 'Unknown'}</span>
                </div>
                <div class="col-6">
                    <strong>Spectral Class:</strong><br>
                    <span class="text-warning">${star.spectral_class || 'Unknown'}</span>
                </div>
            </div>

            <div class="row mt-2">
                <div class="col-6">
                    <strong>Distance:</strong><br>
                    <span class="text-success">${star.distance ? star.distance.toFixed(1) + ' pc' : 'Unknown'}</span>
                </div>
                <div class="col-6">
                    <strong>Constellation:</strong><br>
                    <span class="text-success">${star.constellation || 'Unknown'}</span>
                </div>
            </div>

            <div class="mt-3">
                <strong>Galactic Coordinates:</strong><br>
                <small class="text-muted">
                    X: ${star.x ? star.x.toFixed(2) : 'Unknown'}<br>
                    Y: ${star.y ? star.y.toFixed(2) : 'Unknown'}<br>
                    Z: ${star.z ? star.z.toFixed(2) : 'Unknown'}
                </small>
            </div>

            <div class="mt-3">
                <strong>Star ID:</strong><br>
                <small class="text-muted">${star.id || 'Unknown'}</small>
            </div>
        `;

        if (star.fictional_name && star.fictional_description) {
            html += `
                <div class="mt-3 p-2 bg-light bg-opacity-25 rounded">
                    <strong>Fictional Universe:</strong><br>
                    <small class="text-muted">${star.fictional_description}</small>
                </div>
            `;
        }

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
        console.log('✨ Highlighted star:', star.fictional_name || star.name);
    }

    clearStarHighlights() {
        const highlights = [];
        this.scene.children.forEach(child => {
            if (child.userData && child.userData.type === 'star_highlight') {
                highlights.push(child);
            }
        });

        highlights.forEach(highlight => {
            this.scene.remove(highlight);
            if (highlight.geometry) highlight.geometry.dispose();
            if (highlight.material) highlight.material.dispose();
        });
    }

    showStarTooltip(star, event) {

        let tooltip = document.getElementById('starTooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'starTooltip';
            tooltip.style.cssText = `
                position: fixed;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                z-index: 1000;
                border: 1px solid #333;
            `;
            document.body.appendChild(tooltip);
        }

        const starName = star.fictional_name || star.name || 'Unknown Star';
        const magnitude = star.magnitude ? star.magnitude.toFixed(2) : 'Unknown';
        const spectral = star.spectral_class || 'Unknown';

        tooltip.innerHTML = `<strong>${starName}</strong><br>Mag: ${magnitude} | Type: ${spectral}`;

        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY + 10) + 'px';
        tooltip.style.display = 'block';

        clearTimeout(this.tooltipTimeout);
        this.tooltipTimeout = setTimeout(() => {
            if (tooltip) tooltip.style.display = 'none';
        }, 2000);
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

    // Overlay Loading Methods
    async loadNations() {
        console.log('🏛️ loadNations called - loading nations overlay...');
        try {
            const response = await fetch('/api/v1/nations');
            const data = await response.json();

            if (data.success && data.data) {
                console.log(`🎯 Creating nations for ${data.data.length} nations`);
                this.createNationsOverlay(data.data);
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
        // Create a sphere around single star with larger radius
        let sphereRadius = 3.0; // Increased base radius
        
        // Special handling for specific nations to show their greater influence
        if (nation._id === 'protelani_republic' || nation._id === 'dorsai_republic') {
            sphereRadius *= 2.0; // Double the sphere size for these nations
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
        this.createStarConnections(nationStars, color);
    }

    createStarConnections(stars, color) {
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
                line.userData = { type: 'nation_connection' };
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
                    const color = route.route_type === 'Primary Trade' ? 0x00ff00 : 0x888888;
                    const material = new THREE.LineBasicMaterial({
                        color: color,
                        transparent: true,
                        opacity: 0.7
                    });

                    const line = new THREE.Line(geometry, material);
                    line.userData = { type: 'trade_route', data: route };

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
        console.log('🪐 loadExoplanets called - loading exoplanets overlay...');
        try {
            const response = await fetch('/api/v1/exoplanets');
            const data = await response.json();

            if (data.success && data.data) {
                console.log(`🎯 Creating exoplanets for ${data.data.length} planets`);
                this.createExoplanetsOverlay(data.data);
                return true;
            }
            return false;
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

        this.render();
    }

    render() {
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
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
