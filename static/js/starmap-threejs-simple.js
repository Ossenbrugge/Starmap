/**
 * Three.js Starmap Implementation - Simplified Version
 * Cinematic 3D starmap with particles, spheres, and VR compatibility
 */

class ThreeJSStarmap {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.starField = null;
        this.exoplanetGroup = null;
        this.regionGroup = null;
        this.currentStars = [];
        this.exoplanets = [];
        this.regions = [];
        this.selectedStar = null;
        this.raycaster = null;
        this.mouse = null;
        this.container = null;
        this.isVREnabled = false;
        this.animationId = null;
        
        // Check if Three.js is loaded
        if (typeof THREE === 'undefined') {
            console.error('Three.js not loaded');
            return;
        }
        
        this.init();
    }
    
    init() {
        console.log('Initializing Three.js starmap...');
        
        this.container = document.getElementById('threejs-container');
        if (!this.container) {
            console.error('Three.js container not found');
            return false;
        }
        
        console.log('Container found:', this.container);
        console.log('Container dimensions:', this.container.clientWidth, 'x', this.container.clientHeight);
        
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        this.setupScene();
        this.setupCamera();
        this.setupRenderer();
        this.setupControls();
        this.setupLighting();
        this.setupEventListeners();
        
        // Add a test cube to verify Three.js is working (comment out for production)
        // this.addTestCube();
        
        this.animate();
        console.log('✅ Three.js starmap initialized');
        return true;
    }
    
    addTestCube() {
        // Add a test cube to make sure Three.js is working
        const geometry = new THREE.BoxGeometry(5, 5, 5);
        const material = new THREE.MeshBasicMaterial({ color: 0xff0000, wireframe: true });
        const cube = new THREE.Mesh(geometry, material);
        cube.position.set(0, 0, 0);
        this.scene.add(cube);
        console.log('Test cube added at origin');
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000011);
        this.scene.fog = new THREE.Fog(0x000011, 50, 300);
        
        // Create groups for organization
        this.starField = new THREE.Group();
        this.exoplanetGroup = new THREE.Group();
        this.regionGroup = new THREE.Group();
        
        this.scene.add(this.starField);
        this.scene.add(this.exoplanetGroup);
        this.scene.add(this.regionGroup);
    }
    
    setupCamera() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 2000);
        // Position camera much further back for full galaxy view
        this.camera.position.set(200, 150, 200);
        this.camera.lookAt(0, 0, 0);
        console.log('Camera setup for full galaxy view:', this.camera.position, 'aspect:', aspect);
    }
    
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Clear any existing canvas elements
        while (this.container.firstChild) {
            this.container.removeChild(this.container.firstChild);
        }
        
        this.container.appendChild(this.renderer.domElement);
        console.log('Renderer setup complete, canvas added to container');
        console.log('Canvas dimensions:', this.renderer.domElement.width, 'x', this.renderer.domElement.height);
    }
    
    setupControls() {
        // Check if OrbitControls is available
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        } else {
            console.warn('OrbitControls not available, using basic controls');
            return;
        }
        
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.1;
        this.controls.minDistance = 10;
        this.controls.maxDistance = 1000;
        this.controls.enablePan = true;
        this.controls.target.set(0, 0, 0);
    }
    
    setupLighting() {
        // Ambient light for general illumination
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        
        // Directional light from galactic core
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.2);
        directionalLight.position.set(0, 10, 0);
        directionalLight.castShadow = false;
        this.scene.add(directionalLight);
    }
    
    setupEventListeners() {
        // Mouse events for star selection
        this.renderer.domElement.addEventListener('click', (event) => {
            this.onMouseClick(event);
        });
        
        // Window resize
        window.addEventListener('resize', () => {
            this.onWindowResize();
        });
    }
    
    onMouseClick(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        // Check for star intersections
        const starIntersects = this.raycaster.intersectObjects(this.starField.children);
        if (starIntersects.length > 0) {
            const starMesh = starIntersects[0].object;
            const starData = starMesh.userData.starData;
            if (starData && window.app && window.app.selectStar) {
                window.app.selectStar(starData);
            }
        }
    }
    
    onWindowResize() {
        if (!this.container) return;
        
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
    
    createStars(stars) {
        console.log('🌟 Creating Three.js ParticleSystem with', stars.length, 'stars');
        console.log('📊 Sample star data:', stars[0]);
        
        // Clear existing stars
        this.starField.clear();
        this.currentStars = stars;
        
        // Filter valid stars
        const validStars = stars.filter(star => 
            star.x != null && star.y != null && star.z != null &&
            !isNaN(star.x) && !isNaN(star.y) && !isNaN(star.z)
        );
        
        console.log(`✅ Filtered to ${validStars.length} valid stars for ParticleSystem`);
        
        if (validStars.length === 0) {
            console.error('❌ No valid stars found!');
            return;
        }
        
        console.log('📍 First star position:', validStars[0].x, validStars[0].y, validStars[0].z);
        console.log('📍 Last star position:', validStars[validStars.length-1].x, validStars[validStars.length-1].y, validStars[validStars.length-1].z);
        
        // Create ParticleSystem for performance with 24k+ stars
        this.createParticleSystem(validStars);
        
        // Also create individual meshes for special stars (fictional, Sol, etc.)
        this.createSpecialStars(validStars);
        
        console.log(`🚀 Created ParticleSystem with ${validStars.length} stars`);
        console.log('📦 StarField children count:', this.starField.children.length);
    }
    
    createParticleSystem(stars) {
        console.log('🎯 Creating ParticleSystem for', stars.length, 'stars');
        
        // Create arrays for particle attributes
        const positions = new Float32Array(stars.length * 3);
        const colors = new Float32Array(stars.length * 3);
        const sizes = new Float32Array(stars.length);
        
        // Fill arrays with star data
        stars.forEach((star, i) => {
            const i3 = i * 3;
            
            // Positions (convert coordinate system)
            positions[i3] = star.x;
            positions[i3 + 1] = star.z;
            positions[i3 + 2] = -star.y;
            
            // Colors based on spectral class
            const color = new THREE.Color(this.getStarColor(star));
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
            
            // Size based on magnitude - MUCH LARGER (10x bump)
            sizes[i] = Math.max(5, this.getStarSize(star) * 2.0); // 10x larger than before
        });
        
        // Create BufferGeometry
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        // Create custom shader material for better performance
        const material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0 }
            },
            vertexShader: `
                attribute float size;
                attribute vec3 color;
                varying vec3 vColor;
                uniform float time;
                
                void main() {
                    vColor = color;
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    
                    // Add subtle twinkling effect
                    float twinkle = sin(time * 2.0 + position.x * 10.0) * 0.2 + 0.8;
                    gl_PointSize = size * twinkle * (100.0 / -mvPosition.z);
                    gl_Position = projectionMatrix * mvPosition;
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                
                void main() {
                    float distance = length(gl_PointCoord - vec2(0.5));
                    if (distance > 0.5) discard;
                    
                    // Create circular star with soft edges
                    float alpha = 1.0 - smoothstep(0.2, 0.5, distance);
                    gl_FragColor = vec4(vColor, alpha);
                }
            `,
            transparent: true,
            vertexColors: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        
        // Create Points object (ParticleSystem)
        const particles = new THREE.Points(geometry, material);
        particles.name = 'StarParticleSystem';
        this.starField.add(particles);
        
        console.log('✨ ParticleSystem created with', stars.length, 'star particles');
    }
    
    createSpecialStars(stars) {
        console.log('⭐ Creating special star meshes for interactivity');
        
        // Find special stars
        const specialStars = stars.filter(star => 
            star.name === 'Sol' || 
            star.id === 0 ||
            star.fictional_name === 'Tiefe-Grenze Tor' ||
            star.id === 999999 ||
            star.is_fictional ||
            star.has_planets ||
            star.exoplanet_count > 0
        );
        
        console.log(`🌟 Found ${specialStars.length} special stars for individual meshes`);
        
        specialStars.forEach((star, index) => {
            this.createSpecialStar(star, index);
        });
    }
    
    createSpecialStar(star, index) {
        // Create larger spheres for special stars that can be clicked
        const starSize = Math.max(2, this.getStarSize(star) * 0.5);
        const geometry = new THREE.SphereGeometry(starSize, 12, 8);
        const color = this.getStarColor(star);
        
        const material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.8,
        });
        
        // Strong emissive glow for special stars
        material.emissive = new THREE.Color(color);
        material.emissiveIntensity = 0.6;
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(star.x, star.z, -star.y);
        mesh.userData.starData = star;
        mesh.userData.starIndex = index;
        mesh.name = `SpecialStar_${star.name || star.fictional_name || star.id}`;
        
        // Add extra glow for fictional stars
        if (star.is_fictional || star.fictional_name) {
            this.addStarGlow(mesh, color);
        }
        
        this.starField.add(mesh);
    }
    
    // Old createStar method removed - now using ParticleSystem for performance
    
    addStarGlow(starMesh, color) {
        // Create larger sphere for glow effect
        const glowGeometry = new THREE.SphereGeometry(starMesh.geometry.parameters.radius * 2, 8, 6);
        const glowMaterial = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.2,
            blending: THREE.AdditiveBlending
        });
        
        const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
        starMesh.add(glowMesh);
    }
    
    createExoplanets(exoplanets) {
        console.log('Creating Three.js exoplanets:', exoplanets.length);
        
        // Clear existing exoplanets
        this.exoplanetGroup.clear();
        this.exoplanets = exoplanets;
        
        // Group exoplanets by host star
        const exoplanetsByHost = {};
        exoplanets.forEach(planet => {
            const hostStar = planet.host_star;
            if (!exoplanetsByHost[hostStar]) {
                exoplanetsByHost[hostStar] = [];
            }
            exoplanetsByHost[hostStar].push(planet);
        });
        
        Object.keys(exoplanetsByHost).forEach(hostName => {
            this.createPlanetarySystem(hostName, exoplanetsByHost[hostName]);
        });
    }
    
    createPlanetarySystem(hostName, planets) {
        // Find host star
        const hostStar = this.currentStars.find(star => 
            star.name === hostName || star.fictional_name === hostName
        );
        
        if (!hostStar) return;
        
        const systemGroup = new THREE.Group();
        systemGroup.position.set(hostStar.x, hostStar.z, -hostStar.y);
        
        planets.forEach((planet, index) => {
            // Create planet sphere
            const radius = this.getPlanetRadius(planet);
            const geometry = new THREE.SphereGeometry(radius, 16, 12);
            
            const color = this.getPlanetColor(planet);
            const material = new THREE.MeshPhongMaterial({
                color: color,
                transparent: true,
                opacity: 0.8
            });
            
            // Add glow for fictional planets
            if (planet.fictional) {
                material.emissive = new THREE.Color(color);
                material.emissiveIntensity = 0.3;
            }
            
            const planetMesh = new THREE.Mesh(geometry, material);
            
            // Position planet in orbit
            const orbitRadius = this.getOrbitRadius(planet, index);
            const angle = (index / planets.length) * Math.PI * 2;
            planetMesh.position.set(
                Math.cos(angle) * orbitRadius,
                0,
                Math.sin(angle) * orbitRadius
            );
            
            planetMesh.userData.planetData = planet;
            planetMesh.userData.orbitRadius = orbitRadius;
            planetMesh.userData.orbitAngle = angle;
            
            // Create orbit ring
            this.createOrbitRing(systemGroup, orbitRadius, color);
            
            systemGroup.add(planetMesh);
        });
        
        this.exoplanetGroup.add(systemGroup);
    }
    
    createOrbitRing(parent, radius, color) {
        const geometry = new THREE.RingGeometry(radius - 0.05, radius + 0.05, 32);
        const material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });
        
        const ring = new THREE.Mesh(geometry, material);
        ring.rotation.x = Math.PI / 2;
        parent.add(ring);
    }
    
    createRegionBoxes(regions) {
        console.log('Creating Three.js regions:', regions.length);
        
        // Clear existing regions
        this.regionGroup.clear();
        this.regions = regions;
        
        regions.forEach(region => {
            this.createRegionBox(region);
        });
    }
    
    createRegionBox(region) {
        const x_size = region.x_range[1] - region.x_range[0];
        const y_size = region.y_range[1] - region.y_range[0];
        const z_size = region.z_range[1] - region.z_range[0];
        
        const geometry = new THREE.BoxGeometry(x_size, z_size, y_size);
        const material = new THREE.MeshBasicMaterial({
            color: region.color,
            transparent: true,
            opacity: 0.1,
            wireframe: false
        });
        
        const box = new THREE.Mesh(geometry, material);
        
        // Position at region center
        box.position.set(
            region.center[0],
            region.center[2],
            -region.center[1]
        );
        
        // Add wireframe outline
        const wireframeGeometry = new THREE.EdgesGeometry(geometry);
        const wireframeMaterial = new THREE.LineBasicMaterial({ 
            color: region.color,
            transparent: true,
            opacity: 0.5
        });
        const wireframe = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);
        box.add(wireframe);
        
        box.userData.regionData = region;
        this.regionGroup.add(box);
    }
    
    getStarColor(star) {
        // Fictional stars get special color
        if (star.is_fictional) {
            return '#ff6b6b';
        }
        
        // Stars with exoplanets
        if (star.has_planets || star.exoplanet_count > 0) {
            return '#4ecdc4';
        }
        
        // Color by spectral type
        const spectralClass = star.spectral_class || '';
        const spectral = spectralClass.length > 0 ? spectralClass[0].toUpperCase() : 'G';
        const colors = {
            'O': '#9bb0ff', 'B': '#aabfff', 'A': '#cad7ff',
            'F': '#f8f7ff', 'G': '#fff4ea', 'K': '#ffd2a1', 'M': '#ffad51'
        };
        return colors[spectral] || '#fff4ea';
    }
    
    getStarSize(star) {
        // Special handling for Sol
        if (star.name === 'Sol' || star.id === 0) {
            return 15;
        }
        
        // Special handling for important fictional stars
        if (star.fictional_name === 'Tiefe-Grenze Tor' || star.id === 999999) {
            return 12;
        }
        
        // Make fictional stars more prominent
        if (star.is_fictional) {
            return 10;
        }
        
        // Stars with exoplanets are slightly larger
        if (star.has_planets || star.exoplanet_count > 0) {
            const mag = star.magnitude || 8.0;
            return Math.max(4, Math.min(12, 17 - mag * 2));
        }
        
        // Convert magnitude to size
        const mag = star.magnitude || 8.0;
        return Math.max(2, Math.min(12, 15 - mag * 2));
    }
    
    getPlanetRadius(planet) {
        const earthRadii = planet.radius || planet.planet_radius_earth || 1;
        return Math.max(0.2, Math.min(2, earthRadii * 0.5));
    }
    
    getPlanetColor(planet) {
        if (planet.fictional) {
            return '#00ff88'; // Bright green for fictional
        }
        
        if (planet.potentially_habitable) {
            return '#2196F3'; // Blue for habitable
        }
        
        const temp = planet.equilibrium_temperature || planet.equilibrium_temperature_k || 280;
        if (temp > 373) {
            return '#FF5722'; // Red for hot
        } else if (temp < 273) {
            return '#9C27B0'; // Purple for cold
        }
        
        return '#4CAF50'; // Green default
    }
    
    getOrbitRadius(planet, index) {
        const orbit = planet.orbit || planet.semi_major_axis || (index + 1) * 2;
        return Math.max(1, Math.min(10, Math.log(orbit + 1) * 2));
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        this.render();
    }
    
    render() {
        if (this.controls) {
            this.controls.update();
        }
        
        // Update particle system time for twinkling
        const particleSystem = this.starField.getObjectByName('StarParticleSystem');
        if (particleSystem && particleSystem.material.uniforms) {
            particleSystem.material.uniforms.time.value = Date.now() * 0.001;
        }
        
        // Animate planet orbits
        this.exoplanetGroup.children.forEach(systemGroup => {
            systemGroup.children.forEach(planetMesh => {
                if (planetMesh.userData.orbitRadius && planetMesh.userData.orbitAngle !== undefined) {
                    planetMesh.userData.orbitAngle += 0.01;
                    const radius = planetMesh.userData.orbitRadius;
                    const angle = planetMesh.userData.orbitAngle;
                    planetMesh.position.set(
                        Math.cos(angle) * radius,
                        0,
                        Math.sin(angle) * radius
                    );
                }
            });
        });
        
        this.renderer.render(this.scene, this.camera);
        
        // Debug info every 120 frames (every 2 seconds at 60fps)
        if (this.frameCount === undefined) this.frameCount = 0;
        this.frameCount++;
        if (this.frameCount % 120 === 0) {
            console.log(`🎬 Frame ${this.frameCount}: Scene children: ${this.scene.children.length}, StarField children: ${this.starField.children.length}`);
        }
    }
    
    setVisible(visible) {
        if (this.container) {
            this.container.style.display = visible ? 'block' : 'none';
        }
    }
    
    resize() {
        this.onWindowResize();
    }
    
    dispose() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.renderer) {
            this.renderer.dispose();
        }
        if (this.controls) {
            this.controls.dispose();
        }
    }
}

// Export for use in main starmap
window.ThreeJSStarmap = ThreeJSStarmap;