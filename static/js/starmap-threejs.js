/**
 * Three.js Starmap Implementation
 * Cinematic 3D starmap with particles, spheres, and VR compatibility
 */

// Import Three.js modules dynamically
let THREE, OrbitControls, VRButton;

async function loadThreeJS() {
    if (!THREE) {
        THREE = await import('https://unpkg.com/three@0.158.0/build/three.module.js');
        const orbitControlsModule = await import('https://unpkg.com/three@0.158.0/examples/jsm/controls/OrbitControls.js');
        OrbitControls = orbitControlsModule.OrbitControls;
        const vrButtonModule = await import('https://unpkg.com/three@0.158.0/examples/jsm/webxr/VRButton.js');
        VRButton = vrButtonModule.VRButton;
    }
    return { THREE, OrbitControls, VRButton };
}

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
        
        this.initAsync();
    }
    
    async initAsync() {
        await loadThreeJS();
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.init();
    }
    
    init() {
        this.container = document.getElementById('threejs-container');
        if (!this.container) {
            console.error('Three.js container not found');
            return;
        }
        
        this.setupScene();
        this.setupCamera();
        this.setupRenderer();
        this.setupControls();
        this.setupLighting();
        this.setupEventListeners();
        this.setupVR();
        
        this.animate();
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
        this.camera = new THREE.PerspectiveCamera(
            75,
            this.container.clientWidth / this.container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(30, 20, 30);
    }
    
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.xr.enabled = true;
        
        this.container.appendChild(this.renderer.domElement);
    }
    
    setupControls() {
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.1;
        this.controls.minDistance = 5;
        this.controls.maxDistance = 200;
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
    
    setupVR() {
        // Add VR button
        const vrButton = VRButton.createButton(this.renderer);
        vrButton.style.position = 'absolute';
        vrButton.style.bottom = '20px';
        vrButton.style.right = '20px';
        vrButton.style.zIndex = '1000';
        this.container.appendChild(vrButton);
        
        // VR session handlers
        this.renderer.xr.addEventListener('sessionstart', () => {
            this.isVREnabled = true;
            console.log('VR session started');
        });
        
        this.renderer.xr.addEventListener('sessionend', () => {
            this.isVREnabled = false;
            console.log('VR session ended');
        });
    }
    
    setupEventListeners() {
        // Mouse events for star selection
        this.renderer.domElement.addEventListener('click', (event) => {
            this.onMouseClick(event);
        });
        
        this.renderer.domElement.addEventListener('mousemove', (event) => {
            this.onMouseMove(event);
        });
        
        // Window resize
        window.addEventListener('resize', () => {
            this.onWindowResize();
        });
    }
    
    onMouseClick(event) {
        if (this.isVREnabled) return;
        
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
        
        // Check for exoplanet intersections
        const planetIntersects = this.raycaster.intersectObjects(this.exoplanetGroup.children, true);
        if (planetIntersects.length > 0) {
            const planetMesh = planetIntersects[0].object;
            const planetData = planetMesh.userData.planetData;
            if (planetData) {
                this.showPlanetDetails(planetData);
            }
        }
    }
    
    onMouseMove(event) {
        if (this.isVREnabled) return;
        
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        // Optional: Add hover effects
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects([...this.starField.children, ...this.exoplanetGroup.children], true);
        
        // Reset all hover states
        this.resetHoverStates();
        
        if (intersects.length > 0) {
            const object = intersects[0].object;
            this.setHoverState(object, true);
        }
    }
    
    onWindowResize() {
        if (!this.container) return;
        
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
    
    resetHoverStates() {
        this.starField.children.forEach(star => {
            if (star.userData.originalScale) {
                star.scale.copy(star.userData.originalScale);
            }
        });
        
        this.exoplanetGroup.children.forEach(group => {
            group.children.forEach(planet => {
                if (planet.userData.originalScale) {
                    planet.scale.copy(planet.userData.originalScale);
                }
            });
        });
    }
    
    setHoverState(object, isHovered) {
        if (!object.userData.originalScale) {
            object.userData.originalScale = object.scale.clone();
        }
        
        if (isHovered) {
            object.scale.multiplyScalar(1.5);
        } else {
            object.scale.copy(object.userData.originalScale);
        }
    }
    
    createStars(stars) {
        console.log('Creating Three.js stars:', stars.length);
        
        // Clear existing stars
        this.starField.clear();
        this.currentStars = stars;
        
        // Filter valid stars
        const validStars = stars.filter(star => 
            star.x != null && star.y != null && star.z != null &&
            !isNaN(star.x) && !isNaN(star.y) && !isNaN(star.z)
        );
        
        // Create star particles using BufferGeometry for performance
        const positions = [];
        const colors = [];
        const sizes = [];
        
        // Also create individual meshes for interaction
        validStars.forEach((star, index) => {
            // Add to particle system
            positions.push(star.x, star.z, -star.y); // Adjust coordinate system
            
            const color = this.getStarColor(star);
            const colorObj = new THREE.Color(color);
            colors.push(colorObj.r, colorObj.g, colorObj.b);
            
            const size = this.getStarSize(star);
            sizes.push(size);
            
            // Create individual mesh for interaction
            this.createInteractableStar(star, index);
        });
        
        // Create particle system
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1));
        
        // Custom shader material for particles
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
                    
                    // Add subtle twinkling
                    float twinkle = sin(time * 2.0 + position.x * 10.0) * 0.1 + 0.9;
                    gl_PointSize = size * twinkle * (300.0 / -mvPosition.z);
                    gl_Position = projectionMatrix * mvPosition;
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                
                void main() {
                    float distance = length(gl_PointCoord - vec2(0.5));
                    if (distance > 0.5) discard;
                    
                    float alpha = 1.0 - distance * 2.0;
                    gl_FragColor = vec4(vColor, alpha);
                }
            `,
            transparent: true,
            vertexColors: true,
            blending: THREE.AdditiveBlending
        });
        
        const particles = new THREE.Points(geometry, material);
        this.starField.add(particles);
        
        console.log(`Created ${validStars.length} Three.js stars`);
    }
    
    createInteractableStar(star, index) {
        const geometry = new THREE.SphereGeometry(this.getStarSize(star) * 0.5, 8, 6);
        const color = this.getStarColor(star);
        
        const material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0, // Invisible but clickable
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(star.x, star.z, -star.y);
        mesh.userData.starData = star;
        mesh.userData.starIndex = index;
        
        this.starField.add(mesh);
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
                this.addGlowEffect(material, color);
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
    
    addGlowEffect(material, color) {
        material.emissive = new THREE.Color(color);
        material.emissiveIntensity = 0.3;
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
    
    showPlanetDetails(planet) {
        console.log('Planet clicked:', planet);
        // Show planet details in UI
        if (window.app && window.app.showPlanetDetails) {
            window.app.showPlanetDetails(planet);
        }
    }
    
    animate() {
        if (this.renderer.xr.isPresenting) {
            this.renderer.setAnimationLoop(() => this.render());
        } else {
            requestAnimationFrame(() => this.animate());
            this.render();
        }
    }
    
    render() {
        if (this.controls && !this.isVREnabled) {
            this.controls.update();
        }
        
        // Update particle system time for twinkling
        if (this.starField.children[0] && this.starField.children[0].material.uniforms) {
            this.starField.children[0].material.uniforms.time.value = Date.now() * 0.001;
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