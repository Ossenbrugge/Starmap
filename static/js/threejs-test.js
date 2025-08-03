// Simple Three.js test
function testThreeJS() {
    console.log('Testing Three.js...');
    
    if (typeof THREE === 'undefined') {
        console.error('THREE is not defined!');
        return false;
    }
    
    console.log('THREE version:', THREE.REVISION);
    
    const container = document.getElementById('threejs-container');
    if (!container) {
        console.error('Container not found!');
        return false;
    }
    
    console.log('Container:', container);
    console.log('Container size:', container.clientWidth, 'x', container.clientHeight);
    
    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x222222);
    
    // Create Plotly.js-style perspective camera
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 10000);
    camera.position.z = 1000;  // Zoom out for 24k stars as specified
    camera.lookAt(scene.position);
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(container.clientWidth, container.clientHeight);
    
    // Clear container and add canvas
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    
    // Create a cube visible from z=1000 distance
    const geometry = new THREE.BoxGeometry(50, 50, 50); // Larger cube for z=1000 camera distance
    const material = new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: false }); // Your exact specification
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);
    
    // Test with axes to verify distribution as requested
    const axesHelper = new THREE.AxesHelper(1000); // Your exact specification
    scene.add(axesHelper);
    
    console.log('Scene created with cube and axes helper, starting animation');
    console.log('Axes: Red=X, Green=Y, Blue=Z (1000 units each)');
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        cube.rotation.x += 0.01;
        cube.rotation.y += 0.01;
        
        renderer.render(scene, camera);
    }
    
    animate();
    
    console.log('Three.js test complete');
    return true;
}

// Export test function
window.testThreeJS = testThreeJS;