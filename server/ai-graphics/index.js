// @ts-check
import * as T from "./libs/CS559-Three/build/three.module.js";
import { OrbitControls } from "./libs/CS559-Three/examples/jsm/controls/OrbitControls.js";
// import landmarks from './models/j-hip-thrust.json' assert { type: 'json' };

let landmarks = [];

let w = 1200;
let h = 720;
let scene = new T.Scene();
scene.background = new T.Color( 0x555555 );

let renderer = new T.WebGLRenderer();

renderer.setSize(w, h);
// console.log(renderer.domElement.clientWidth);
// renderer.setSize(renderer.domElement.width*2, renderer.domElement.width*2);
renderer.shadowMap.enabled = true;

// @ts-ignore
document.getElementById("canvas").appendChild(renderer.domElement);

let ground = new T.Mesh(
	new T.BoxGeometry(200, 0.1, 200),
	new T.MeshStandardMaterial({
		color: "#222222",
		metalness: 0.5,
		roughness: 0.25
	})
);
ground.position.set(0, -1, 0);
ground.castShadow = true;
ground.receiveShadow = true;
scene.add(ground);

/** create a "main camera" */
/** @type{T.PerspectiveCamera} */
let main_camera = new T.PerspectiveCamera(60, w / h, 1, 1000);
main_camera.position.set(40, 20, 10);
main_camera.rotation.set(0, 0, 0);

let joints = [];
let materials = [];

for (let i = 0; i < 33; i++) {
    let color = "#333333";
    let geo = new T.SphereGeometry(1.2);

    if (i == 0) {
        color = "#ff0000";
    }

    if (i == 12 || i == 11 || i == 24 || i == 23) {
        color = "#333333";
    }

	if (i >= 15 && i <= 22) {
		color = "#ffffff";
		geo = new T.SphereGeometry(0.5);
	}

	if (i >= 27 && i <= 32) {
		color = "#ffffff";
		geo = new T.SphereGeometry(0.8);
	}

	// let material = new T.MeshStandardMaterial({
	// 	color: color,
	// 	metalness: 0.8,
	// 	roughness: 0.6
	// });
	let material = new T.MeshStandardMaterial({
		color: color,
		// emissive: 0x111111,
		metalness: 1,
		roughness: 0.55,
	});
	let joint = new T.Mesh(
		geo, material
	);
    joint.castShadow = true;
    joint.receiveShadow = true;


	materials.push(material);
	ground.add(joint);
	joints.push(joint);
}



let active_camera = main_camera;
let controls = new OrbitControls(main_camera, renderer.domElement);

let ambient = new T.AmbientLight(0xffffff, 1.5);
let point = new T.PointLight(0xffffff, 1, 1000);
let dir = new T.DirectionalLight(0xffffff, 2);
point.position.set( 0, 10, 0 );
scene.add(point);
scene.add(ambient);
scene.add(dir);




let uniformScaleSlider = document.getElementById("uniform-scale-slider");
let uniformScale = uniformScaleSlider.value;
uniformScaleSlider.addEventListener("input", () => {
	uniformScale = uniformScaleSlider.value;
});

let jointScaleSlider =  document.getElementById("joint-scale-slider");
let jointScale = jointScaleSlider.value;
jointScaleSlider.addEventListener("input", () => {
	jointScale = jointScaleSlider.value;
});

let xSlider = document.getElementById("x-move-slider");
let x = parseFloat(xSlider.value);
xSlider.addEventListener("input", () => {
	x = parseFloat(xSlider.value);
});

let ySlider = document.getElementById("y-move-slider");
let y = parseFloat(ySlider.value);
ySlider.addEventListener("input", () => {
	y = parseFloat(ySlider.value);
});

let zSlider = document.getElementById("z-move-slider");
let z = parseFloat(zSlider.value);
zSlider.addEventListener("input", () => {
	z = parseFloat(zSlider.value);
});

let xStretchSlider = document.getElementById("x-stretch-slider");
let xStretch = xStretchSlider.value;
xStretchSlider.addEventListener("input", () => {
	xStretch = xStretchSlider.value;
});

let yStretchSlider = document.getElementById("y-stretch-slider");
let yStretch = yStretchSlider.value;
yStretchSlider.addEventListener("input", () => {
	yStretch = yStretchSlider.value;
});

let zStretchSlider = document.getElementById("z-stretch-slider");
let zStretch = zStretchSlider.value;
zStretchSlider.addEventListener("input", () => {
	zStretch = zStretchSlider.value;
});

let ambientIntensitySlider = document.getElementById("ambient-slider");
ambient.intensity = ambientIntensitySlider.value;
ambientIntensitySlider.addEventListener("input", () => {
	ambient.intensity = ambientIntensitySlider.value;
});

let slowdownSlider = document.getElementById("slowdown-slider");
let slowdown = parseInt(slowdownSlider.value);
slowdownSlider.addEventListener("input", () => {
	slowdown = parseInt(slowdownSlider.value);
});

let jointMetallicitySlider = document.getElementById("joint-metallicity-slider");
materials.forEach(material => material.metalness = jointMetallicitySlider.value);
jointMetallicitySlider.addEventListener("input", () => {
	materials.forEach(material => material.metalness = jointMetallicitySlider.value);
});

let modelSelection = document.getElementById("model-selection");
modelSelection.addEventListener("change", () => {
    let newModel = modelSelection.value;
    switchModel(newModel);
});


let usernames = new Set();

function addModelOption(username, model) {
    let optgroup;
    if (!usernames.has(username)) {
        optgroup = document.createElement("optgroup");
        optgroup.label = username;
        optgroup.setAttribute('id', "optgroup-" + username);
        modelSelection.appendChild(optgroup);
    }
    else {
        optgroup = document.getElementById("optgroup-" + username);
    }

    let option = document.createElement("option")
    option.value = model;
    option.innerHTML = model;
    optgroup.appendChild(option);

    usernames.add(username);

}

let frameIndex = 0;

async function switchModel(modelName) {
    const response = await fetch("https://greatamericanyouth.com/ai-graphics/models/" + modelName + ".json");
    const lms = await response.json();
    landmarks = lms;
    frameIndex = 0;
}

async function retrieveModelData() {
    const response = await fetch("https://greatamericanyouth.com/api/model");
    const models = Object.entries(await response.json());

    for (let model of models) {
        addModelOption(model[1]["username"], model[1]["model"]);
    }
    switchModel(modelSelection.value);
}

retrieveModelData();

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

let lastTimestamp;
async function animate(timestamp) {
	let dt = 0.001 * (lastTimestamp ? timestamp - lastTimestamp : 0);

	if (frameIndex++ > landmarks.length) {
		frameIndex = 0;
	}


    for (let i = 0; i < 33; i++) {

        let lms = landmarks[frameIndex];

        if (lms) {
            let lm = lms[i];
            let groundLevel = ground.position.y;
            joints[i].scale.set(jointScale, jointScale, jointScale);
            joints[i].position.x = lm ? (lm["x"] * uniformScale * xStretch) + x: joints[i].position.x;
            joints[i].position.y = lm ? (-(lm["y"]+groundLevel) * uniformScale * yStretch) + y: joints[i].position.y;
            joints[i].position.z = lm ? (-lm["z"] * uniformScale * zStretch) + z: joints[i].position.z;
        }
    }

    await sleep(slowdown);

	lastTimestamp = timestamp;
	renderer.render(scene, active_camera);
	window.requestAnimationFrame(animate);
}


window.requestAnimationFrame(animate);
