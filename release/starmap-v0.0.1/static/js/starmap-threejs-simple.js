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
            
            // Dynamic scaling system
            this.lastCameraDistance = 0;
            this.scalingThresholds = {
                far: 15000,    // Very zoomed out - maximum planet scaling
                medium: 8000,  // Medium zoom - moderate scaling  
                near: 3000     // Close zoom - realistic scaling
            };
            
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
        
        // EXOPLANETS START VISIBLE - set exoplanetGroup visibility to true
        this.exoplanetGroup.visible = true;
        this.fictionalExoplanetGroup.visible = true;
        
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
        
        // First try to intersect with star field objects only (highest priority)
        const starIntersects = this.raycaster.intersectObjects(this.starField.children, false);
        if (starIntersects.length > 0) {
            const selectedObject = starIntersects[0].object;
            this.handleStarSelection(selectedObject);
            return;
        }
        
        // Then try exoplanets (including Sol system)
        const planetIntersects = this.raycaster.intersectObjects(this.exoplanetGroup.children, false);
        if (planetIntersects.length > 0) {
            const selectedObject = planetIntersects[0].object;
            this.handlePlanetSelection(selectedObject);
            return;
        }
        
        // Then try fictional exoplanets
        const fictionalPlanetIntersects = this.raycaster.intersectObjects(this.fictionalExoplanetGroup.children, false);
        if (fictionalPlanetIntersects.length > 0) {
            const selectedObject = fictionalPlanetIntersects[0].object;
            this.handleFictionalPlanetSelection(selectedObject);
            return;
        }
        
        // If nothing was selected, clear highlights
        this.clearStarHighlights();
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
    
    handlePlanetSelection(selectedObject) {
        if (selectedObject.userData && selectedObject.userData.planetData) {
            const planetData = selectedObject.userData.planetData;
            console.log('🪐 Planet selected:', planetData.name);
            
            this.clearStarHighlights();
            selectedObject.material.color.setHex(0xff0000);
            this.selectedStar = selectedObject;
            
            this.showPlanetInMainWindow(planetData);
            return planetData;
        } else if (selectedObject.userData && selectedObject.userData.exoplanetData) {
            const exoplanetData = selectedObject.userData.exoplanetData;
            console.log('🪐 Exoplanet selected:', exoplanetData.name);
            
            this.clearStarHighlights();
            selectedObject.material.color.setHex(0xff0000);
            this.selectedStar = selectedObject;
            
            this.showExoplanetInMainWindow(exoplanetData);
            return exoplanetData;
        }
        return null;
    }
    
    handleFictionalPlanetSelection(selectedObject) {
        if (selectedObject.userData && selectedObject.userData.fictionalPlanetData) {
            const planetData = selectedObject.userData.fictionalPlanetData;
            console.log('🔴 Fictional planet selected:', planetData.name);
            
            this.clearStarHighlights();
            selectedObject.material.color.setHex(0xffff00);
            this.selectedStar = selectedObject;
            
            this.showFictionalPlanetInMainWindow(planetData);
            return planetData;
        }
        return null;
    }
    
    clearStarHighlights() {
        if (this.selectedStar) {
            // Handle different object types
            if (this.selectedStar.userData.starData) {
                // It's a star
                const starData = this.selectedStar.userData.starData;
                this.selectedStar.material.color = this.getStarColor(starData);
            } else if (this.selectedStar.userData.planetData) {
                // It's a Sol system planet - restore original color
                const planetData = this.selectedStar.userData.planetData;
                const solarPlanets = {
                    'Mercury': 0x8c6239, 'Venus': 0xffc649, 'Earth': 0x6b93d6, 'Mars': 0xcd5c5c,
                    'Jupiter': 0xd8ca9d, 'Saturn': 0xfad5a5, 'Uranus': 0x4fd0e4, 'Neptune': 0x4b70dd
                };
                this.selectedStar.material.color.setHex(solarPlanets[planetData.name] || 0x4ecdc4);
            } else if (this.selectedStar.userData.exoplanetData) {
                // It's an exoplanet - restore original color
                const exoplanetData = this.selectedStar.userData.exoplanetData;
                this.selectedStar.material.color = this.getPlanetColor(exoplanetData);
            } else if (this.selectedStar.userData.fictionalPlanetData) {
                // It's a fictional planet - restore red color
                this.selectedStar.material.color.setHex(0xff0000);
            }
            
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
    
    showPlanetInMainWindow(planetData) {
        const starDetailsPanel = document.getElementById('starDetails');
        if (starDetailsPanel) {
            let html = `<h5>🪐 ${planetData.name}</h5>`;
            html += `<p><strong>System:</strong> ${planetData.system}</p>`;
            html += `<p><strong>Type:</strong> ${planetData.type || 'Unknown'}</p>`;
            html += `<p><strong>Category:</strong> ${planetData.category}</p>`;
            if (planetData.distance) {
                html += `<p><strong>Distance from Star:</strong> ${planetData.distance} AU</p>`;
            }
            
            starDetailsPanel.innerHTML = html;
            starDetailsPanel.style.display = 'block';
        }
    }
    
    showExoplanetInMainWindow(exoplanetData) {
        const starDetailsPanel = document.getElementById('starDetails');
        if (starDetailsPanel) {
            let html = `<h5>🪐 ${exoplanetData.name || 'Unknown Exoplanet'}</h5>`;
            html += `<p><strong>Type:</strong> <span style="color: #4ecdc4;">Exoplanet</span></p>`;
            if (exoplanetData.host_star) {
                html += `<p><strong>Host Star:</strong> ${exoplanetData.host_star}</p>`;
            }
            if (exoplanetData.x !== undefined) {
                html += `<p><strong>Coordinates:</strong> (${exoplanetData.x?.toFixed(2)}, ${exoplanetData.y?.toFixed(2)}, ${exoplanetData.z?.toFixed(2)})</p>`;
            }
            
            starDetailsPanel.innerHTML = html;
            starDetailsPanel.style.display = 'block';
        }
    }
    
    showFictionalPlanetInMainWindow(planetData) {
        const starDetailsPanel = document.getElementById('starDetails');
        if (starDetailsPanel) {
            let html = `<h5>🔴 ${planetData.name || 'Unknown Fictional Planet'}</h5>`;
            html += `<p><strong>Type:</strong> <span style="color: #ff6b6b;">Fictional Exoplanet</span></p>`;
            if (planetData.host_star) {
                html += `<p><strong>Host Star:</strong> ${planetData.host_star}</p>`;
            }
            if (planetData.description) {
                html += `<p><strong>Description:</strong> ${planetData.description}</p>`;
            }
            if (planetData.x !== undefined) {
                html += `<p><strong>Coordinates:</strong> (${planetData.x?.toFixed(2)}, ${planetData.y?.toFixed(2)}, ${planetData.z?.toFixed(2)})</p>`;
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

            const geometry = new THREE.SphereGeometry((nation.radius || 25) * scale / 3, 32, 32); // Reduced radius by 2/3rds for better visibility
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
            
            console.log(`🏛️ Created nation sphere: "${nation.name}" at (${(center.x * scale).toFixed(1)}, ${(center.y * scale).toFixed(1)}, ${(center.z * scale).toFixed(1)}) radius: ${((nation.radius || 25) * scale / 3).toFixed(1)}`);
        });
        
        console.log(`✅ Created ${data.length} nation spheres (radius 25 * ${scale} / 3, wireframe, translucent)`);
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
                // Find the actual star coordinates by star_id, with fallback to system name
                let fromStar = this.currentStars.find(star => star.id === route.endpoints.from.star_id);
                let toStar = this.currentStars.find(star => star.id === route.endpoints.to.star_id);
                
                // Fallback: try to find by system name
                if (!fromStar && route.endpoints.from.system) {
                    fromStar = this.currentStars.find(star => 
                        star.name === route.endpoints.from.system || 
                        star.fictional_name === route.endpoints.from.system
                    );
                }
                if (!toStar && route.endpoints.to.system) {
                    toStar = this.currentStars.find(star => 
                        star.name === route.endpoints.to.system || 
                        star.fictional_name === route.endpoints.to.system
                    );
                }
                
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
                    const fromInfo = `${route.endpoints.from.system} (ID: ${route.endpoints.from.star_id})`;
                    const toInfo = `${route.endpoints.to.system} (ID: ${route.endpoints.to.star_id})`;
                    console.warn(`Trade route ${route.name}: Could not find stars - From: ${fromInfo}, To: ${toInfo}`);
                }
            }
        });
        
        console.log(`✅ Created ${createdRoutes} trade routes (${scale}x scaled) from ${routes.length} route definitions`);
    }
    
    async loadExoplanets() {
        try {
            console.log('📡 Loading real exoplanets...');
            const response = await fetch('/api/exoplanets');
            const data = await response.json();
            
            console.log('📊 Exoplanets response:', data);
            
            if (data.success && data.data) {
                console.log(`✅ Found ${data.data.length} real exoplanets`);
                this.createExoplanets(data.data);
            } else if (Array.isArray(data)) {
                console.log(`✅ Found ${data.length} real exoplanets (direct array)`);
                this.createExoplanets(data);
            } else {
                console.warn('⚠️ No real exoplanets data found');
            }
        } catch (error) {
            console.error('❌ Error loading exoplanets:', error);
        }
    }
    
    createExoplanets(exoplanets) {
        console.log('🪐 Creating enhanced exoplanet system for', exoplanets ? exoplanets.length : 0, 'planets');
        
        // LOG ALL REAL EXOPLANET DATA
        console.log('📊 REAL EXOPLANETS DATA ANALYSIS:');
        console.log('=====================================');
        
        if (exoplanets && exoplanets.length > 0) {
            console.log(`📈 Total real exoplanets received: ${exoplanets.length}`);
            
            // Log first 5 complete entries
            console.log('📋 First 5 real exoplanets (full data):');
            exoplanets.slice(0, 5).forEach((planet, i) => {
                console.log(`${i + 1}. "${planet.name || 'Unknown'}"`, planet);
            });
            
            // Analyze coordinate availability
            const withCoords = exoplanets.filter(p => p.x !== undefined && p.y !== undefined && p.z !== undefined);
            const withoutCoords = exoplanets.filter(p => p.x === undefined || p.y === undefined || p.z === undefined);
            
            console.log(`📍 Coordinate analysis:`);
            console.log(`   - With coordinates: ${withCoords.length}`);
            console.log(`   - Without coordinates: ${withoutCoords.length}`);
            
            if (withCoords.length > 0) {
                console.log('✅ Sample planets WITH coordinates:');
                withCoords.slice(0, 3).forEach(p => {
                    console.log(`   - ${p.name}: (${p.x}, ${p.y}, ${p.z})`);
                });
            }
            
            if (withoutCoords.length > 0) {
                console.log('❌ Sample planets WITHOUT coordinates:');
                withoutCoords.slice(0, 3).forEach(p => {
                    console.log(`   - ${p.name || 'Unknown'}: missing coords, has host_star: ${p.host_star || 'No'}`);
                });
            }
            
            // Analyze host star data
            const withHostStar = exoplanets.filter(p => p.host_star);
            console.log(`🌟 Host star analysis:`);
            console.log(`   - With host_star field: ${withHostStar.length}`);
            console.log(`   - Sample host stars: ${withHostStar.slice(0, 3).map(p => p.host_star).join(', ')}`);
            
        } else {
            console.log('❌ No real exoplanet data received');
        }
        
        console.log('=====================================');
        
        // Clear existing exoplanets with proper disposal
        this.clearExoplanets();
        this.exoplanets = exoplanets || [];
        
        const scale = 100; // Match star scale
        
        // Add our solar system planets around Sol at origin
        const solarSystemPlanets = [
            { name: 'Mercury', distance: 3.0, color: 0x8c6239, size: 0.3, type: 'terrestrial' },
            { name: 'Venus', distance: 4.5, color: 0xffc649, size: 0.4, type: 'terrestrial' },
            { name: 'Earth', distance: 6.0, color: 0x6b93d6, size: 0.4, type: 'terrestrial' },
            { name: 'Mars', distance: 8.0, color: 0xcd5c5c, size: 0.3, type: 'terrestrial' },
            { name: 'Jupiter', distance: 15.0, color: 0xd8ca9d, size: 0.8, type: 'gas_giant' },
            { name: 'Saturn', distance: 22.0, color: 0xfad5a5, size: 0.7, type: 'gas_giant' },
            { name: 'Uranus', distance: 35.0, color: 0x4fd0e4, size: 0.5, type: 'ice_giant' },
            { name: 'Neptune', distance: 45.0, color: 0x4b70dd, size: 0.5, type: 'ice_giant' }
        ];
        
        const createdSolarPlanets = []; // Track created planets for duplicate checking
        
        solarSystemPlanets.forEach((planet, index) => {
            const angle = (index / solarSystemPlanets.length) * Math.PI * 2;
            const distance = planet.distance; // Use defined distance directly
            
            const geometry = new THREE.SphereGeometry(planet.size, 32, 32); // Use specific planet size
            const material = new THREE.MeshBasicMaterial({
                color: planet.color,
                transparent: true,
                opacity: 0.9
            });
            
            const planetMesh = new THREE.Mesh(geometry, material);
            const initialPosition = {
                x: Math.cos(angle) * distance,
                y: 0,
                z: Math.sin(angle) * distance
            };
            
            planetMesh.position.set(initialPosition.x, initialPosition.y, initialPosition.z);
            
            // Store original properties for adaptive scaling
            planetMesh.userData.originalRadius = planet.size;
            planetMesh.userData.originalOpacity = 0.9;
            
            planetMesh.userData.planetData = {
                name: planet.name,
                system: 'Sol',
                distance: planet.distance,
                type: planet.type,
                category: 'Solar System Planet'
            };
            planetMesh.name = `SolarPlanet_${planet.name}`;
            
            // Create enlarged invisible click target for Sol system planets
            const clickTargetGeometry = new THREE.SphereGeometry(Math.max(planet.size * 2.5, 3.0), 8, 8);
            const clickTargetMaterial = new THREE.MeshBasicMaterial({ 
                transparent: true, 
                opacity: 0.0,
                visible: false, // Ensure completely invisible
                side: THREE.DoubleSide
            });
            const clickTarget = new THREE.Mesh(clickTargetGeometry, clickTargetMaterial);
            clickTarget.position.copy(planetMesh.position);
            clickTarget.userData = planetMesh.userData; // Share userData
            clickTarget.name = `ClickTarget_${planet.name}`;
            clickTarget.userData.isPlanetClickTarget = true;
            // Store original radius for click target scaling
            clickTarget.userData.originalRadius = Math.max(planet.size * 2.5, 3.0);
            
            // Check for duplicate positions
            const duplicates = this.checkForDuplicatePositions(
                { position: planetMesh.position, name: planet.name },
                createdSolarPlanets,
                2.0 // Threshold for Sol system planets
            );
            
            if (duplicates.length > 0) {
                const newPosition = this.resolveDuplicatePosition(
                    { position: planetMesh.position, name: planet.name },
                    duplicates,
                    'Sol system planet'
                );
                planetMesh.position.set(newPosition.x, newPosition.y, newPosition.z);
            }
            
            this.exoplanetGroup.add(planetMesh);
            this.exoplanetGroup.add(clickTarget); // Add click target
            createdSolarPlanets.push({ position: planetMesh.position, name: planet.name });
            console.log(`🪐 Created solar system planet: "${planet.name}" at position (${planetMesh.position.x.toFixed(1)}, ${planetMesh.position.y.toFixed(1)}, ${planetMesh.position.z.toFixed(1)})`);
        });
        
        console.log(`✅ Sol system duplicate check complete: ${createdSolarPlanets.length} planets positioned`);
        
        // Add other exoplanets from API data with enhanced colors
        let createdCount = 0;
        let skippedCount = 0;
        
        if (exoplanets && exoplanets.length > 0) {
            exoplanets.forEach((exoplanet, i) => {
                // Skip exoplanets without coordinates
                if (exoplanet.x === undefined || exoplanet.y === undefined || exoplanet.z === undefined) {
                    console.warn(`⚠️ Skipping exoplanet "${exoplanet.name || 'Unknown'}" - missing coordinates`);
                    skippedCount++;
                    return;
                }
                
                const geometry = new THREE.SphereGeometry(1.2, 32, 32); // Increased size for better visibility
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
                
                // Store original properties for adaptive scaling
                planet.userData.originalRadius = 1.2;
                planet.userData.originalOpacity = 0.8;
                
                // Create enlarged invisible click target for better interaction
                const clickTargetRadius = Math.max(1.2 * 2, 3.0);
                const clickTargetGeometry = new THREE.SphereGeometry(clickTargetRadius, 8, 8);
                const clickTargetMaterial = new THREE.MeshBasicMaterial({ 
                    transparent: true, 
                    opacity: 0.0,
                    visible: false, // Ensure completely invisible
                    side: THREE.DoubleSide
                });
                const clickTarget = new THREE.Mesh(clickTargetGeometry, clickTargetMaterial);
                clickTarget.position.copy(planet.position);
                clickTarget.userData = planet.userData; // Share userData
                clickTarget.name = `ClickTarget_${exoplanet.name || i}`;
                clickTarget.userData.isPlanetClickTarget = true;
                // Store original radius for click target scaling
                clickTarget.userData.originalRadius = clickTargetRadius;
                
                this.exoplanetGroup.add(planet);
                this.exoplanetGroup.add(clickTarget); // Add click target
                console.log(`🪐 Created exoplanet: "${exoplanet.name || 'Unknown'}" at position (${exoplanet.x * scale}, ${exoplanet.y * scale}, ${exoplanet.z * scale})`);
                createdCount++;
            });
            
            console.log(`📊 Exoplanet creation summary: ${createdCount} created, ${skippedCount} skipped (missing coordinates)`);
        }
        
        console.log(`✅ Enhanced exoplanet system created: ${solarSystemPlanets.length} solar system planets + ${createdCount || 0} real exoplanets`);
        console.log(`🪐 EXOPLANET SIZES: Solar system planets = variable sizes, API exoplanets = 1.2 units, 32x32 geometry`);
        
        // REAL EXOPLANET CREATION SUMMARY
        console.log('📊 REAL EXOPLANET CREATION SUMMARY:');
        console.log('====================================');
        console.log(`🌞 Sol System: 8 planets created (Mercury to Neptune)`);
        console.log(`🪐 API Exoplanets: ${createdCount || 0} created, ${skippedCount || 0} skipped`);
        console.log(`📍 Real planets with coordinates: ${createdCount || 0}`);
        console.log('====================================');
    }
    
    async loadFictionalExoplanets() {
        try {
            console.log('📡 Loading fictional exoplanets...');
            const response = await fetch('/api/fictional-exoplanets');
            const data = await response.json();
            
            console.log('📊 Fictional exoplanets response:', data);
            
            if (data.success && data.data) {
                console.log(`✅ Found ${data.data.length} fictional exoplanets`);
                this.createFictionalExoplanets(data.data);
            } else if (Array.isArray(data)) {
                console.log(`✅ Found ${data.length} fictional exoplanets (direct array)`);
                this.createFictionalExoplanets(data);
            } else {
                console.warn('⚠️ No fictional exoplanets data found');
            }
        } catch (error) {
            console.error('❌ Error loading fictional exoplanets:', error);
        }
    }
    
    checkForDuplicatePositions(newPlanet, existingPlanets, threshold = 1.0) {
        const duplicates = [];
        
        existingPlanets.forEach((existing, index) => {
            const distance = Math.sqrt(
                Math.pow(newPlanet.position.x - existing.position.x, 2) +
                Math.pow(newPlanet.position.y - existing.position.y, 2) +
                Math.pow(newPlanet.position.z - existing.position.z, 2)
            );
            
            if (distance < threshold) {
                duplicates.push({
                    index: index,
                    planet: existing,
                    distance: distance
                });
            }
        });
        
        return duplicates;
    }
    
    resolveDuplicatePosition(planet, duplicates, planetType = 'planet') {
        if (duplicates.length === 0) return planet.position;
        
        console.warn(`🚨 Found ${duplicates.length} duplicate position(s) for ${planetType} "${planet.name}"`);
        duplicates.forEach((dup, i) => {
            console.warn(`   ${i + 1}. Distance ${dup.distance.toFixed(2)} from "${dup.planet.name}"`);
        });
        
        // Find a new position by offsetting in a spiral pattern
        let attempts = 0;
        let newPosition = { ...planet.position };
        const maxAttempts = 20;
        const offsetStep = 0.5;
        
        while (attempts < maxAttempts) {
            attempts++;
            const angle = (attempts * 137.5) * (Math.PI / 180); // Golden angle for spiral
            const radius = attempts * offsetStep;
            
            newPosition = {
                x: planet.position.x + radius * Math.cos(angle),
                y: planet.position.y + radius * Math.sin(angle) * 0.3, // Flatten slightly
                z: planet.position.z + radius * Math.sin(angle)
            };
            
            // Check if new position is clear
            const newDuplicates = this.checkForDuplicatePositions(
                { position: newPosition, name: planet.name }, 
                duplicates.map(d => d.planet),
                1.0
            );
            
            if (newDuplicates.length === 0) {
                console.log(`✅ Resolved duplicate position for "${planet.name}" after ${attempts} attempts`);
                console.log(`   New position: (${newPosition.x.toFixed(2)}, ${newPosition.y.toFixed(2)}, ${newPosition.z.toFixed(2)})`);
                return newPosition;
            }
        }
        
        console.error(`❌ Could not resolve duplicate position for "${planet.name}" after ${maxAttempts} attempts`);
        return planet.position; // Return original if we can't resolve
    }
    
    convertAUtoPosition(au, angleRad, starPos) {
        // Convert AU to starmap units: Keep planets visible near their stars
        // 1 AU = 5 starmap units (about 0.05 parsecs at 100x scale)
        const distance = Math.min(au * 5, 100); // Cap at 100 units for very distant orbits
        
        const x = starPos.x + distance * Math.cos(angleRad);
        const y = starPos.y + distance * Math.sin(angleRad); 
        const z = starPos.z; // Keep z same as star unless inclined orbit
        
        console.log(`🪐 AU conversion: ${au} AU → ${distance.toFixed(2)} units at ${(angleRad * 180 / Math.PI).toFixed(1)}° → (${x.toFixed(2)}, ${y.toFixed(2)}, ${z.toFixed(2)})`);
        
        return { x, y, z };
    }
    
    calculatePlanetProperties(planet) {
        // Extract planet properties with defaults
        const radius = planet.planet_radius_earth || 1.0;
        const mass = planet.planet_mass_earth || 1.0;
        const temperature = planet.equilibrium_temperature || 288;
        const isHabitable = planet.potentially_habitable || false;
        const name = planet.name || 'Unknown';
        
        // Calculate visual radius (scale for visibility)
        let visualRadius = Math.max(0.8, Math.min(4.0, radius * 1.5));
        
        // Determine planet type and base color based on size and mass
        let planetType, baseColor;
        
        if (radius < 0.5) {
            // Small rocky worlds (Mercury-like)
            planetType = 'small_rocky';
            baseColor = 0x8c7853; // Gray-brown
        } else if (radius < 1.5) {
            // Earth-like worlds
            planetType = 'terrestrial';
            baseColor = isHabitable ? 0x4a90e2 : 0xa0522d; // Blue if habitable, brown if not
        } else if (radius < 4.0) {
            // Super-Earths or small gas planets
            planetType = 'super_earth';
            baseColor = 0x87ceeb; // Sky blue
        } else if (radius < 10.0) {
            // Neptune-like ice giants
            planetType = 'ice_giant';
            baseColor = 0x4169e1; // Royal blue
        } else {
            // Jupiter-like gas giants
            planetType = 'gas_giant';
            baseColor = 0xd2691e; // Orange-brown (Jupiter-like)
        }
        
        // Temperature-based color adjustment
        let finalColor = baseColor;
        if (temperature > 1000) {
            // Very hot - red tint
            finalColor = 0xff4500; // Orange-red
        } else if (temperature > 500) {
            // Hot - orange tint
            finalColor = this.blendColors(baseColor, 0xff8c00, 0.6); // Blend with orange
        } else if (temperature < 150) {
            // Very cold - blue tint
            finalColor = this.blendColors(baseColor, 0x4169e1, 0.4); // Blend with blue
        }
        
        // Special handling for known planets
        if (name === 'Earth') {
            finalColor = 0x6b93d6; // Earth blue
            visualRadius = 1.0;
        } else if (name === 'Mars') {
            finalColor = 0xcd5c5c; // Mars red
            visualRadius = 0.8;
        } else if (name === 'Jupiter') {
            finalColor = 0xd2691e; // Jupiter orange
            visualRadius = 3.5;
        } else if (name === 'Saturn') {
            finalColor = 0xfad5a5; // Saturn yellow
            visualRadius = 3.0;
        } else if (name === 'Neptune') {
            finalColor = 0x4169e1; // Neptune blue
            visualRadius = 2.2;
        } else if (name === 'Uranus') {
            finalColor = 0x4fd0e3; // Uranus cyan
            visualRadius = 2.0;
        } else if (name === 'Venus') {
            finalColor = 0xffc649; // Venus yellow
            visualRadius = 0.95;
        } else if (name === 'Mercury') {
            finalColor = 0x8c7853; // Mercury gray
            visualRadius = 0.6;
        }
        
        // Habitable worlds get a green tint
        if (isHabitable && name !== 'Earth') {
            finalColor = this.blendColors(finalColor, 0x32cd32, 0.3); // Blend with green
        }
        
        // Calculate opacity based on planet type
        let opacity = 0.9;
        if (planetType === 'gas_giant' || planetType === 'ice_giant') {
            opacity = 0.7; // Gas planets more translucent
        }
        
        console.log(`🎨 Planet "${name}": ${planetType}, radius=${radius}R⊕ → visual=${visualRadius}, temp=${temperature}K, color=#${finalColor.toString(16)}`);
        
        return {
            radius: visualRadius,
            color: finalColor,
            opacity: opacity,
            type: planetType,
            temperature: temperature,
            isHabitable: isHabitable
        };
    }
    
    blendColors(color1, color2, ratio) {
        // Extract RGB components
        const r1 = (color1 >> 16) & 0xff;
        const g1 = (color1 >> 8) & 0xff;
        const b1 = color1 & 0xff;
        
        const r2 = (color2 >> 16) & 0xff;
        const g2 = (color2 >> 8) & 0xff;
        const b2 = color2 & 0xff;
        
        // Blend colors
        const r = Math.round(r1 * (1 - ratio) + r2 * ratio);
        const g = Math.round(g1 * (1 - ratio) + g2 * ratio);
        const b = Math.round(b1 * (1 - ratio) + b2 * ratio);
        
        return (r << 16) | (g << 8) | b;
    }
    
    calculateAdaptivePlanetScale(baseRadius, cameraDistance) {
        // Calculate adaptive scaling based on camera distance
        let scaleFactor = 1.0;
        
        if (cameraDistance > this.scalingThresholds.far) {
            // Very far - scale up significantly for visibility
            scaleFactor = 4.0;
        } else if (cameraDistance > this.scalingThresholds.medium) {
            // Medium distance - moderate scaling
            const ratio = (cameraDistance - this.scalingThresholds.medium) / 
                         (this.scalingThresholds.far - this.scalingThresholds.medium);
            scaleFactor = 1.0 + (3.0 * ratio); // Scale from 1x to 4x
        } else if (cameraDistance > this.scalingThresholds.near) {
            // Close to medium - slight scaling
            const ratio = (cameraDistance - this.scalingThresholds.near) / 
                         (this.scalingThresholds.medium - this.scalingThresholds.near);
            scaleFactor = 1.0 + (1.0 * ratio); // Scale from 1x to 2x
        }
        // else: Very close - use base scale (1.0)
        
        return Math.max(0.5, Math.min(5.0, baseRadius * scaleFactor));
    }
    
    updatePlanetVisibility() {
        // Get current camera distance from origin
        const cameraDistance = this.camera.position.distanceTo(this.controls.target);
        
        // Only update if camera moved significantly
        if (Math.abs(cameraDistance - this.lastCameraDistance) < 500) {
            return;
        }
        
        this.lastCameraDistance = cameraDistance;
        
        // Update fictional exoplanets scaling
        this.fictionalExoplanetGroup.children.forEach(child => {
            if (child.userData && child.userData.originalRadius) {
                const newScale = this.calculateAdaptivePlanetScale(
                    child.userData.originalRadius, 
                    cameraDistance
                );
                child.scale.setScalar(newScale / child.userData.originalRadius);
                
                // Update opacity based on distance for better visibility
                if (child.material) {
                    const baseOpacity = child.userData.originalOpacity || 0.9;
                    if (cameraDistance > this.scalingThresholds.medium) {
                        child.material.opacity = Math.min(1.0, baseOpacity + 0.2);
                    } else {
                        child.material.opacity = baseOpacity;
                    }
                }
            } else if (child.userData && child.userData.isOrbitRing) {
                // Handle orbit rings - make them even more subtle when zoomed in
                if (child.material) {
                    const baseOpacity = child.userData.originalOpacity || 0.05;
                    if (cameraDistance < this.scalingThresholds.near) {
                        // Very close - hide orbit rings completely
                        child.material.opacity = 0.0;
                    } else if (cameraDistance < this.scalingThresholds.medium) {
                        // Medium distance - very subtle
                        child.material.opacity = baseOpacity * 0.5;
                    } else {
                        // Far - show at base opacity
                        child.material.opacity = baseOpacity;
                    }
                }
            }
        });
        
        // Update Sol system and real exoplanets scaling
        this.exoplanetGroup.children.forEach(child => {
            if (child.userData && child.userData.originalRadius) {
                const newScale = this.calculateAdaptivePlanetScale(
                    child.userData.originalRadius, 
                    cameraDistance
                );
                child.scale.setScalar(newScale / child.userData.originalRadius);
                
                // Update opacity
                if (child.material) {
                    const baseOpacity = child.userData.originalOpacity || 0.9;
                    if (cameraDistance > this.scalingThresholds.medium) {
                        child.material.opacity = Math.min(1.0, baseOpacity + 0.1);
                    } else {
                        child.material.opacity = baseOpacity;
                    }
                }
            }
        });
        
        // Update zoom indicator UI
        this.updateZoomIndicator(cameraDistance);
        
        console.log(`🔍 Updated planet visibility for camera distance: ${cameraDistance.toFixed(0)} units`);
    }
    
    updateZoomIndicator(cameraDistance) {
        const indicator = document.getElementById('zoom-indicator');
        if (!indicator) return;
        
        // Show indicator when Three.js view is active
        const threejsContainer = document.getElementById('threejs-container');
        const isVisible = threejsContainer && threejsContainer.style.display !== 'none';
        
        if (isVisible) {
            indicator.style.display = 'block';
            
            // Update distance
            document.getElementById('camera-distance').textContent = `${cameraDistance.toFixed(0)} units`;
            
            // Calculate current scale factor
            let scaleFactor = 1.0;
            let viewMode = 'Close';
            
            if (cameraDistance > this.scalingThresholds.far) {
                scaleFactor = 4.0;
                viewMode = 'Very Far';
            } else if (cameraDistance > this.scalingThresholds.medium) {
                const ratio = (cameraDistance - this.scalingThresholds.medium) / 
                             (this.scalingThresholds.far - this.scalingThresholds.medium);
                scaleFactor = 1.0 + (3.0 * ratio);
                viewMode = 'Far';
            } else if (cameraDistance > this.scalingThresholds.near) {
                const ratio = (cameraDistance - this.scalingThresholds.near) / 
                             (this.scalingThresholds.medium - this.scalingThresholds.near);
                scaleFactor = 1.0 + (1.0 * ratio);
                viewMode = 'Medium';
            }
            
            document.getElementById('planet-scale').textContent = `${scaleFactor.toFixed(1)}x`;
            document.getElementById('view-mode').textContent = viewMode;
        } else {
            indicator.style.display = 'none';
        }
    }

    createFictionalExoplanets(fictionalPlanets) {
        console.log('🔴 Creating fictional exoplanets:', fictionalPlanets ? fictionalPlanets.length : 0);
        
        // LOG ALL FICTIONAL EXOPLANET DATA
        console.log('📊 FICTIONAL EXOPLANETS DATA ANALYSIS:');
        console.log('==========================================');
        
        if (fictionalPlanets && fictionalPlanets.length > 0) {
            console.log(`📈 Total fictional exoplanets received: ${fictionalPlanets.length}`);
            
            // Log first 5 complete entries
            console.log('📋 First 5 fictional exoplanets (full data):');
            fictionalPlanets.slice(0, 5).forEach((planet, i) => {
                console.log(`${i + 1}. "${planet.name || 'Unknown'}"`, planet);
            });
            
            // Analyze coordinate availability
            const withDirectCoords = fictionalPlanets.filter(p => p.x !== undefined && p.y !== undefined && p.z !== undefined);
            const withoutDirectCoords = fictionalPlanets.filter(p => p.x === undefined || p.y === undefined || p.z === undefined);
            
            console.log(`📍 Direct coordinate analysis:`);
            console.log(`   - With direct coordinates: ${withDirectCoords.length}`);
            console.log(`   - Without direct coordinates: ${withoutDirectCoords.length}`);
            
            // Analyze star_id availability
            const withStarId = fictionalPlanets.filter(p => p.star_id);
            const withoutStarId = fictionalPlanets.filter(p => !p.star_id);
            
            console.log(`🌟 Star ID analysis:`);
            console.log(`   - With star_id: ${withStarId.length}`);
            console.log(`   - Without star_id: ${withoutStarId.length}`);
            
            if (withStarId.length > 0) {
                console.log('✅ Sample planets WITH star_id:');
                withStarId.slice(0, 5).forEach(p => {
                    console.log(`   - ${p.name}: star_id=${p.star_id}, host_star="${p.host_star || 'N/A'}"`);
                });
            }
            
            // Analyze orbital data
            const withOrbitalData = fictionalPlanets.filter(p => p.semi_major_axis);
            console.log(`🪐 Orbital data analysis:`);
            console.log(`   - With semi_major_axis: ${withOrbitalData.length}`);
            
            if (withOrbitalData.length > 0) {
                console.log('✅ Sample planets WITH orbital data:');
                withOrbitalData.slice(0, 5).forEach(p => {
                    console.log(`   - ${p.name}: ${p.semi_major_axis} AU, period=${p.orbital_period} days`);
                });
            }
            
            // Check for duplicates
            const nameStarPairs = fictionalPlanets.map(p => `${p.name}_${p.star_id}`);
            const uniquePairs = [...new Set(nameStarPairs)];
            const duplicateCount = nameStarPairs.length - uniquePairs.length;
            
            console.log(`🔄 Duplicate analysis:`);
            console.log(`   - Total entries: ${fictionalPlanets.length}`);
            console.log(`   - Unique name+star combinations: ${uniquePairs.length}`);
            console.log(`   - Duplicates to remove: ${duplicateCount}`);
            
            if (duplicateCount > 0) {
                const duplicateNames = [];
                const seen = new Set();
                fictionalPlanets.forEach(p => {
                    const key = `${p.name}_${p.star_id}`;
                    if (seen.has(key)) {
                        duplicateNames.push(p.name);
                    } else {
                        seen.add(key);
                    }
                });
                console.log(`🔄 Duplicate planet names: ${[...new Set(duplicateNames)].join(', ')}`);
            }
            
        } else {
            console.log('❌ No fictional exoplanet data received');
        }
        
        console.log('==========================================');
        
        this.clearFictionalExoplanets();
        const scale = 100; // Match star scale
        
        if (fictionalPlanets && fictionalPlanets.length > 0) {
            // Remove duplicates based on name and star_id, and filter out Sol system planets
            const uniquePlanets = [];
            const seen = new Set();
            const solSystemPlanetNames = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'];
            let solPlanetsRemoved = 0;
            
            fictionalPlanets.forEach(planet => {
                // Skip Sol system planets that are already created as real planets
                if (solSystemPlanetNames.includes(planet.name)) {
                    console.log(`🌞 Removing Sol system planet from fictional data: "${planet.name}"`);
                    solPlanetsRemoved++;
                    return;
                }
                
                const key = `${planet.name}_${planet.star_id}`;
                if (!seen.has(key)) {
                    seen.add(key);
                    uniquePlanets.push(planet);
                } else {
                    console.log(`🔄 Removing duplicate fictional planet: "${planet.name}" at star ${planet.star_id}`);
                }
            });
            
            console.log(`📊 Filtering summary: ${fictionalPlanets.length} original → ${solPlanetsRemoved} Sol planets removed → ${uniquePlanets.length} unique fictional planets`);
            
            let createdCount = 0;
            let skippedCount = 0;
            const createdFictionalPlanets = []; // Track created planets for duplicate checking
            
            uniquePlanets.forEach((planet, i) => {
                // Find host star
                const hostStar = this.currentStars.find(star => star.id === planet.star_id);
                if (!hostStar) {
                    console.warn(`⚠️ Skipping fictional planet "${planet.name || 'Unknown'}" - no host star found (star_id: ${planet.star_id})`);
                    skippedCount++;
                    return;
                }
                
                // Scale star position for starmap
                const starPos = { 
                    x: hostStar.x * scale, 
                    y: hostStar.y * scale, 
                    z: hostStar.z * scale 
                };
                
                console.log(`🔴 Processing fictional planet "${planet.name}"`);
                console.log(`🌟 Host star "${hostStar.name || hostStar.fictional_name}" at: (${starPos.x}, ${starPos.y}, ${starPos.z})`);
                console.log(`🔴 Planet orbital data:`, {
                    semi_major_axis: planet.semi_major_axis,
                    orbital_period: planet.orbital_period,
                    orbital_angle: planet.orbital_angle,
                    planet_radius_earth: planet.planet_radius_earth
                });
                
                // Ensure orbital data for animation (add defaults if missing)
                planet.orbit = planet.semi_major_axis || 1.0; // Orbital radius in AU
                planet.period = planet.orbital_period || 365; // Orbital period in days
                planet.star_id = planet.star_id; // Ensure star_id is available
                
                // Get orbital parameters
                const au = planet.orbit;
                const angleDeg = planet.orbital_angle || (i * (360 / uniquePlanets.length)); // Distribute evenly if no angle
                const angleRad = angleDeg * (Math.PI / 180); // Convert degrees to radians
                
                console.log(`🪐 Orbital setup: ${au} AU, ${planet.period} days period, initial angle ${angleDeg}°`);
                
                // Convert AU to 3D position using proper orbital mechanics (initial position)
                const position = this.convertAUtoPosition(au, angleRad, starPos);
                
                let x = position.x;
                let y = position.y;
                let z = position.z;
                
                // Create sphere with enhanced size and color based on planet properties
                const planetProperties = this.calculatePlanetProperties(planet);
                const geometry = new THREE.SphereGeometry(planetProperties.radius, 32, 32);
                const material = new THREE.MeshBasicMaterial({
                    color: planetProperties.color,
                    transparent: true,
                    opacity: planetProperties.opacity
                });
                
                const planetMesh = new THREE.Mesh(geometry, material);
                planetMesh.position.set(x, y, z); // Initial position already scaled in convertAUtoPosition
                
                // Store original properties for adaptive scaling
                planetMesh.userData.originalRadius = planetProperties.radius;
                planetMesh.userData.originalOpacity = planetProperties.opacity;
                
                // Create enlarged invisible click target for better interaction
                const clickTargetGeometry = new THREE.SphereGeometry(Math.max(planetProperties.radius * 2, 4.0), 8, 8);
                const clickTargetMaterial = new THREE.MeshBasicMaterial({ 
                    transparent: true, 
                    opacity: 0.0,
                    visible: false, // Ensure completely invisible
                    side: THREE.DoubleSide
                });
                const clickTarget = new THREE.Mesh(clickTargetGeometry, clickTargetMaterial);
                clickTarget.position.copy(planetMesh.position);
                clickTarget.userData = planetMesh.userData; // Share userData
                clickTarget.name = `ClickTarget_${planet.name || i}`;
                clickTarget.userData.isPlanetClickTarget = true;
                // Store original radius for click target scaling
                clickTarget.userData.originalRadius = Math.max(planetProperties.radius * 2, 4.0);
                
                // Check for duplicate positions before adding
                const duplicates = this.checkForDuplicatePositions(
                    { position: planetMesh.position, name: planet.name },
                    createdFictionalPlanets,
                    1.5 // Threshold for fictional exoplanets
                );
                
                if (duplicates.length > 0) {
                    const newPosition = this.resolveDuplicatePosition(
                        { position: planetMesh.position, name: planet.name },
                        duplicates,
                        'fictional exoplanet'
                    );
                    planetMesh.position.set(newPosition.x, newPosition.y, newPosition.z);
                    
                    // Update x, y, z for orbit ring creation
                    x = newPosition.x;
                    y = newPosition.y;
                    z = newPosition.z;
                }
                
                // Store orbital data for animation
                planetMesh.userData.fictionalPlanetData = planet;
                planetMesh.userData.planetData = {
                    star_id: planet.star_id,
                    orbit: planet.orbit, // AU
                    period: planet.period, // days
                    initialAngle: angleRad, // Initial orbital angle
                    hostStar: hostStar // Reference to host star
                };
                planetMesh.name = `FictionalPlanet_${planet.name || i}`;
                
                this.fictionalExoplanetGroup.add(planetMesh);
                this.fictionalExoplanetGroup.add(clickTarget); // Add click target
                
                // Create very subtle orbit path (optional - can be disabled)
                if (false && au > 2.0) { // DISABLED: Only show orbit rings for distant planets
                    const orbitRadius = Math.min(au * 5, 100); // Same scale as convertAUtoPosition
                    const orbitGeometry = new THREE.RingGeometry(orbitRadius - 0.01, orbitRadius + 0.01, 32);
                    const orbitMaterial = new THREE.MeshBasicMaterial({ 
                        color: 0x333333, // Darker gray
                        transparent: true, 
                        opacity: 0.05, // Much more subtle
                        side: THREE.DoubleSide
                    });
                    const orbitPath = new THREE.Mesh(orbitGeometry, orbitMaterial);
                    orbitPath.position.set(starPos.x, starPos.y, starPos.z);
                    orbitPath.rotation.x = Math.PI / 2; // Flat orbit plane
                    orbitPath.name = `OrbitPath_${planet.name || i}`;
                    
                    // Store original properties for scaling
                    orbitPath.userData.originalOpacity = 0.05;
                    orbitPath.userData.isOrbitRing = true;
                    
                    this.fictionalExoplanetGroup.add(orbitPath);
                }
                
                // Track created planet for duplicate checking
                createdFictionalPlanets.push({ position: planetMesh.position, name: planet.name });
                
                console.log(`🎨 Created fictional exoplanet: "${planet.name || 'Unknown'}" (${planetProperties.type}) at position (${x.toFixed(1)}, ${y.toFixed(1)}, ${z.toFixed(1)})`);
                createdCount++;
            });
            
            console.log(`📊 Fictional exoplanet creation summary: ${createdCount} created, ${skippedCount} skipped (missing coordinates)`);
            console.log(`✅ Fictional exoplanet duplicate check complete: ${createdFictionalPlanets.length} planets positioned`);
            
            console.log(`✅ Fictional exoplanet system created: ${uniquePlanets.length} unique glowing red planets with orbits`);
            
            // FINAL STATISTICS SUMMARY
            console.log('📊 EXOPLANET SYSTEM SUMMARY:');
            console.log('===============================');
            console.log(`🌞 Sol System Planets: 8 (Mercury to Neptune)`);
            console.log(`🪐 Real Exoplanets: ${this.exoplanets ? this.exoplanets.length : 0} loaded`);
            console.log(`🔴 Fictional Exoplanets: ${uniquePlanets.length} unique created`);
            console.log(`📍 Total Planetary Objects: ${8 + (this.exoplanets ? this.exoplanets.length : 0) + uniquePlanets.length}`);
            console.log('===============================');
            
        } else {
            console.log(`✅ Fictional exoplanet system created: 0 planets (no data available)`);
        }
        console.log(`🎨 FICTIONAL PLANET RENDERING: Size based on radius, colors by type/temperature, habitable worlds have green tint`);
        console.log(`🎨 COLOR CODING: Small rocky (gray-brown) → Terrestrial (blue/brown) → Super-Earth (sky blue) → Ice Giant (royal blue) → Gas Giant (orange)`);
        console.log(`🌡️ TEMPERATURE EFFECTS: Very hot (>1000K) = red, Hot (>500K) = orange tint, Cold (<150K) = blue tint`);
        console.log(`🌍 SPECIAL: Habitable worlds = green tint, Sol system planets = accurate colors`);
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
        // Enhanced planet coloring based on type and properties
        
        // Check for planetary type first
        const planetType = planet.type || planet.physical_properties?.planet_type;
        if (planetType) {
            switch (planetType.toLowerCase()) {
                case 'terrestrial':
                case 'rocky':
                case 'super earth':
                    return new THREE.Color(0x8B4513); // Brown for terrestrial
                case 'gas_giant':
                case 'gas giant':
                case 'jupiter-like':
                    return new THREE.Color(0xDAA520); // Golden for gas giants
                case 'ice_giant':
                case 'ice giant':
                case 'neptune-like':
                case 'neptune like':
                case 'mini-neptune':
                    return new THREE.Color(0x4682B4); // Steel blue for ice giants
                case 'water_world':
                case 'ocean':
                    return new THREE.Color(0x006994); // Deep blue for water worlds
                case 'desert':
                    return new THREE.Color(0xCD853F); // Sandy brown for desert
                case 'frozen':
                case 'ice':
                    return new THREE.Color(0xB0E0E6); // Powder blue for frozen
                case 'volcanic':
                    return new THREE.Color(0xFF4500); // Orange red for volcanic
                default:
                    break; // Fall through to other checks
            }
        }
        
        // Check for habitability
        const isHabitable = planet.potentially_habitable || 
                           planet.habitability?.potentially_habitable === 'True';
        if (isHabitable) {
            return new THREE.Color(0x2196F3); // Blue for habitable
        }
        
        // Check temperature
        const temp = planet.equilibrium_temperature || 
                    planet.physical_properties?.equilibrium_temperature_k;
        if (temp) {
            if (temp > 373) {
                return new THREE.Color(0xFF5722); // Red for hot
            } else if (temp < 273) {
                return new THREE.Color(0x9C27B0); // Purple for cold
            }
        }
        
        // Default colors
        return new THREE.Color(0x4ecdc4); // Cyan for unknown/exoplanets
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
        // Increased star sizes for better visibility
        if (star.name === 'Sol' || star.id === 500000 || star.id === 0) return 3.0; // Sol very prominent
        if (star.fictional_name === 'Tiefe-Grenze Tor' || star.id === 999999) return 2.4;
        if (star.is_fictional) return 1.8;
        if (star.has_planets || star.exoplanet_count > 0) return 1.5;
        return 1.0; // Increased base star size
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
        
        // Update planet visibility based on camera distance
        this.updatePlanetVisibility();
        
        // Animate fictional exoplanets in their orbits
        this.animateFictionalExoplanets();
        
        this.render();
    }
    
    animateFictionalExoplanets() {
        if (!this.fictionalExoplanetGroup) return;
        
        const time = Date.now() * 0.0001; // Slow rotation based on real time
        const scale = 100; // Match starmap scale
        
        this.fictionalExoplanetGroup.children.forEach(child => {
            // Only animate planet meshes, not orbit paths or click targets
            if (child.name && child.name.startsWith('FictionalPlanet_')) {
                const planetData = child.userData.planetData;
                if (planetData && planetData.hostStar) {
                    const hostStar = planetData.hostStar;
                    const orbitRadius = planetData.orbit * 0.5; // Same scale as convertAUtoPosition
                    const period = planetData.period || 365; // Period in days
                    
                    // Calculate current orbital angle
                    const angularVelocity = (2 * Math.PI) / period; // Radians per day
                    const currentAngle = planetData.initialAngle + (time * angularVelocity * 10); // Speed up 10x for visibility
                    
                    // Calculate new position
                    const starPos = {
                        x: hostStar.x * scale,
                        y: hostStar.y * scale,
                        z: hostStar.z * scale
                    };
                    
                    const newPosition = {
                        x: starPos.x + orbitRadius * Math.cos(currentAngle),
                        y: starPos.y, // Keep y same as star (flat orbit)
                        z: starPos.z + orbitRadius * Math.sin(currentAngle)
                    };
                    
                    child.position.set(newPosition.x, newPosition.y, newPosition.z);
                    
                    // Update corresponding click target position
                    const clickTargetName = `ClickTarget_${child.userData.fictionalPlanetData?.name}`;
                    const clickTarget = this.fictionalExoplanetGroup.children.find(c => c.name === clickTargetName);
                    if (clickTarget) {
                        clickTarget.position.copy(child.position);
                    }
                }
            }
        });
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