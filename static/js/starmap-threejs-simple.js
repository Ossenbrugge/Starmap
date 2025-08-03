/**
 * Three.js Starmap Implementation - Simplified Version
 * Cinematic 3D starmap with particles, spheres, and VR compatibility
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
        console.log('🚀 Initializing Three.js starmap...');
        
        // Check if Three.js is available
        if (typeof THREE === 'undefined') {
            console.error('❌ Three.js not available');
            return false;
        }
        
        console.log('✅ Three.js version:', THREE.REVISION);
        console.log('🔒 CSP-safe mode: Using PointsMaterial instead of ShaderMaterial to avoid eval()');
        
        this.container = document.getElementById('threejs-container');
        if (!this.container) {
            console.error('❌ Three.js container not found');
            return false;
        }
        
        // Check container dimensions
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        if (width <= 0 || height <= 0) {
            console.warn('⚠️ Container has invalid dimensions:', width, 'x', height);
            // Set minimum dimensions
            this.container.style.width = '800px';
            this.container.style.height = '600px';
        }
        
        console.log('✅ Container found with dimensions:', width, 'x', height);
        
        try {
            // Initialize Three.js components
            this.raycaster = new THREE.Raycaster();
            this.mouse = new THREE.Vector2();
            
            this.setupScene();
            this.setupCamera();
            this.setupRenderer();
            this.setupControls();
            this.setupLighting();
            this.setupEventListeners();
            
            // Skip test objects to avoid clutter - stars will be added when data loads
            // this.addTestStar();
            
            // Start animation loop
            this.animate();
            
            console.log('✅ Three.js starmap initialized successfully');
            return true;
            
        } catch (error) {
            console.error('❌ Error initializing Three.js starmap:', error);
            return false;
        }
    }
    
    addTestCube() {
        // Add a small, colored test cube as specified
        const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5); // Small cube
        const material = new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: false }); // Your exact specification
        const cube = new THREE.Mesh(geometry, material);
        cube.position.set(0, 0, 0);
        this.scene.add(cube);
        console.log('✅ Small colored test cube added at origin');
    }
    
    addTestStar() {
        // Add a test star with basic material to verify rendering
        const geometry = new THREE.SphereGeometry(0.1, 32, 32);
        const material = new THREE.MeshBasicMaterial({ 
            color: 0xffffff, 
            wireframe: false,
            transparent: true,
            opacity: 0.9
        });
        const testStar = new THREE.Mesh(geometry, material);
        testStar.position.set(50, 0, 0);
        testStar.name = 'TestStar_Basic';
        this.starField.add(testStar);
        console.log('✅ Test star added with basic material at (50, 0, 0)');
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
        
        // Test with axes to verify distribution as requested
        this.axesHelper = new THREE.AxesHelper(1000); // Your exact specification
        this.axesHelper.name = 'AxesHelper';
        this.scene.add(this.axesHelper);
        console.log('🎯 Added AxesHelper(1000) to verify star distribution - Red=X, Green=Y, Blue=Z');
        console.log('💡 Axes: Red=X-axis, Green=Y-axis, Blue=Z-axis (1000 units each)');
    }
    
    setupCamera() {
        // Plotly.js-style perspective camera settings
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 10000); // Extended far plane for 24k stars
        
        // Zoom out for 24k stars as specified
        this.camera.position.z = 1000;  // Your exact specification
        this.camera.lookAt(this.scene.position); // Your exact specification using scene.position
        
        console.log('✅ Plotly.js-style camera setup: FOV=75°, near=0.1, far=10000, position.z=1000');
        console.log('📊 Camera aspect ratio:', aspect);
        console.log('📍 Camera position:', this.camera.position);
        console.log('🎯 Camera looking at scene position:', this.scene.position);
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
        try {
            // Use modern ES6 imported OrbitControls with your specified configuration
            this.controls = new OrbitControls(this.camera, this.renderer.domElement);
            
            // Apply your specified configuration
            this.controls.enableDamping = true;  // Smooth movement
            this.controls.dampingFactor = 0.25;
            this.controls.screenSpacePanning = false;
            this.controls.maxPolarAngle = Math.PI / 2;
            
            // Additional starmap-specific settings
            this.controls.minDistance = 50;
            this.controls.maxDistance = 2000;
            this.controls.enablePan = true;
            this.controls.enableZoom = true;
            this.controls.enableRotate = true;
            this.controls.target.set(0, 0, 0);
            
            // Mouse button configuration
            this.controls.mouseButtons = {
                LEFT: THREE.MOUSE.ROTATE,
                MIDDLE: THREE.MOUSE.DOLLY,
                RIGHT: THREE.MOUSE.PAN
            };
            
            console.log('✅ Modern OrbitControls initialized with ES6 imports');
            console.log('🎮 Controls: Left-drag=rotate, Right-drag=pan, Wheel=zoom');
            console.log('⚙️ Settings: damping=true, dampingFactor=0.25, maxPolarAngle=90°');
            
        } catch (error) {
            console.warn('⚠️ Modern OrbitControls failed, falling back to manual controls:', error);
            this.setupEnhancedBasicControls();
        }
    }
    
    setupEnhancedBasicControls() {
        // Enhanced fallback controls with maximum browser compatibility
        this.mouseState = {
            isLeftDown: false,
            isRightDown: false,
            lastX: 0,
            lastY: 0
        };
        
        const canvas = this.renderer.domElement;
        
        // Store event listeners for potential cleanup
        this.controlEventListeners = [];
        
        // Prevent context menu on right click
        const contextMenuHandler = (event) => {
            event.preventDefault();
            return false;
        };
        canvas.addEventListener('contextmenu', contextMenuHandler);
        this.controlEventListeners.push({element: canvas, event: 'contextmenu', handler: contextMenuHandler});
        
        // Mouse down handler
        const mouseDownHandler = (event) => {
            event.preventDefault();
            const button = event.button;
            if (button === 0) { // Left button
                this.mouseState.isLeftDown = true;
                console.log('🖱️ Left mouse down - rotate mode');
            } else if (button === 2) { // Right button
                this.mouseState.isRightDown = true;
                console.log('🖱️ Right mouse down - pan mode');
            }
            this.mouseState.lastX = event.clientX;
            this.mouseState.lastY = event.clientY;
            
            // Capture mouse for better tracking
            if (canvas.setCapture) {
                canvas.setCapture();
            }
        };
        canvas.addEventListener('mousedown', mouseDownHandler);
        this.controlEventListeners.push({element: canvas, event: 'mousedown', handler: mouseDownHandler});
        
        // Mouse move handler
        const mouseMoveHandler = (event) => {
            if (!this.mouseState.isLeftDown && !this.mouseState.isRightDown) return;
            
            const deltaX = event.clientX - this.mouseState.lastX;
            const deltaY = event.clientY - this.mouseState.lastY;
            
            if (this.mouseState.isLeftDown) {
                // Left mouse: Rotate camera around origin
                try {
                    const spherical = new THREE.Spherical();
                    spherical.setFromVector3(this.camera.position);
                    spherical.theta -= deltaX * 0.01;
                    spherical.phi += deltaY * 0.01;
                    spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));
                    
                    this.camera.position.setFromSpherical(spherical);
                    this.camera.lookAt(0, 0, 0);
                } catch (error) {
                    console.warn('Rotation error:', error);
                }
            } else if (this.mouseState.isRightDown) {
                // Right mouse: Pan camera
                try {
                    const distance = this.camera.position.length();
                    const panSpeed = distance * 0.002; // Increased pan sensitivity
                    
                    const panX = -deltaX * panSpeed;
                    const panY = deltaY * panSpeed;
                    
                    // Simplified panning without matrix operations for better compatibility
                    const forward = new THREE.Vector3(0, 0, -1);
                    const right = new THREE.Vector3(1, 0, 0);
                    const up = new THREE.Vector3(0, 1, 0);
                    
                    // Transform by camera rotation
                    forward.applyQuaternion(this.camera.quaternion);
                    right.applyQuaternion(this.camera.quaternion);
                    up.applyQuaternion(this.camera.quaternion);
                    
                    const panVector = new THREE.Vector3();
                    panVector.addScaledVector(right, panX);
                    panVector.addScaledVector(up, panY);
                    
                    this.camera.position.add(panVector);
                } catch (error) {
                    console.warn('Pan error:', error);
                }
            }
            
            this.mouseState.lastX = event.clientX;
            this.mouseState.lastY = event.clientY;
        };
        document.addEventListener('mousemove', mouseMoveHandler); // Use document for better tracking
        this.controlEventListeners.push({element: document, event: 'mousemove', handler: mouseMoveHandler});
        
        // Mouse up handler
        const mouseUpHandler = (event) => {
            const button = event.button;
            if (button === 0) {
                this.mouseState.isLeftDown = false;
                console.log('🖱️ Left mouse up');
            } else if (button === 2) {
                this.mouseState.isRightDown = false;
                console.log('🖱️ Right mouse up');
            }
            
            // Release capture
            if (document.releaseCapture) {
                document.releaseCapture();
            }
        };
        document.addEventListener('mouseup', mouseUpHandler); // Use document for better tracking
        this.controlEventListeners.push({element: document, event: 'mouseup', handler: mouseUpHandler});
        
        // Mouse wheel handler with improved compatibility
        const wheelHandler = (event) => {
            event.preventDefault();
            
            // Normalize wheel delta across browsers
            let delta = 0;
            if (event.wheelDelta) {
                delta = event.wheelDelta / 120;
            } else if (event.detail) {
                delta = -event.detail / 3;
            } else if (event.deltaY) {
                delta = -event.deltaY / 100;
            }
            
            const scale = delta > 0 ? 0.9 : 1.1;
            this.camera.position.multiplyScalar(scale);
            
            // Clamp distance
            const distance = this.camera.position.length();
            if (distance < 50) this.camera.position.normalize().multiplyScalar(50);
            if (distance > 2000) this.camera.position.normalize().multiplyScalar(2000);
            
            console.log(`🎡 Zoom: distance=${distance.toFixed(1)}`);
        };
        
        // Add wheel listeners for different browsers
        canvas.addEventListener('wheel', wheelHandler);
        canvas.addEventListener('mousewheel', wheelHandler); // IE/Webkit
        canvas.addEventListener('DOMMouseScroll', wheelHandler); // Firefox
        this.controlEventListeners.push({element: canvas, event: 'wheel', handler: wheelHandler});
        this.controlEventListeners.push({element: canvas, event: 'mousewheel', handler: wheelHandler});
        this.controlEventListeners.push({element: canvas, event: 'DOMMouseScroll', handler: wheelHandler});
        
        console.log('✅ Enhanced manual controls initialized with maximum browser compatibility');
        console.log('🎮 Controls: Left-drag=rotate, Right-drag=pan, Wheel=zoom');
        console.log('🎮 Try dragging and scrolling on the starmap now!');
    }
    
    disableManualControls() {
        // Remove manual control event listeners when OrbitControls takes over
        if (this.controlEventListeners) {
            this.controlEventListeners.forEach(({element, event, handler}) => {
                element.removeEventListener(event, handler);
            });
            this.controlEventListeners = [];
            console.log('🔧 Manual controls disabled, OrbitControls active');
        }
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
            const intersect = starIntersects[0];
            const starMesh = intersect.object;
            
            // Handle different star types (Individual Mesh, InstancedMesh, ParticleSystem)
            let starData = null;
            let starId = null;
            
            if (starMesh.userData && starMesh.userData.starData) {
                // Individual mesh with full starData
                starData = starMesh.userData.starData;
                starId = starData.id;
            } else if (starMesh.userData && starMesh.userData.id) {
                // Individual mesh with userData directly
                starData = starMesh.userData;
                starId = starData.id;
            } else if (starMesh.isInstancedMesh && intersect.instanceId !== undefined) {
                // InstancedMesh - get star from currentStars array using instanceId
                if (this.currentStars && intersect.instanceId < this.currentStars.length) {
                    starData = this.currentStars[intersect.instanceId];
                    starId = starData.id;
                }
            } else if (starMesh.name === 'ParticleSystem' && intersect.index !== undefined) {
                // ParticleSystem - get star from currentStars array using index
                if (this.currentStars && intersect.index < this.currentStars.length) {
                    starData = this.currentStars[intersect.index];
                    starId = starData.id;
                }
            }
            
            if (starId && starData) {
                console.log('🌟 Star clicked:', starId, starData.name || starData.fictional_name || 'Unnamed');
                console.log("Selected star:", starData); // Ensure userData has star info as specified
                
                // Highlight selected star (change color to red) as specified
                this.highlightSelectedStar(starMesh, intersect);
                
                this.showStarDetails(starId, event);
                
                // Also call legacy app method if available
                if (window.app && window.app.selectStar) {
                    window.app.selectStar(starData);
                }
            } else {
                console.log('🔍 Click detected but no star data found:', starMesh.name || 'Unknown object');
            }
        } else {
            // No star intersection - hide tooltip and clear highlights
            this.hideStarTooltip();
            this.clearStarHighlights();
        }
    }
    
    showStarDetails(starId, event) {
        // Show loading tooltip first
        this.displayLoadingTooltip(event);
        
        fetch(`/api/star/${starId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Star details:", data);
                // Update UI or tooltip with details
                this.displayStarTooltip(data, event);
            })
            .catch(error => {
                console.error('Error fetching star details:', error);
                this.displayErrorTooltip(starId, error, event);
            });
    }
    
    displayLoadingTooltip(event) {
        let tooltip = document.getElementById('star-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'star-tooltip';
            tooltip.style.cssText = `
                position: absolute;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                z-index: 1000;
                max-width: 300px;
                pointer-events: none;
            `;
            document.body.appendChild(tooltip);
        }
        
        tooltip.innerHTML = `
            <h4>Loading Star Details...</h4>
            <p>Fetching data from API...</p>
        `;
        
        tooltip.style.left = event.clientX + 10 + 'px';
        tooltip.style.top = event.clientY - 10 + 'px';
        tooltip.style.display = 'block';
    }
    
    displayErrorTooltip(starId, error, event) {
        let tooltip = document.getElementById('star-tooltip');
        if (tooltip) {
            tooltip.innerHTML = `
                <h4>Error Loading Star</h4>
                <p><strong>Star ID:</strong> ${starId}</p>
                <p><strong>Error:</strong> ${error.message}</p>
                <p>Click elsewhere to dismiss</p>
            `;
            
            tooltip.style.left = event.clientX + 10 + 'px';
            tooltip.style.top = event.clientY - 10 + 'px';
            tooltip.style.display = 'block';
            
            // Hide error after 5 seconds
            setTimeout(() => {
                tooltip.style.display = 'none';
            }, 5000);
        }
    }
    
    displayStarTooltip(starData, event) {
        // Create or update star details tooltip/panel
        let tooltip = document.getElementById('star-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'star-tooltip';
            tooltip.style.cssText = `
                position: absolute;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                z-index: 1000;
                max-width: 300px;
                pointer-events: none;
            `;
            document.body.appendChild(tooltip);
        }
        
        // Update tooltip content based on API response format
        const displayName = starData.names?.primary_name || starData.names?.fictional_name || starData.name || 'Unnamed Star';
        const coordinates = starData.coordinates || starData;
        const properties = starData.physical_properties || starData;
        const classification = starData.classification || starData;
        
        tooltip.innerHTML = `
            <h4>${displayName}</h4>
            <p><strong>ID:</strong> ${starData.id || starData._id}</p>
            <p><strong>Position:</strong> (${coordinates.x?.toFixed(2)}, ${coordinates.y?.toFixed(2)}, ${coordinates.z?.toFixed(2)})</p>
            <p><strong>Magnitude:</strong> ${properties.magnitude || 'N/A'}</p>
            <p><strong>Spectral Class:</strong> ${properties.spectral_class || 'N/A'}</p>
            ${coordinates.dist ? `<p><strong>Distance:</strong> ${coordinates.dist} ly</p>` : ''}
            ${properties.luminosity ? `<p><strong>Luminosity:</strong> ${properties.luminosity}</p>` : ''}
            ${classification.constellation ? `<p><strong>Constellation:</strong> ${classification.constellation}</p>` : ''}
            ${starData.exoplanets?.count > 0 ? `<p><strong>Exoplanets:</strong> ${starData.exoplanets.count}</p>` : ''}
        `;
        
        // Position tooltip near mouse
        tooltip.style.left = event.clientX + 10 + 'px';
        tooltip.style.top = event.clientY - 10 + 'px';
        tooltip.style.display = 'block';
        
        // Hide tooltip after 5 seconds
        setTimeout(() => {
            tooltip.style.display = 'none';
        }, 5000);
        
        console.log('📊 Star tooltip displayed for:', starData.name || starData.fictional_name || 'Unnamed');
    }
    
    hideStarTooltip() {
        const tooltip = document.getElementById('star-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }
    
    highlightSelectedStar(starMesh, intersect) {
        // Clear previous selection highlight
        this.clearStarHighlights();
        
        // Store current selection for future clearing
        this.selectedStar = { mesh: starMesh, intersect: intersect };
        
        if (starMesh.isInstancedMesh && intersect.instanceId !== undefined) {
            // InstancedMesh highlighting - change color of specific instance
            const color = new THREE.Color(0xff0000); // Red as specified
            starMesh.setColorAt(intersect.instanceId, color);
            if (starMesh.instanceColor) {
                starMesh.instanceColor.needsUpdate = true;
            }
            console.log(`🔴 Highlighted InstancedMesh star at index ${intersect.instanceId}`);
        } else if (starMesh.material) {
            // Individual mesh highlighting - change material color
            if (Array.isArray(starMesh.material)) {
                starMesh.material.forEach(mat => {
                    if (mat.color) mat.color.set(0xff0000); // Red as specified
                });
            } else {
                starMesh.material.color.set(0xff0000); // Red as specified
            }
            console.log(`🔴 Highlighted individual star mesh`);
        } else {
            console.log(`⚠️ Cannot highlight star - no material found`);
        }
    }
    
    clearStarHighlights() {
        if (this.selectedStar) {
            const { mesh, intersect } = this.selectedStar;
            
            if (mesh.isInstancedMesh && intersect.instanceId !== undefined) {
                // Restore InstancedMesh color
                const color = new THREE.Color(0xffffff); // White default
                mesh.setColorAt(intersect.instanceId, color);
                if (mesh.instanceColor) {
                    mesh.instanceColor.needsUpdate = true;
                }
            } else if (mesh.material) {
                // Restore individual mesh color
                if (Array.isArray(mesh.material)) {
                    mesh.material.forEach(mat => {
                        if (mat.color) mat.color.set(0xffffff); // White default
                    });
                } else {
                    mesh.material.color.set(0xffffff); // White default
                }
            }
            
            this.selectedStar = null;
            console.log(`⚪ Cleared star highlight`);
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
        
        if (!stars || !Array.isArray(stars) || stars.length === 0) {
            console.error('❌ Invalid or empty stars array provided');
            return;
        }
        
        // DATA VALIDATION: Test with smaller subset for isolation unless full dataset requested
        const originalCount = stars.length;
        const useFullDataset = window.starmapConfig?.useFullDataset || false;
        
        if (!useFullDataset && stars.length > 100) {
            console.log('🔬 DATA TESTING MODE: Limiting to 100 stars for isolation and validation');
            console.log('💡 To test full 24k+ dataset with InstancedMesh, set: window.starmapConfig = {useFullDataset: true}');
            stars = stars.slice(0, 100);  // Test with 100 stars
        } else if (useFullDataset) {
            console.log('🚀 FULL DATASET MODE: Using all', stars.length, 'stars for InstancedMesh testing');
        }
        
        console.log(`📊 Star data validation: ${originalCount} total → ${stars.length} testing subset`);
        console.log('📊 Sample star data:', stars[0]);
        
        // LOG ALL STAR DATA as requested
        console.log('🌟 Complete star data array:', stars);
        
        // Validate star data structure
        if (!this.validateStarData(stars)) {
            console.error('❌ Star data validation failed');
            return;
        }
        
        try {
            // Clear existing stars safely
            if (this.starField) {
                while (this.starField.children.length > 0) {
                    const child = this.starField.children[0];
                    this.starField.remove(child);
                    if (child.geometry) child.geometry.dispose();
                    if (child.material) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach(mat => mat.dispose());
                        } else {
                            child.material.dispose();
                        }
                    }
                }
            }
            
            this.currentStars = stars;
            
            // Filter valid stars with more detailed validation
            const validStars = stars.filter(star => {
                if (!star) return false;
                
                const hasValidCoords = 
                    star.x != null && star.y != null && star.z != null &&
                    !isNaN(star.x) && !isNaN(star.y) && !isNaN(star.z) &&
                    isFinite(star.x) && isFinite(star.y) && isFinite(star.z);
                
                if (!hasValidCoords) {
                    console.warn(`⚠️ Invalid coordinates for star:`, star.name || star.id, star.x, star.y, star.z);
                }
                
                return hasValidCoords;
            });
            
            console.log(`✅ Filtered to ${validStars.length} valid stars for ParticleSystem`);
            
            if (validStars.length === 0) {
                console.error('❌ No valid stars found after filtering!');
                this.createErrorVisualization();
                return;
            }
            
            // Log coordinate ranges for debugging
            const xCoords = validStars.map(s => s.x);
            const yCoords = validStars.map(s => s.y);
            const zCoords = validStars.map(s => s.z);
            
            console.log('📍 Coordinate ranges:');
            console.log(`   X: ${Math.min(...xCoords).toFixed(2)} to ${Math.max(...xCoords).toFixed(2)}`);
            console.log(`   Y: ${Math.min(...yCoords).toFixed(2)} to ${Math.max(...yCoords).toFixed(2)}`);
            console.log(`   Z: ${Math.min(...zCoords).toFixed(2)} to ${Math.max(...zCoords).toFixed(2)}`);
            
            // Choose rendering method based on star count for optimal performance
            if (validStars.length > 1000) {
                console.log('🚀 Using InstancedMesh for large star dataset (>1000 stars)');
                this.createInstancedStars(validStars);
            } else if (validStars.length > 150) {
                console.log('⭐ Using ParticleSystem for medium star dataset (150-1000 stars)');
                this.createParticleSystem(validStars);
            } else {
                console.log('🔵 Using Individual Meshes for small star dataset (≤150 stars)');
                this.createIndividualStarMeshes(validStars);
            }
            
            // GHOST HUNTING: Disable special stars temporarily to isolate the uniform issue
            console.log('👻 GHOST HUNTING: Skipping special stars to isolate uniform issue');
            // this.createSpecialStars(validStars);
            
            console.log(`🚀 Created star visualization with ${validStars.length} stars`);
            console.log('📦 StarField children count:', this.starField.children.length);
            console.log('📦 Scene total children count:', this.scene.children.length);
            
            // Initial material validation after star creation (one-time only)
            console.log('🔍 Running initial material validation after star creation');
            setTimeout(() => {
                this.debugAllMaterials();
                console.log('✅ Initial material validation complete - further checks will run every 60 seconds');
            }, 100);
            
        } catch (error) {
            console.error('❌ Error creating stars:', error);
            this.createErrorVisualization();
        }
    }
    
    validateStarData(stars) {
        console.log('🔍 Validating star data structure...');
        
        if (!stars || stars.length === 0) {
            console.error('❌ No stars to validate');
            return false;
        }
        
        // Check first few stars for required properties
        const testStars = stars.slice(0, Math.min(5, stars.length));
        let validStars = 0;
        let totalIssues = 0;
        
        testStars.forEach((star, index) => {
            const issues = [];
            
            // Check required coordinate properties
            if (typeof star.x !== 'number' || isNaN(star.x) || !isFinite(star.x)) {
                issues.push('invalid x coordinate');
            }
            if (typeof star.y !== 'number' || isNaN(star.y) || !isFinite(star.y)) {
                issues.push('invalid y coordinate');
            }
            if (typeof star.z !== 'number' || isNaN(star.z) || !isFinite(star.z)) {
                issues.push('invalid z coordinate');
            }
            
            // Check optional but common properties
            if (star.id === undefined) {
                issues.push('missing id');
            }
            if (!star.name && !star.fictional_name) {
                issues.push('missing name');
            }
            if (typeof star.magnitude !== 'number') {
                issues.push('invalid magnitude');
            }
            
            if (issues.length === 0) {
                validStars++;
                console.log(`✅ Star ${index + 1} valid: ${star.name || star.fictional_name || 'Unnamed'} at (${star.x.toFixed(1)}, ${star.y.toFixed(1)}, ${star.z.toFixed(1)})`);
            } else {
                totalIssues += issues.length;
                console.warn(`⚠️ Star ${index + 1} issues: ${issues.join(', ')}`, star);
            }
        });
        
        // Calculate data quality
        const validPercentage = (validStars / testStars.length) * 100;
        console.log(`📊 Data Quality Report:`);
        console.log(`   - Valid stars: ${validStars}/${testStars.length} (${validPercentage.toFixed(1)}%)`);
        console.log(`   - Total issues: ${totalIssues}`);
        console.log(`   - Sample coordinates range: x(${Math.min(...stars.map(s => s.x || 0)).toFixed(1)} to ${Math.max(...stars.map(s => s.x || 0)).toFixed(1)})`);
        
        // Return true if at least 80% of test stars are valid
        const isValid = validPercentage >= 80;
        
        if (isValid) {
            console.log('✅ Star data validation passed');
        } else {
            console.error(`❌ Star data validation failed: only ${validPercentage.toFixed(1)}% valid`);
        }
        
        return isValid;
    }
    
    createErrorVisualization() {
        // Create a simple error visualization when star creation fails
        console.log('🔧 Creating error visualization...');
        
        try {
            const geometry = new THREE.BoxGeometry(1.0, 1.0, 1.0); // Small cube as specified
            const material = new THREE.MeshBasicMaterial({ 
                color: 0xff0000, // Red for error indication
                wireframe: false, // Your specification: wireframe: false
                transparent: true,
                opacity: 0.8 
            });
            const errorCube = new THREE.Mesh(geometry, material);
            errorCube.position.set(0, 0, 0);
            errorCube.name = 'ErrorVisualization';
            
            this.starField.add(errorCube);
            
            // Add error text
            console.log('⚠️ Error visualization created - small red cube at origin');
            
        } catch (fallbackError) {
            console.error('❌ Even error visualization failed:', fallbackError);
        }
    }
    
    createParticleSystem(stars) {
        console.log('🎯 Creating ParticleSystem for', stars.length, 'stars');
        
        // Validate we have stars to process
        if (!stars || stars.length === 0) {
            console.error('❌ No stars provided to createParticleSystem');
            return;
        }
        
        console.log('📊 Creating attribute arrays for', stars.length, 'stars...');
        
        // Create arrays for particle attributes
        const positions = new Float32Array(stars.length * 3);
        const colors = new Float32Array(stars.length * 3);
        const sizes = new Float32Array(stars.length);
        
        let validStarsProcessed = 0;
        let invalidStarsSkipped = 0;
        
        // Fill arrays with star data
        stars.forEach((star, i) => {
            // Additional validation during processing
            if (!star || typeof star.x !== 'number' || typeof star.y !== 'number' || typeof star.z !== 'number') {
                console.warn(`⚠️ Skipping invalid star at index ${i}:`, star);
                invalidStarsSkipped++;
                // Set default values for invalid stars
                const i3 = i * 3;
                positions[i3] = 0;
                positions[i3 + 1] = 0;
                positions[i3 + 2] = 0;
                colors[i3] = 1;
                colors[i3 + 1] = 1;
                colors[i3 + 2] = 1;
                sizes[i] = 1;
                return;
            }
            
            const i3 = i * 3;
            
            // Positions with 10x scaling for Plotly.js-style distribution (convert coordinate system)
            positions[i3] = star.x * 10;
            positions[i3 + 1] = star.z * 10;
            positions[i3 + 2] = -star.y * 10;
            
            // Colors based on spectral class (Plotly.js style)
            const colorHex = this.getStarColorHex(star);
            const color = new THREE.Color(colorHex);
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
            
            // Size based on magnitude (Plotly.js style - smaller, more realistic)
            sizes[i] = Math.max(0.05, this.getStarSize(star) * 0.02); // Plotly.js-style smaller sizes
            
            validStarsProcessed++;
            
            // Log first few stars for debugging with 10x scaling
            if (i < 5) {
                console.log(`⭐ Star ${i + 1}: ${star.name || star.fictional_name || 'Unnamed'} at (${star.x.toFixed(1)}, ${star.y.toFixed(1)}, ${star.z.toFixed(1)}) → ParticleSystem(${positions[i3].toFixed(1)}, ${positions[i3 + 1].toFixed(1)}, ${positions[i3 + 2].toFixed(1)}) [10x scaled]`);
            }
        });
        
        console.log(`📊 ParticleSystem processing complete:`);
        console.log(`   - Valid stars processed: ${validStarsProcessed}`);
        console.log(`   - Invalid stars skipped: ${invalidStarsSkipped}`);
        console.log(`   - Positions array length: ${positions.length}`);
        console.log(`   - Colors array length: ${colors.length}`);
        console.log(`   - Sizes array length: ${sizes.length}`);
        
        // Create BufferGeometry
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        // Force use of PointsMaterial to avoid CSP eval() issues with shader materials
        console.log('🎨 Using CSP-safe PointsMaterial for star rendering (no eval() required)');
        const material = this.createFallbackMaterial();
        
        // Create Points object (ParticleSystem)
        const particles = new THREE.Points(geometry, material);
        particles.name = 'StarParticleSystem';
        
        // Debug: Log particle system details
        console.log('📊 ParticleSystem geometry vertices:', geometry.attributes.position.count);
        console.log('📊 ParticleSystem material type:', material.type);
        console.log('📊 ParticleSystem material size:', material.size);
        console.log('📊 ParticleSystem individual sizes range:', Math.min(...sizes), 'to', Math.max(...sizes));
        console.log('📊 ParticleSystem rendered object added to starField:', particles.name);
        
        this.starField.add(particles);
        
        // Skip test spheres to avoid visual clutter - the ParticleSystem should be visible
        console.log('📍 Star positions logged above - no test spheres added to reduce clutter');
        
        console.log('✨ ParticleSystem created with', stars.length, 'star particles');
    }
    
    createIndividualStarMeshes(starData) {
        console.log('🔵 Creating Individual Star Meshes for', starData.length, 'stars');
        
        // LOG ALL STAR DATA as requested
        console.log('🌟 Star data for individual meshes:', starData);
        
        // Validate we have stars to process
        if (!starData || starData.length === 0) {
            console.error('❌ No star data provided to createIndividualStarMeshes');
            return;
        }
        
        console.log('📊 Creating individual mesh geometry and material...');
        
        // Create shared geometry for individual star meshes as specified
        const starGeometry = new THREE.SphereGeometry(0.1, 32, 32); // Your exact specification
        
        console.log('🔄 Starting position loop for individual star meshes...');
        
        // Create material as specified
        const starMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff }); // Your exact specification
        
        // Loop through star data and create individual meshes as requested
        for (let i = 0; i < starData.length; i++) {
            // Create individual mesh for each star as specified
            const star = new THREE.Mesh(starGeometry, starMaterial);
            
            // Set position with 10x scaling for Plotly.js-style distribution as specified
            star.position.set(starData[i].x * 10, starData[i].y * 10, starData[i].z * 10);
            
            // Add userData as specified
            star.userData = { id: starData[i].id, name: starData[i].name };
            
            // Add to scene as specified
            this.scene.add(star);
        }
        
        console.log(`✨ Individual star meshes created: ${starData.length} stars added to scene`);
        console.log('📦 Scene children count:', this.scene.children.length);
    }
    
    createInstancedStars(stars) {
        console.log('🚀 Creating InstancedMesh for', stars.length, 'stars (optimized for 24k+ stars)');
        
        // Validate we have stars to process
        if (!stars || stars.length === 0) {
            console.error('❌ No stars provided to createInstancedStars');
            return;
        }
        
        console.log('📊 Creating instanced star geometry for', stars.length, 'stars...');
        
        // Create shared geometry and material for all star instances as specified
        const starGeometry = new THREE.SphereGeometry(0.1, 32, 32); // Your exact specification
        const starMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff }); // Your exact specification
        
        // Create InstancedMesh with exact star count
        const instancedStars = new THREE.InstancedMesh(starGeometry, starMaterial, stars.length);
        instancedStars.name = 'InstancedStarField';
        
        // Create matrix for each star instance
        const matrix = new THREE.Matrix4();
        const color = new THREE.Color();
        
        let validStarsProcessed = 0;
        let invalidStarsSkipped = 0;
        
        // Set position, rotation, scale, and color for each star instance
        stars.forEach((star, i) => {
            // Additional validation during processing
            if (!star || typeof star.x !== 'number' || typeof star.y !== 'number' || typeof star.z !== 'number') {
                console.warn(`⚠️ Skipping invalid star at index ${i}:`, star);
                invalidStarsSkipped++;
                
                // Set default position for invalid stars (hidden at origin)
                matrix.setPosition(0, 0, 0);
                matrix.scale(new THREE.Vector3(0.001, 0.001, 0.001)); // Make invisible
                instancedStars.setMatrixAt(i, matrix);
                instancedStars.setColorAt(i, new THREE.Color(0x000000)); // Black = invisible
                return;
            }
            
            // Set position with 10x scaling for Plotly.js-style distribution as specified
            instancedStars.setMatrixAt(i, new THREE.Matrix4().makeTranslation(star.x * 10, star.y * 10, star.z * 10));
            instancedStars.setColorAt(i, new THREE.Color(0xffffff));
            
            validStarsProcessed++;
            
            // Log first few stars for debugging with 10x scaling
            if (i < 5) {
                console.log(`⭐ Instance ${i + 1}: ${star.name || star.fictional_name || 'Unnamed'} at (${star.x.toFixed(1)}, ${star.y.toFixed(1)}, ${star.z.toFixed(1)}) → InstancedMesh(${(star.x * 10).toFixed(1)}, ${(star.y * 10).toFixed(1)}, ${(star.z * 10).toFixed(1)}) [10x scaled]`);
            }
        });
        
        // Mark instance matrices as needing update
        instancedStars.instanceMatrix.needsUpdate = true;
        if (instancedStars.instanceColor) {
            instancedStars.instanceColor.needsUpdate = true;
        }
        
        console.log(`📊 InstancedMesh processing complete:`);
        console.log(`   - Valid stars processed: ${validStarsProcessed}`);
        console.log(`   - Invalid stars skipped: ${invalidStarsSkipped}`);
        console.log(`   - Total instances: ${stars.length}`);
        console.log(`   - Geometry: SphereGeometry(0.1, 32, 32) - your exact specification`);
        console.log(`   - Material: MeshBasicMaterial({ color: 0xffffff }) - your exact specification`);
        console.log(`   - Position scaling: 10x for Plotly.js-style distribution`);
        console.log(`   - Rendered object added to starField:`, instancedStars.name);
        
        // Add to scene
        this.starField.add(instancedStars);
        
        // Skip test spheres to avoid visual clutter - the InstancedMesh should be visible
        console.log('📍 Star positions logged above - no test spheres added to reduce clutter');
        
        console.log('✨ InstancedMesh created with', stars.length, 'star instances for optimal 24k+ performance');
    }
    
    createShaderMaterial() {
        try {
            // Create uniforms object manually to ensure compatibility
            const uniforms = {
                time: { 
                    type: 'f', 
                    value: 0.0 
                }
            };
            
            const material = new THREE.ShaderMaterial({
                uniforms: uniforms,
                vertexShader: `
                    attribute float size;
                    attribute vec3 color;
                    varying vec3 vColor;
                    uniform float time;
                    
                    void main() {
                        vColor = color;
                        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                        
                        // Simple size calculation without twinkling to avoid uniform issues
                        float pointSize = size;
                        
                        // Safe distance calculation
                        float distance = max(1.0, -mvPosition.z);
                        gl_PointSize = pointSize * (100.0 / distance);
                        
                        // Clamp point size to reasonable range
                        gl_PointSize = clamp(gl_PointSize, 1.0, 50.0);
                        
                        gl_Position = projectionMatrix * mvPosition;
                    }
                `,
                fragmentShader: `
                    #ifdef GL_ES
                    precision mediump float;
                    #endif
                    
                    varying vec3 vColor;
                    
                    void main() {
                        // Create circular star with soft edges
                        vec2 center = gl_PointCoord - vec2(0.5);
                        float distance = length(center);
                        
                        if (distance > 0.5) discard;
                        
                        // Smooth falloff from center
                        float alpha = 1.0 - smoothstep(0.1, 0.5, distance);
                        alpha = alpha * alpha; // Square for softer falloff
                        
                        gl_FragColor = vec4(vColor, alpha);
                    }
                `,
                transparent: true,
                vertexColors: true,
                blending: THREE.AdditiveBlending,
                depthWrite: false,
                depthTest: true
            });
            
            // Validate uniform creation
            if (material.uniforms && 
                material.uniforms.time && 
                typeof material.uniforms.time.value === 'number') {
                console.log('✅ Shader material with proper uniforms created successfully');
                return material;
            } else {
                console.warn('⚠️ Shader material uniforms validation failed, using fallback');
                throw new Error('Uniform validation failed');
            }
            
        } catch (error) {
            console.error('❌ Error creating shader material:', error);
            throw error; // Re-throw to trigger fallback
        }
    }
    
    createFallbackMaterial() {
        // Plotly.js-style PointsMaterial for beautiful and stable star rendering
        console.log('🔧 Creating Plotly.js-style PointsMaterial for reliable star display');
        return this.createPlotlyStylePointsMaterial();
    }
    
    createPlotlyStylePointsMaterial() {
        // Exact Plotly.js mimicry as requested
        return new THREE.PointsMaterial({
            size: 0.1, // Plotly.js-style base size
            color: 0xffffff, // Base color (will be overridden by vertex colors)
            sizeAttenuation: true, // Makes points appear smaller with distance, like plotly
            vertexColors: true, // Individual star colors based on data
            transparent: true,
            opacity: 0.9,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            alphaTest: 0.1,
            fog: false
        });
    }
    
    switchToFallbackMaterial() {
        try {
            const particleSystem = this.starField.getObjectByName('StarParticleSystem');
            if (particleSystem && particleSystem.material) {
                console.log('🔄 Switching particle system to fallback material');
                
                // Dispose of the problematic shader material
                if (particleSystem.material.dispose) {
                    particleSystem.material.dispose();
                }
                
                // Replace with fallback material
                particleSystem.material = this.createFallbackMaterial();
                console.log('✅ Successfully switched to fallback material');
            }
        } catch (error) {
            console.error('❌ Error switching to fallback material:', error);
        }
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
        const starSize = Math.max(0.1, Math.min(2.0, this.getStarSize(star) * 0.1));
        const geometry = new THREE.SphereGeometry(starSize, 32, 32);
        const color = this.getStarColor(star);
        
        // Use basic material first to eliminate uniform issues - add glow effects later
        const material = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.8,
            wireframe: false
        });
        
        console.log(`✅ Created basic star material for ${star.name || star.fictional_name}: ${material.type}`);
        
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
        // Create larger sphere for glow effect using basic material
        const glowGeometry = new THREE.SphereGeometry(starMesh.geometry.parameters.radius * 2, 8, 6);
        const glowMaterial = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.2,
            wireframe: false,
            blending: THREE.AdditiveBlending,
            depthWrite: false
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
            // Use basic material first to eliminate uniform issues - add glow effects later
            const material = new THREE.MeshBasicMaterial({
                color: color,
                transparent: true,
                opacity: 0.8,
                wireframe: false
            });
            
            console.log(`✅ Created basic planet material: ${material.type}`);
            
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
        
        // Ensure region boxes are properly sized and use solid material as specified
        const geometry = new THREE.BoxGeometry(x_size, z_size, y_size);
        const material = new THREE.MeshBasicMaterial({
            color: region.color,
            wireframe: false, // Your specification: wireframe: false
            transparent: true,
            opacity: 0.1
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
    
    getStarColorHex(star) {
        // Convert color string to hex number for Three.js materials
        const colorString = this.getStarColor(star);
        return parseInt(colorString.replace('#', '0x'));
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
        try {
            // Update OrbitControls - required for damping to work properly
            if (this.controls && typeof this.controls.update === 'function') {
                this.controls.update();  // Call in animate loop as specified
            }
            
            // No uniform updates needed for PointsMaterial - it's self-contained and stable
            // This eliminates the uniform access errors that were causing crashes
            
            // Animate planet orbits with error handling
            try {
                this.exoplanetGroup.children.forEach(systemGroup => {
                    if (systemGroup && systemGroup.children) {
                        systemGroup.children.forEach(planetMesh => {
                            if (planetMesh.userData && 
                                typeof planetMesh.userData.orbitRadius === 'number' && 
                                typeof planetMesh.userData.orbitAngle === 'number') {
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
                    }
                });
            } catch (error) {
                if (this.frameCount % 600 === 0) {
                    console.warn('⚠️ Planet orbit animation error:', error.message);
                }
            }
            
            // Debug: Log all materials and their uniforms before rendering (reduced frequency)
            if (this.frameCount % 3600 === 0) { // Every 60 seconds instead of 2 seconds
                this.debugAllMaterials();
            }
            
            // Check and fix material uniforms before rendering
            this.validateAndFixUniforms();
            
            // Main render call with error handling
            if (this.renderer && this.scene && this.camera) {
                this.renderer.render(this.scene, this.camera);
            } else {
                console.error('❌ Critical Three.js components missing - stopping render loop');
                this.dispose();
                return;
            }
            
            // Debug info and frame counting
            if (this.frameCount === undefined) this.frameCount = 0;
            this.frameCount++;
            
            // Log debug info every 2 minutes to reduce console spam
            if (this.frameCount % 7200 === 0) {
                console.log(`🎬 Frame ${this.frameCount}: Scene children: ${this.scene.children.length}, StarField children: ${this.starField.children.length}`);
                console.log(`📊 Memory: ${performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + 'MB' : 'Unknown'}`);
            }
            
        } catch (error) {
            console.error('❌ Critical render error:', error);
            // Try to recover by reinitializing
            if (this.frameCount % 60 === 0) { // Only try once per second
                console.log('🔄 Attempting to recover from render error...');
                this.dispose();
            }
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
    
    validateAndFixUniforms() {
        // Check and fix material uniforms before rendering to prevent undefined value errors
        this.scene.traverse((object) => {
            if (object.material) {
                const material = object.material;
                
                // Handle shader materials with uniforms
                if (material.type === 'ShaderMaterial' && material.uniforms) {
                    // Check common uniform names that might be undefined
                    const commonUniforms = ['time', 'opacity', 'diffuse', 'emissive', 'emissiveIntensity', 'map', 'normalMap'];
                    
                    commonUniforms.forEach(uniformName => {
                        if (material.uniforms[uniformName] !== undefined) {
                            // Check if the uniform object exists but value is undefined
                            if (material.uniforms[uniformName].value === undefined) {
                                console.error(`❌ Uniform undefined—defaulting to safe value: ${object.name || 'Unnamed'}.${uniformName}`);
                                
                                // Set default values based on uniform type
                                switch (uniformName) {
                                    case 'time':
                                        material.uniforms[uniformName].value = 0.0;
                                        break;
                                    case 'opacity':
                                        material.uniforms[uniformName].value = 1.0;
                                        break;
                                    case 'emissiveIntensity':
                                        material.uniforms[uniformName].value = 1.0;
                                        break;
                                    case 'diffuse':
                                    case 'emissive':
                                        material.uniforms[uniformName].value = new THREE.Color(0xffffff);
                                        break;
                                    case 'map':
                                    case 'normalMap':
                                        material.uniforms[uniformName].value = null;
                                        break;
                                    default:
                                        material.uniforms[uniformName].value = 0.0;
                                }
                            }
                        }
                    });
                    
                    // Specific fix for emissiveIntensity as requested
                    if (material.uniforms && material.uniforms.emissiveIntensity === undefined) {
                        material.uniforms.emissiveIntensity = { value: 1.0 };
                        console.log(`✅ Added missing emissiveIntensity uniform: ${object.name || 'Unnamed'}`);
                    }
                    
                    // Special handling for custom uniforms that might exist
                    Object.keys(material.uniforms).forEach(uniformName => {
                        const uniform = material.uniforms[uniformName];
                        if (!uniform || uniform.value === undefined) {
                            console.error(`❌ Custom uniform undefined—defaulting to 0: ${object.name || 'Unnamed'}.${uniformName}`);
                            
                            // Create the uniform structure if it doesn't exist
                            if (!uniform) {
                                material.uniforms[uniformName] = { value: 0.0 };
                            } else {
                                uniform.value = 0.0;
                            }
                        }
                    });
                }
                
                // Handle materials that might have emissive properties but wrong material type
                if (material.type === 'MeshBasicMaterial') {
                    // MeshBasicMaterial doesn't support emissiveIntensity - fix the material type issue
                    if (material.emissiveIntensity !== undefined) {
                        console.warn(`⚠️ MeshBasicMaterial doesn't support emissiveIntensity, removing property: ${object.name || 'Unnamed'}`);
                        delete material.emissiveIntensity;
                    }
                    
                    // Basic material property validation
                    if (material.opacity === undefined) {
                        material.opacity = 1.0;
                    }
                    if (material.transparent === undefined) {
                        material.transparent = false;
                    }
                }
                
                // Handle materials that properly support emissive properties
                if (material.type === 'MeshPhongMaterial' || material.type === 'MeshStandardMaterial') {
                    // These materials properly support emissive and emissiveIntensity
                    if (material.opacity === undefined) {
                        console.warn(`⚠️ Material opacity undefined, defaulting to 1.0: ${object.name || 'Unnamed'}`);
                        material.opacity = 1.0;
                    }
                    if (material.transparent === undefined) {
                        material.transparent = false;
                    }
                    if (material.emissiveIntensity === undefined && material.emissive) {
                        console.log(`✅ Adding missing emissiveIntensity property: ${object.name || 'Unnamed'}`);
                        material.emissiveIntensity = 1.0;
                    }
                }
            }
        });
    }
    
    debugAllMaterials() {
        console.log('🔍 DEBUG: Scanning all materials for uniform issues...');
        
        const materialCount = { total: 0, shader: 0, points: 0, mesh: 0, problematic: 0 };
        
        this.scene.traverse((object) => {
            if (object.material) {
                materialCount.total++;
                const material = object.material;
                
                console.log(`📋 Object: ${object.name || 'Unnamed'} | Type: ${object.type} | Material: ${material.type}`);
                
                if (material.type === 'ShaderMaterial') {
                    materialCount.shader++;
                    console.log(`🎨 SHADER MATERIAL FOUND: ${object.name}`);
                    
                    if (material.uniforms) {
                        console.log('🔧 Uniforms:', Object.keys(material.uniforms));
                        
                        // Check each uniform for undefined values
                        Object.keys(material.uniforms).forEach(uniformName => {
                            const uniform = material.uniforms[uniformName];
                            if (!uniform || uniform.value === undefined) {
                                console.error(`❌ UNIFORM GHOST FOUND! ${object.name}.${uniformName} = ${uniform}`);
                                materialCount.problematic++;
                            } else {
                                console.log(`✅ ${uniformName}: ${typeof uniform.value} = ${uniform.value}`);
                            }
                        });
                    } else {
                        console.error(`❌ SHADER MATERIAL WITHOUT UNIFORMS: ${object.name}`);
                        materialCount.problematic++;
                    }
                } else if (material.type === 'PointsMaterial') {
                    materialCount.points++;
                    console.log(`⭐ Points material: ${object.name} - OK`);
                } else if (object.type === 'InstancedMesh') {
                    materialCount.instanced = (materialCount.instanced || 0) + 1;
                    console.log(`🚀 InstancedMesh material: ${material.type} - ${object.name} (${object.count} instances)`);
                } else {
                    materialCount.mesh++;
                    console.log(`🔷 Other material: ${material.type} - ${object.name}`);
                    
                    // Check if it's a mesh material that might have shader properties
                    if (material.uniforms) {
                        console.warn(`⚠️ Unexpected uniforms in ${material.type}:`, Object.keys(material.uniforms));
                    }
                }
            }
        });
        
        console.log('📊 Material Summary:', materialCount);
        
        if (materialCount.problematic > 0) {
            console.error(`❌ Found ${materialCount.problematic} problematic materials with undefined uniforms!`);
        } else {
            console.log('✅ All materials look healthy');
        }
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

// Export for use in main starmap (ES6 module style)
export { ThreeJSStarmap };

// Also make available globally for backwards compatibility
window.ThreeJSStarmap = ThreeJSStarmap;