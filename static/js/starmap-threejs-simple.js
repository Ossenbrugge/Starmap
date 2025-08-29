// Three.js Starmap Implementation - Minimal Working Version
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

    init() {
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
            this.setupControls();
            this.setupLighting();

            // Load stars
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
        console.log('✅ Scene setup complete');
    }

    setupCamera() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 10000);
        this.camera.position.z = 10000;
        console.log('✅ Camera setup complete');
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
        console.log('✅ Renderer setup complete');
    }

    setupControls() {
        this.controls = {
            update: () => {},
            target: new THREE.Vector3(0, 0, 0)
        };
        console.log('✅ Controls setup complete');
    }

    setupLighting() {
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        console.log('✅ Lighting setup complete');
    }

    async loadStars() {
        try {
            console.log('🌟 Loading stars...');
            const response = await fetch('/api/stars');
            const data = await response.json();

            if (data.success && data.data) {
                console.log(`✅ Loaded ${data.data.length} stars`);
                this.createStars(data.data);
            }
        } catch (error) {
            console.error('❌ Error loading stars:', error);
        }
    }

    createStars(stars) {
        console.log(`Creating ${stars.length} stars...`);

        // Simple star creation - just points
        const geometry = new THREE.BufferGeometry();
        const positions = [];
        const colors = [];

        stars.forEach(star => {
            if (star.x !== undefined && star.y !== undefined && star.z !== undefined) {
                positions.push(star.x, star.y, star.z);
                colors.push(1, 1, 1); // White stars
            }
        });

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 2,
            vertexColors: true
        });

        const points = new THREE.Points(geometry, material);
        this.starField.add(points);

        console.log(`✅ Created ${stars.length} stars`);
    }

    // Add missing methods that main app calls
    async loadStellarRegions() {
        console.log('🌌 loadStellarRegions called - implementing basic version');
        try {
            const response = await fetch('/api/stellar-regions');
            const data = await response.json();
            console.log(`🎯 Stellar regions response: ${data.data ? data.data.length : 0} regions`);
            return true;
        } catch (error) {
            console.warn('🌌 loadStellarRegions failed, but continuing:', error);
            return false;
        }
    }

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
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
}

// Make available globally
if (typeof window !== 'undefined') {
    window.ThreeJSStarmap = ThreeJSStarmap;
    console.log('✅ ThreeJSStarmap class registered globally');
}

export { ThreeJSStarmap };
