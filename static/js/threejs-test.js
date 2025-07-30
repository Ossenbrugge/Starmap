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
    
    // Create camera
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.z = 5;
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(container.clientWidth, container.clientHeight);
    
    // Clear container and add canvas
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    
    // Create a simple cube
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);
    
    console.log('Scene created with cube, starting animation');
    
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