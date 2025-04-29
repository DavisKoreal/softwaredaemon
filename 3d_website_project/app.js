// Initialize Three.js scene
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('viewer').appendChild(renderer.domElement);

// Add lights
const light = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(light);
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight.position.set(0, 1, 1);
scene.add(directionalLight);

// Handle file upload
document.getElementById('file-input').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const messageEl = document.getElementById('message');
    
    // Check file extension
    const allowedExtensions = ['.gltf', '.glb', '.obj', '.fbx', '.stl'];
    const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!allowedExtensions.includes(fileExt)) {
        messageEl.textContent = 'Error: Only 3D file formats (.gltf, .glb, .obj, .fbx, .stl) are allowed';
        return;
    }
    
    messageEl.textContent = 'Loading 3D model...';
    
    // Here you would normally load the 3D model
    // For demo purposes, we'll just add a cube
    const geometry = new THREE.BoxGeometry();
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);
    
    camera.position.z = 5;
    messageEl.textContent = '3D model loaded successfully!';
});

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();

// Handle window resize
window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});