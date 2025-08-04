/**
 * Three.js Starmap Implementation - Essential Version
 * Core 3D starmap with mouse navigation and star selection
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

class ThreeJSStarmap {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.starField = null;
        this.exoplanetGroup = null;
        this.fictionalExoplanetGroup = null;
        this.stellarRegionsGroup = null;
        this.nationsGroup = null;
        this.nationalBordersGroup = null;
        this.tradeRoutesGroup = null;
        this.currentStars = [];
        this.exoplanets = [];
        this.selectedStar = null;
        this.axisLabels = [];
        this.raycaster = null;
        this.mouse = null;
        this.container = null;
        this.animationId = null;
        
        if (typeof THREE === 'undefined') {
            console.error('❌ Three.js not loaded');
            return;
        }
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Three.js starmap...');
        
        this.container = document.getElementById('threejs-container');
        if (!this.container) {
            console.error('❌ Three.js container not found');
            return false;
        }
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        if (width <= 0 || height <= 0) {
            this.container.style.width = '800px';
            this.container.style.height = '600px';
        }
        
        try {
            this.raycaster = new THREE.Raycaster();
            this.mouse = new THREE.Vector2();
            
            this.setupScene();
            this.setupCamera();
            this.setupRenderer();
            this.setupControls();
            this.setupLighting();
            this.setupEventListeners();
            
            // Load stars first, then other data that depends on stars
            this.loadStars().then(() => {
                this.loadExoplanets();
                this.loadNations();
                this.loadFictionalExoplanets();
                this.loadTradeRoutes();
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
        
        // Create essential groups
        this.starField = new THREE.Group();
        this.exoplanetGroup = new THREE.Group();
        this.fictionalExoplanetGroup = new THREE.Group();
        this.stellarRegionsGroup = new THREE.Group();
        this.nationsGroup = new THREE.Group();
        this.nationalBordersGroup = new THREE.Group();
        this.tradeRoutesGroup = new THREE.Group();
        
        // OCTANTS START HIDDEN - set stellarRegionsGroup visibility to false
        this.stellarRegionsGroup.visible = false;
        
        // NATIONAL BORDERS START HIDDEN - set nationalBordersGroup visibility to false
        this.nationalBordersGroup.visible = false;
        
        this.scene.add(this.starField);
        this.scene.add(this.exoplanetGroup);
        this.scene.add(this.fictionalExoplanetGroup);
        this.scene.add(this.stellarRegionsGroup);
        this.scene.add(this.nationsGroup);
        this.scene.add(this.nationalBordersGroup);
        this.scene.add(this.tradeRoutesGroup);
        
        // Trade routes start visible by default
        this.tradeRoutesGroup.visible = true;
        
        // Add galactic direction axes
        this.createGalacticDirections();
        
        console.log('✅ Scene setup complete');
    }
    
    setupCamera() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 10000);
        this.camera.position.z = 10000; // Start much further back for greatly increased scale
        this.camera.lookAt(0, 0, 0);
        
        console.log('✅ Camera setup complete');
    }
    
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        while (this.container.firstChild) {
            this.container.removeChild(this.container.firstChild);
        }
        
        this.container.appendChild(this.renderer.domElement);
        console.log('✅ Renderer setup complete');
    }
    
    setupControls() {
        try {
            this.controls = new OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.25;
            this.controls.minDistance = 0.1; // Allow very close zoom to Sol
            this.controls.maxDistance = 25000; // Increase max distance for much larger scale
            this.controls.enablePan = true;
            this.controls.enableZoom = true;
            this.controls.enableRotate = true;
            this.controls.target.set(0, 0, 0);
            this.controls.update();
            
            console.log('✅ OrbitControls setup complete');
        } catch (error) {
            console.error('❌ Error setting up controls:', error);
        }
    }
    
    setupLighting() {
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.2);
        directionalLight.position.set(0, 10, 0);
        this.scene.add(directionalLight);
        
        console.log('✅ Lighting setup complete');
    }
    
    setupEventListeners() {
        window.addEventListener('resize', () => {
            this.onWindowResize();
        });
        
        // Enhanced mouse events on renderer canvas
        if (this.renderer && this.renderer.domElement) {
            this.renderer.domElement.addEventListener('mousemove', (event) => {
                this.onMouseMove(event);
            }, false);
            
            this.renderer.domElement.addEventListener('mousedown', (event) => {
                this.onMouseDown(event);
            }, false);
            
            this.renderer.domElement.addEventListener('mouseup', (event) => {
                this.onMouseUp(event);
            }, false);
            
            this.renderer.domElement.addEventListener('click', (event) => {
                this.onMouseClick(event);
            }, false);
        }
        
        // Set up raycaster parameters
        this.raycaster.params.Points.threshold = 0.5;
        
        console.log('✅ Event listeners setup complete');
    }
    
    onMouseMove(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    }
    
    onMouseDown(event) {
        // Enhanced mouse down handling for better orbit controls
        if (this.controls) {
            this.controls.handleMouseDown?.(event);
        }
    }
    
    onMouseUp(event) {
        // Enhanced mouse up handling for better orbit controls
        if (this.controls) {
            this.controls.handleMouseUp?.(event);
        }
    }
    
    onMouseClick(_event) {
        if (!this.raycaster || !this.camera || !this.scene) return;
        
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.scene.children, true);
        
        if (intersects.length > 0) {
            const selectedObject = intersects[0].object;
            this.handleStarSelection(selectedObject);
        } else {
            this.clearStarHighlights();
        }
    }
    
    handleStarSelection(selectedObject) {
        if (selectedObject.userData && selectedObject.userData.starData) {
            const starData = selectedObject.userData.starData;
            console.log('🌟 Star selected:', starData.name);
            
            this.clearStarHighlights();
            selectedObject.material.color.setHex(0xff0000);
            this.selectedStar = selectedObject;
            
            // Set orbit controls to center on the selected star
            const scale = 100;
            const starPosition = new THREE.Vector3(
                starData.x * scale,
                starData.y * scale,
                starData.z * scale
            );
            this.controls.target.copy(starPosition);
            this.controls.update();
            
            console.log(`🎯 Orbit target set to ${starData.name} at (${starPosition.x.toFixed(1)}, ${starPosition.y.toFixed(1)}, ${starPosition.z.toFixed(1)})`);
            
            this.showStarInMainWindow(starData);
            return starData;
        }
        return null;
    }
    
    clearStarHighlights() {
        if (this.selectedStar) {
            const starData = this.selectedStar.userData.starData;
            this.selectedStar.material.color = this.getStarColor(starData);
            this.selectedStar = null;
        }
    }
    
    resetOrbitTarget() {
        // Reset orbit controls back to origin (Sol)
        this.controls.target.set(0, 0, 0);
        this.controls.update();
        console.log('🎯 Orbit target reset to origin (Sol)');
    }
    
    async loadStars() {
        try {
            const response = await fetch('/api/stars');
            const data = await response.json();
            
            if (data.success && data.data) {
                this.createStars(data.data);
                return data.data;
            } else if (Array.isArray(data)) {
                this.createStars(data);
                return data;
            }
        } catch (error) {
            console.error('Error loading stars:', error);
            return [];
        }
    }
    
    showStarInMainWindow(starData) {
        const starDetailsPanel = document.getElementById('starDetails');
        if (starDetailsPanel) {
            // Build comprehensive star information including fictional details
            let html = `<h5>${starData.name || starData.fictional_name || 'Unknown Star'}</h5>`;
            
            // Basic information
            html += `<p><strong>ID:</strong> ${starData.id}</p>`;
            html += `<p><strong>Coordinates:</strong> (${starData.x?.toFixed(2)}, ${starData.y?.toFixed(2)}, ${starData.z?.toFixed(2)})</p>`;
            
            // Real vs Fictional
            if (starData.is_fictional) {
                html += `<p><strong>Type:</strong> <span style="color: #ff6b6b;">Fictional Star</span></p>`;
                if (starData.fictional_name) {
                    html += `<p><strong>Fictional Name:</strong> ${starData.fictional_name}</p>`;
                }
                if (starData.fictional_description) {
                    html += `<p><strong>Description:</strong> ${starData.fictional_description}</p>`;
                }
            } else {
                html += `<p><strong>Type:</strong> <span style="color: #4ecdc4;">Real Star</span></p>`;
            }
            
            // Stellar properties
            if (starData.spectral_class) {
                html += `<p><strong>Spectral Class:</strong> ${starData.spectral_class}</p>`;
            }
            if (starData.magnitude !== undefined) {
                html += `<p><strong>Magnitude:</strong> ${starData.magnitude}</p>`;
            }
            if (starData.distance !== undefined) {
                html += `<p><strong>Distance:</strong> ${starData.distance} ly</p>`;
            }
            
            // Planet information - special handling for Sol
            if (starData.name === 'Sol' || starData.id === 500000 || starData.id === 0) {
                html += `<p><strong>Planets:</strong> <span style="color: #4ecdc4;">Yes (8 planets)</span></p>`;
                html += `<p><strong>Known Planets:</strong> Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune</p>`;
                html += `<p><strong>Habitable Zone:</strong> Earth</p>`;
                html += `<p><strong>System Type:</strong> Our Solar System</p>`;
            } else if (starData.has_planets || starData.exoplanet_count > 0) {
                html += `<p><strong>Planets:</strong> <span style="color: #4ecdc4;">Yes (${starData.exoplanet_count || 'Unknown number'})</span></p>`;
            } else {
                html += `<p><strong>Planets:</strong> None known</p>`;
            }
            
            // Fictional universe information
            if (starData.controlling_faction) {
                html += `<p><strong>Controlling Faction:</strong> ${starData.controlling_faction}</p>`;
            }
            if (starData.system_notes) {
                html += `<p><strong>Notes:</strong> ${starData.system_notes}</p>`;
            }
            
            starDetailsPanel.innerHTML = html;
            starDetailsPanel.style.display = 'block';
        }
    }
    
    createStars(stars) {
        console.log(`Creating ${stars.length} stars with increased scale...`);
        
        this.starField.clear();
        this.currentStars = stars;
        
        const scale = 100; // Much larger scale to spread stars out significantly
        const geometry = new THREE.BufferGeometry();
        const positions = [];
        
        stars.forEach(star => {
            positions.push(star.x * scale, star.y * scale, star.z * scale);
        });
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        
        // Use specified PointsMaterial with size 0.2 and white color
        const material = new THREE.PointsMaterial({
            size: 0.2,
            color: 0xffffff,
            sizeAttenuation: true
        });
        
        const points = new THREE.Points(geometry, material);
        
        // Add individual star spheres for raycasting with increased scale
        stars.forEach((star) => {
            const pointGeometry = new THREE.SphereGeometry(this.getStarSize(star), 8, 6);
            const pointMaterial = new THREE.MeshBasicMaterial({ 
                color: this.getStarColor(star),
                transparent: true,
                opacity: 0.5 // Moderate opacity for better visibility while keeping PointsMaterial primary
            });
            const point = new THREE.Mesh(pointGeometry, pointMaterial);
            point.position.set(star.x * scale, star.y * scale, star.z * scale);
            point.userData.starData = star;
            this.starField.add(point);
        });
        
        this.starField.add(points);
        console.log(`✅ Created ${stars.length} stars with ${scale}x scale`);
        console.log(`🌟 STAR SIZES: Sol = 2.0 units, fictional = 1.2-1.6 units, planets = 1.0 units, regular = 0.6 units`);
        console.log(`⚪ POINTSMATERIAL: Base size = 0.2, white color, sizeAttenuation = true`);
    }
    
    async loadStellarRegions() {
        try {
            const response = await fetch('/api/stellar-regions');
            const data = await response.json();
            
            if (data.success && data.data) {
                this.createStellarRegions(data.data);
            }
        } catch (error) {
            console.error('Error loading stellar regions:', error);
        }
    }
    
    createStellarRegions(regions) {
        this.stellarRegionsGroup.clear();
        
        const scale = 100; // Match star scale
        regions.forEach(region => {
            // Calculate LARGE dimensions with increased scaling
            const width = (region.x_range[1] - region.x_range[0]) * scale;
            const height = (region.y_range[1] - region.y_range[0]) * scale;
            const depth = (region.z_range[1] - region.z_range[0]) * scale;
            
            const geometry = new THREE.BoxGeometry(width, height, depth);
            const material = new THREE.MeshBasicMaterial({
                color: 0x00ff00,
                wireframe: false, // Set wireframe to false as requested
                transparent: true,
                opacity: 0.1
            });
            
            const cube = new THREE.Mesh(geometry, material);
            cube.position.set(
                (region.x_range[0] + region.x_range[1]) / 2 * scale,
                (region.y_range[0] + region.y_range[1]) / 2 * scale,
                (region.z_range[0] + region.z_range[1]) / 2 * scale
            );
            
            this.stellarRegionsGroup.add(cube);
        });
        
        console.log(`✅ Created ${regions.length} stellar regions (${scale}x scaled, wireframe: false, hidden by default)`);
    }
    
    async loadNations() {
        const response = await fetch('/api/nations');
        const data = await response.json();
        this.createNationSpheres(data.data || data);
    }
    
    createNationSpheres(data) {
        console.log('🏛️ Creating nation spheres for', data.length, 'nations');
        const scale = 100; // Match star scale
        
        data.forEach(nation => {
            // Assume nation has capital_star_id or center_point
            const center = nation.center_point || this.getStarCenter(nation.capital_star_id); // Fetch coords if needed
            if (!center) return;

            const geometry = new THREE.SphereGeometry((nation.radius || 50) * scale, 32, 32); // Larger radius for visibility, scaled
            const material = new THREE.MeshBasicMaterial({
                color: nation.color || 0x00ff00,
                transparent: true,
                opacity: 0.3,
                wireframe: true
            });
            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.set(center.x * scale, center.y * scale, center.z * scale); // Apply scale to position
            sphere.userData.nationData = nation;
            sphere.name = `NationSphere_${nation.name || nation.id}`;
            this.nationsGroup.add(sphere);
            
            console.log(`🏛️ Created nation sphere: "${nation.name}" at (${(center.x * scale).toFixed(1)}, ${(center.y * scale).toFixed(1)}, ${(center.z * scale).toFixed(1)}) radius: ${((nation.radius || 50) * scale).toFixed(1)}`);
        });
        
        console.log(`✅ Created ${data.length} nation spheres (radius 50 * ${scale}, wireframe, translucent)`);
    }

    getStarCenter(starId) {
        // Fetch star coords from API or currentStars
        const star = this.currentStars.find(s => s.id === starId);
        return star ? { x: star.x, y: star.y, z: star.z } : { x: 0, y: 0, z: 0 }; // Default to origin if not found
    }
    
    createNations(nations) {
        this.nationsGroup.clear();
        
        const scale = 100; // Match star scale
        nations.forEach(nation => {
            nation.territory_boundaries?.forEach(boundary => {
                const scaledBoundary = boundary.map(point => [
                    point[0] * scale, point[1] * scale, point[2] * scale
                ]);
                
                const geometry = new THREE.BufferGeometry();
                const positions = scaledBoundary.flat();
                geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                
                const material = new THREE.LineBasicMaterial({ 
                    color: nation.color || 0xffffff,
                    transparent: true,
                    opacity: 0.6
                });
                
                const line = new THREE.Line(geometry, material);
                this.nationsGroup.add(line);
            });
        });
        
        console.log(`✅ Created ${nations.length} nations (${scale}x scaled)`);
    }
    
    async loadNationalBorders() {
        try {
            const response = await fetch('/api/nations');
            const data = await response.json();
            
            if (data.success && data.data) {
                this.createNationalBorders(data.data);
            }
        } catch (error) {
            console.error('Error loading national borders:', error);
        }
    }
    
    createNationalBorders(nations) {
        this.nationalBordersGroup.clear();
        
        const scale = 100; // Match star scale
        nations.forEach(nation => {
            if (nation.territory_boundaries && nation.territory_boundaries.length > 0) {
                nation.territory_boundaries.forEach(boundary => {
                    // Create a more visible border representation
                    const scaledBoundary = boundary.map(point => [
                        point[0] * scale, point[1] * scale, point[2] * scale
                    ]);
                    
                    // Create border lines
                    const geometry = new THREE.BufferGeometry();
                    const positions = scaledBoundary.flat();
                    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                    
                    const material = new THREE.LineBasicMaterial({ 
                        color: nation.color || 0xff0000, // Default to red if no color
                        transparent: true,
                        opacity: 0.8,
                        linewidth: 3 // Thicker lines for borders
                    });
                    
                    const borderLine = new THREE.Line(geometry, material);
                    borderLine.userData.nationData = nation;
                    borderLine.name = `Border_${nation.name || nation.id}`;
                    
                    this.nationalBordersGroup.add(borderLine);
                    
                    // Add border markers at key points
                    this.createBorderMarkers(scaledBoundary, nation);
                });
            }
        });
        
        console.log(`✅ Created national borders for ${nations.length} nations (${scale}x scaled)`);
    }
    
    createBorderMarkers(boundary, nation) {
        // Create small spheres at border vertices for better visibility
        boundary.forEach((point, index) => {
            if (index % 3 === 0) { // Only every 3rd point to avoid clutter
                const geometry = new THREE.SphereGeometry(0.8, 8, 6);
                const material = new THREE.MeshBasicMaterial({
                    color: nation.color || 0xff0000,
                    transparent: true,
                    opacity: 0.6
                });
                
                const marker = new THREE.Mesh(geometry, material);
                marker.position.set(point[0], point[1], point[2]);
                marker.userData.nationData = nation;
                marker.userData.markerType = 'border';
                marker.name = `BorderMarker_${nation.name || nation.id}_${index}`;
                
                this.nationalBordersGroup.add(marker);
            }
        });
    }
    
    toggleNationalBorders() {
        this.nationalBordersGroup.visible = !this.nationalBordersGroup.visible;
        console.log(`🚩 National borders ${this.nationalBordersGroup.visible ? 'shown' : 'hidden'}`);
        return this.nationalBordersGroup.visible;
    }
    
    async loadTradeRoutes() {
        try {
            const response = await fetch('/api/trade-routes');
            const data = await response.json();
            
            if (data.success && data.data) {
                this.createTradeRoutes(data.data);
            }
        } catch (error) {
            console.error('Error loading trade routes:', error);
        }
    }
    
    createTradeRoutes(routes) {
        this.tradeRoutesGroup.clear();
        
        const scale = 100; // Match star scale
        let createdRoutes = 0;
        
        routes.forEach(route => {
            if (route.endpoints?.from?.star_id && route.endpoints?.to?.star_id) {
                // Find the actual star coordinates by star_id
                const fromStar = this.currentStars.find(star => star.id === route.endpoints.from.star_id);
                const toStar = this.currentStars.find(star => star.id === route.endpoints.to.star_id);
                
                if (fromStar && toStar) {
                    // Scale coordinates by 100x
                    const fromPos = new THREE.Vector3(
                        fromStar.x * scale,
                        fromStar.y * scale,
                        fromStar.z * scale
                    );
                    const toPos = new THREE.Vector3(
                        toStar.x * scale,
                        toStar.y * scale,
                        toStar.z * scale
                    );
                    
                    const geometry = new THREE.BufferGeometry().setFromPoints([fromPos, toPos]);
                    const material = new THREE.LineDashedMaterial({
                        color: 0x00ffff,
                        dashSize: 15, // Increase dash size for larger scale
                        gapSize: 5,
                        transparent: true,
                        opacity: 0.7
                    });
                    
                    const line = new THREE.Line(geometry, material);
                    line.computeLineDistances();
                    line.userData.routeData = route;
                    this.tradeRoutesGroup.add(line);
                    createdRoutes++;
                } else {
                    console.warn(`Trade route ${route.name}: Could not find stars with IDs ${route.endpoints.from.star_id} or ${route.endpoints.to.star_id}`);
                }
            }
        });
        
        console.log(`✅ Created ${createdRoutes} trade routes (${scale}x scaled) from ${routes.length} route definitions`);
    }
    
    async loadExoplanets() {
        try {
            const response = await fetch('/api/exoplanets');
            const data = await response.json();
            
            if (data.success && data.data) {
                this.createExoplanets(data.data);
            }
        } catch (error) {
            console.error('Error loading exoplanets:', error);
        }
    }
    
    createExoplanets(exoplanets) {
        console.log('🪐 Creating enhanced exoplanet system for', exoplanets ? exoplanets.length : 0, 'planets');
        
        // Clear existing exoplanets with proper disposal
        this.clearExoplanets();
        this.exoplanets = exoplanets || [];
        
        const scale = 100; // Match star scale
        
        // Add our solar system planets around Sol at origin
        const solarSystemPlanets = [
            { name: 'Mercury', distance: 0.39, color: 0x8c6239, type: 'terrestrial' },
            { name: 'Venus', distance: 0.72, color: 0xffc649, type: 'terrestrial' },
            { name: 'Earth', distance: 1.0, color: 0x6b93d6, type: 'terrestrial' },
            { name: 'Mars', distance: 1.52, color: 0xcd5c5c, type: 'terrestrial' },
            { name: 'Jupiter', distance: 5.2, color: 0xd8ca9d, size: 0.6, type: 'gas_giant' },
            { name: 'Saturn', distance: 9.5, color: 0xfad5a5, size: 0.5, type: 'gas_giant' },
            { name: 'Uranus', distance: 19.2, color: 0x4fd0e4, size: 0.4, type: 'ice_giant' },
            { name: 'Neptune', distance: 30.1, color: 0x4b70dd, size: 0.4, type: 'ice_giant' }
        ];
        
        solarSystemPlanets.forEach((planet, index) => {
            const angle = (index / solarSystemPlanets.length) * Math.PI * 2;
            const distance = planet.distance * 2; // Scale distance for visibility
            
            const geometry = new THREE.SphereGeometry(planet.size || 0.5, 32, 32); // Increased size and quality for visibility
            const material = new THREE.MeshBasicMaterial({
                color: planet.color,
                transparent: true,
                opacity: 0.9
            });
            
            const planetMesh = new THREE.Mesh(geometry, material);
            planetMesh.position.set(
                Math.cos(angle) * distance,
                0,
                Math.sin(angle) * distance
            );
            planetMesh.userData.planetData = {
                name: planet.name,
                system: 'Sol',
                distance: planet.distance,
                type: planet.type,
                category: 'Solar System Planet'
            };
            planetMesh.name = `SolarPlanet_${planet.name}`;
            
            this.exoplanetGroup.add(planetMesh);
            console.log(`🪐 Created solar system planet: "${planet.name}" at distance ${planet.distance} AU`);
        });
        
        // Add other exoplanets from API data with enhanced colors
        if (exoplanets && exoplanets.length > 0) {
            exoplanets.forEach((exoplanet, i) => {
                const geometry = new THREE.SphereGeometry(0.5, 32, 32); // Increased size for better visibility
                const material = new THREE.MeshBasicMaterial({
                    color: this.getPlanetColor(exoplanet),
                    transparent: true,
                    opacity: 0.8
                });
                
                const planet = new THREE.Mesh(geometry, material);
                planet.position.set(
                    exoplanet.x * scale,
                    exoplanet.y * scale,
                    exoplanet.z * scale
                );
                planet.userData.exoplanetData = exoplanet;
                planet.name = `Exoplanet_${exoplanet.name || i}`;
                
                this.exoplanetGroup.add(planet);
                console.log(`🪐 Created exoplanet: "${exoplanet.name || 'Unknown'}" at position (${exoplanet.x * scale}, ${exoplanet.y * scale}, ${exoplanet.z * scale})`);
            });
        }
        
        console.log(`✅ Enhanced exoplanet system created: ${solarSystemPlanets.length} solar system planets + ${exoplanets ? exoplanets.length : 0} exoplanets`);
        console.log(`🪐 EXOPLANET SIZES: Solar system planets = 0.5 units, API exoplanets = 0.5 units, 32x32 geometry`);
    }
    
    async loadFictionalExoplanets() {
        try {
            const response = await fetch('/api/fictional-exoplanets');
            const data = await response.json();
            
            if (data.success && data.data) {
                this.createFictionalExoplanets(data.data);
            } else if (Array.isArray(data)) {
                this.createFictionalExoplanets(data);
            }
        } catch (error) {
            console.error('Error loading fictional exoplanets:', error);
        }
    }
    
    createFictionalExoplanets(fictionalPlanets) {
        console.log('🔴 Creating fictional exoplanets:', fictionalPlanets ? fictionalPlanets.length : 0);
        
        this.clearFictionalExoplanets();
        const scale = 100; // Match star scale
        
        if (fictionalPlanets && fictionalPlanets.length > 0) {
            fictionalPlanets.forEach((planet, i) => {
                // Create glowing red sphere - DOUBLED radius for visibility
                const geometry = new THREE.SphereGeometry(1.0, 32, 32); // Doubled from 0.5 to 1.0
                const material = new THREE.MeshBasicMaterial({
                    color: 0xff0000, // Glowing red
                    transparent: true,
                    opacity: 0.8
                });
                
                const planetMesh = new THREE.Mesh(geometry, material);
                planetMesh.position.set(
                    planet.x * scale,
                    planet.y * scale,
                    planet.z * scale
                );
                planetMesh.userData.fictionalPlanetData = planet;
                planetMesh.name = `FictionalPlanet_${planet.name || i}`;
                
                this.fictionalExoplanetGroup.add(planetMesh);
                
                // Create orbit ring - DOUBLED radius for visibility
                this.createOrbitRing(planet, scale, 2.0); // Doubled orbit radius
                
                console.log(`🔴 Created fictional exoplanet: "${planet.name || 'Unknown'}" at position (${planet.x * scale}, ${planet.y * scale}, ${planet.z * scale})`);
            });
        }
        
        console.log(`✅ Fictional exoplanet system created: ${fictionalPlanets ? fictionalPlanets.length : 0} glowing red planets with orbits`);
        console.log(`🔴 FICTIONAL PLANET SIZES: 1.0 units (doubled), orbit radius: 2.0 units (doubled), glowing red`);
    }
    
    createOrbitRing(planet, scale, orbitRadius) {
        const geometry = new THREE.RingGeometry(orbitRadius - 0.1, orbitRadius + 0.1, 32);
        const material = new THREE.MeshBasicMaterial({
            color: 0xff4444, // Slightly lighter red for orbit
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });
        
        const orbitRing = new THREE.Mesh(geometry, material);
        orbitRing.position.set(
            planet.x * scale,
            planet.y * scale,
            planet.z * scale
        );
        orbitRing.rotation.x = Math.PI / 2; // Make ring horizontal
        orbitRing.userData.orbitData = planet;
        orbitRing.name = `Orbit_${planet.name || 'Unknown'}`;
        
        this.fictionalExoplanetGroup.add(orbitRing);
    }
    
    clearFictionalExoplanets() {
        while (this.fictionalExoplanetGroup.children.length > 0) {
            const child = this.fictionalExoplanetGroup.children[0];
            this.fictionalExoplanetGroup.remove(child);
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
        }
    }
    
    getPlanetColor(planet) {
        // Enhanced planet coloring based on type
        if (planet.type) {
            switch (planet.type.toLowerCase()) {
                case 'terrestrial':
                case 'rocky':
                    return 0x8B4513; // Brown for terrestrial
                case 'gas_giant':
                case 'gas giant':
                    return 0xDAA520; // Golden for gas giants
                case 'ice_giant':
                case 'ice giant':
                    return 0x4682B4; // Steel blue for ice giants
                case 'water_world':
                case 'ocean':
                    return 0x006994; // Deep blue for water worlds
                default:
                    return 0x4ecdc4; // Cyan for unknown/exoplanets
            }
        }
        return 0x4ecdc4; // Default cyan
    }
    
    clearExoplanets() {
        // Properly dispose of existing exoplanets
        while (this.exoplanetGroup.children.length > 0) {
            const child = this.exoplanetGroup.children[0];
            this.exoplanetGroup.remove(child);
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
        }
    }
    
    createGalacticDirections() {
        // Create coordinate axes for galactic directions - much larger for the new scale
        const axesHelper = new THREE.AxesHelper(2500);
        this.scene.add(axesHelper);
        this.axesHelper = axesHelper; // Store reference for visibility control
        
        // Create text labels for galactic directions
        const labelPositions = [
            { pos: [3000, 0, 0], text: 'Spinward', color: 0xff0000 },
            { pos: [-3000, 0, 0], text: 'Anti-Spinward', color: 0xff0000 },
            { pos: [0, 3000, 0], text: 'Coreward', color: 0x00ff00 },
            { pos: [0, -3000, 0], text: 'Rimward', color: 0x00ff00 },
            { pos: [0, 0, 3000], text: 'Trailing', color: 0x0000ff },
            { pos: [0, 0, -3000], text: 'Driftward', color: 0x0000ff }
        ];
        
        labelPositions.forEach(label => {
            const geometry = new THREE.SphereGeometry(2, 8, 6); // Reasonable size direction labels
            const material = new THREE.MeshBasicMaterial({ color: label.color });
            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.set(...label.pos);
            sphere.userData.labelText = label.text;
            
            this.axisLabels.push(sphere);
            this.scene.add(sphere);
        });
        
        console.log('✅ Created galactic direction axes and labels');
    }
    
    getStarColor(star) {
        if (star.is_fictional) return new THREE.Color(0xff6b6b);
        // Sol always has planets, as do any stars with planets or exoplanet count
        if (star.name === 'Sol' || star.id === 500000 || star.id === 0 || star.has_planets || star.exoplanet_count > 0) {
            return new THREE.Color(0x4ecdc4);
        }
        
        const spectralClass = star.spectral_class || '';
        const spectral = spectralClass.length > 0 ? spectralClass[0].toUpperCase() : 'G';
        const colors = {
            'O': 0x9bb0ff, 'B': 0xaabfff, 'A': 0xcad7ff,
            'F': 0xf8f7ff, 'G': 0xfff4ea, 'K': 0xffd2a1, 'M': 0xffad51
        };
        return new THREE.Color(colors[spectral] || 0xfff4ea);
    }
    
    getStarSize(star) {
        // Double the sizes AGAIN for maximum visibility
        if (star.name === 'Sol' || star.id === 500000 || star.id === 0) return 2.0; // Sol very prominent
        if (star.fictional_name === 'Tiefe-Grenze Tor' || star.id === 999999) return 1.6;
        if (star.is_fictional) return 1.2;
        if (star.has_planets || star.exoplanet_count > 0) return 1.0;
        return 0.6; // Doubled again for maximum visibility
    }
    
    onWindowResize() {
        if (!this.camera || !this.renderer) return;
        
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    setVisible(visible) {
        if (this.container) {
            this.container.style.display = visible ? 'block' : 'none';
        }
    }
    
    // Public methods for UI integration
    toggleStellarRegions() {
        this.stellarRegionsGroup.visible = !this.stellarRegionsGroup.visible;
        console.log(`🌌 Stellar regions ${this.stellarRegionsGroup.visible ? 'shown' : 'hidden'}`);
        return this.stellarRegionsGroup.visible;
    }
    
    toggleNations() {
        this.nationsGroup.visible = !this.nationsGroup.visible;
        console.log(`🏛️ Nations ${this.nationsGroup.visible ? 'shown' : 'hidden'}`);
        return this.nationsGroup.visible;
    }
    
    toggleTradeRoutes() {
        this.tradeRoutesGroup.visible = !this.tradeRoutesGroup.visible;
        console.log(`🚚 Trade routes ${this.tradeRoutesGroup.visible ? 'shown' : 'hidden'}`);
        return this.tradeRoutesGroup.visible;
    }
    
    toggleExoplanets() {
        this.exoplanetGroup.visible = !this.exoplanetGroup.visible;
        console.log(`🪐 Exoplanets ${this.exoplanetGroup.visible ? 'shown' : 'hidden'}`);
        return this.exoplanetGroup.visible;
    }
    
    toggleGalacticDirections() {
        this.axisLabels.forEach(label => {
            label.visible = !label.visible;
        });
        if (this.axesHelper) {
            this.axesHelper.visible = !this.axesHelper.visible;
        }
        const visible = this.axisLabels.length > 0 ? this.axisLabels[0].visible : false;
        console.log(`🧭 Galactic directions ${visible ? 'shown' : 'hidden'}`);
        return visible;
    }
    
    resize() {
        this.onWindowResize();
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        if (this.controls) {
            this.controls.update();
        }
        this.render();
    }
    
    render() {
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }
    
    dispose() {
        console.log('🧹 Disposing Three.js starmap resources...');
        
        // Cancel animation
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        
        // Dispose of all groups and their children
        this.clearExoplanets();
        this.clearFictionalExoplanets();
        this.clearStarField();
        this.clearGroups();
        
        // Dispose of controls
        if (this.controls) {
            this.controls.dispose();
            this.controls = null;
        }
        
        // Dispose of renderer
        if (this.renderer) {
            this.renderer.dispose();
            this.renderer = null;
        }
        
        // Clear references
        this.scene = null;
        this.camera = null;
        this.raycaster = null;
        this.mouse = null;
        
        console.log('✅ Three.js starmap disposed successfully');
    }
    
    clearStarField() {
        if (this.starField) {
            while (this.starField.children.length > 0) {
                const child = this.starField.children[0];
                this.starField.remove(child);
                if (child.geometry) child.geometry.dispose();
                if (child.material) child.material.dispose();
            }
        }
    }
    
    clearGroups() {
        const groups = [
            this.stellarRegionsGroup,
            this.nationsGroup,
            this.nationalBordersGroup,
            this.tradeRoutesGroup
        ];
        
        groups.forEach(group => {
            if (group) {
                while (group.children.length > 0) {
                    const child = group.children[0];
                    group.remove(child);
                    if (child.geometry) child.geometry.dispose();
                    if (child.material) child.material.dispose();
                }
            }
        });
        
        // Clear axis labels
        this.axisLabels.forEach(label => {
            if (label.geometry) label.geometry.dispose();
            if (label.material) label.material.dispose();
            if (label.parent) label.parent.remove(label);
        });
        this.axisLabels = [];
    }
}

// Export for use in main starmap
export { ThreeJSStarmap };

// Make available globally for backwards compatibility
if (typeof window !== 'undefined') {
    window.ThreeJSStarmap = ThreeJSStarmap;
    console.log('✅ ThreeJSStarmap class registered globally');
}