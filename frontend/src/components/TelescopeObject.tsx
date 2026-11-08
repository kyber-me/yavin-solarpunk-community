import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import type { Aim } from './Telescope';
import type { AmbientSource } from '../arrivalEffects';

export function TelescopeObject({ aim, zoom, ambient }: { aim: Aim; zoom: number; ambient: AmbientSource }) {
  const host = useRef<HTMLDivElement>(null);
  const model = useRef<{ update: (aim: Aim, zoom: number) => void } | null>(null);
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    const element = host.current;
    if (!element) return;
    let renderer: THREE.WebGLRenderer;
    try { renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' }); }
    catch { setUnavailable(true); return; }
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(33, 1, .1, 30);
    camera.position.set(-3.3, 2.7, -5.2);
    camera.lookAt(0, 1.22, .1);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.domElement.setAttribute('aria-hidden', 'true');
    element.append(renderer.domElement);

    scene.add(new THREE.HemisphereLight(0xf9e9c0, 0x283e2a, 2.5));
    const sunlight = new THREE.DirectionalLight(0xffe4ad, 3.5);
    sunlight.position.set(-3, 6, 3);
    sunlight.castShadow = true;
    sunlight.shadow.mapSize.set(1024, 1024);
    sunlight.shadow.camera.left = -3;
    sunlight.shadow.camera.right = 3;
    sunlight.shadow.camera.top = 3;
    sunlight.shadow.camera.bottom = -3;
    sunlight.shadow.normalBias = .025;
    sunlight.shadow.radius = 4;
    scene.add(sunlight);
    const fill = new THREE.DirectionalLight(0xb9d9cb, 1.5);
    fill.position.set(3, 2, -4);
    scene.add(fill);

    const noise = new Uint8Array(128 * 128 * 4);
    for (let i = 0; i < 128 * 128; i++) {
      const value = 224 + ((i * 73 + (i >> 5) * 29) % 32);
      noise.set([value, value, value, 255], i * 4);
    }
    const patina = new THREE.DataTexture(noise, 128, 128, THREE.RGBAFormat);
    patina.wrapS = patina.wrapT = THREE.RepeatWrapping;
    patina.repeat.set(3, 2);
    patina.needsUpdate = true;
    const green = new THREE.MeshStandardMaterial({ color: 0x536e55, roughness: .73, metalness: .2, map: patina });
    const brass = new THREE.MeshStandardMaterial({ color: 0xb69c61, roughness: .54, metalness: .58, map: patina });
    const dark = new THREE.MeshStandardMaterial({ color: 0x263e31, roughness: .85, metalness: .16 });
    const wood = new THREE.MeshStandardMaterial({ color: 0x806c45, roughness: .86, map: patina });
    const glass = new THREE.MeshPhysicalMaterial({ color: 0x133d35, metalness: .25, roughness: .12, clearcoat: 1, clearcoatRoughness: .1 });
    const materials: THREE.Material[] = [green, brass, dark, wood, glass];
    const geometries: THREE.BufferGeometry[] = [];
    function mesh(parent: THREE.Object3D, geometry: THREE.BufferGeometry, material: THREE.Material) {
      geometries.push(geometry);
      const object = new THREE.Mesh(geometry, material);
      object.castShadow = true;
      object.receiveShadow = true;
      parent.add(object);
      return object;
    }
    function rod(parent: THREE.Object3D, from: THREE.Vector3, to: THREE.Vector3, radius: number, material: THREE.Material, upperRadius = radius) {
      const direction = to.clone().sub(from);
      const object = mesh(parent, new THREE.CylinderGeometry(upperRadius, radius, direction.length(), 32), material);
      object.position.copy(from).add(to).multiplyScalar(.5);
      object.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize());
      return object;
    }
    function axial(parent: THREE.Object3D, front: number, back: number, length: number, z: number, material: THREE.Material) {
      const object = mesh(parent, new THREE.CylinderGeometry(front, back, length, 64), material);
      object.rotation.x = Math.PI / 2;
      object.position.z = z;
      return object;
    }
    const body = new THREE.Group();
    scene.add(body);
    // Three legs, braces, feet and collars share the same perspective and light.
    for (let i = 0; i < 3; i++) {
      const angle = i * Math.PI * 2 / 3 + .45;
      const foot = new THREE.Vector3(Math.sin(angle) * .82, .075, Math.cos(angle) * .82);
      const top = new THREE.Vector3(Math.sin(angle) * .14, 1.23, Math.cos(angle) * .14);
      rod(body, foot, top, .047, green, .065);
      const collar = foot.clone().lerp(top, .45);
      rod(body, collar.clone().lerp(top, .05), collar.clone().lerp(foot, .05), .061, brass);
      rod(body, new THREE.Vector3(0, .5, 0), foot.clone().lerp(top, .37), .015, brass);
      const shoe = mesh(body, new THREE.SphereGeometry(.08, 24, 12), dark);
      shoe.position.copy(foot);
      shoe.scale.set(1.2, .45, 1.7);
      const grip = rod(body, foot.clone().lerp(top, .1), foot.clone().lerp(top, .4), .054, wood);
      grip.castShadow = true;
    }
    rod(body, new THREE.Vector3(0, .4, 0), new THREE.Vector3(0, 1.44, 0), .055, brass);
    const hub = mesh(body, new THREE.CylinderGeometry(.2, .14, .18, 48), green);
    hub.position.y = 1.23;
    const yaw = new THREE.Group();
    yaw.position.y = 1.42;
    body.add(yaw);
    const yoke = mesh(yaw, new THREE.TorusGeometry(.28, .035, 12, 40, Math.PI), brass);
    yoke.rotation.z = Math.PI;
    yoke.position.y = .14;
    for (const x of [-.27, .27]) {
      rod(yaw, new THREE.Vector3(x, -.03, 0), new THREE.Vector3(x, .25, 0), .035, green);
      const pivot = mesh(yaw, new THREE.CylinderGeometry(.09, .09, .07, 32), brass);
      pivot.position.set(x, .24, 0);
      pivot.rotation.z = Math.PI / 2;
      for (let j = 0; j < 10; j++) {
        const tooth = mesh(yaw, new THREE.SphereGeometry(.014, 8, 6), dark);
        tooth.position.set(x * 1.16, .24 + Math.sin(j * Math.PI / 5) * .073, Math.cos(j * Math.PI / 5) * .073);
      }
    }
    const barrel = new THREE.Group();
    barrel.position.y = .24;
    yaw.add(barrel);
    axial(barrel, .3, .19, 1.35, .15, green);
    axial(barrel, .32, .32, .11, .82, brass);
    axial(barrel, .315, .315, .18, .95, green);
    axial(barrel, .33, .33, .055, 1.06, brass);
    axial(barrel, .295, .295, .012, 1.094, dark);
    axial(barrel, .267, .267, .014, 1.103, glass);
    for (const z of [-.36, .35]) axial(barrel, z > 0 ? .28 : .225, z > 0 ? .28 : .225, .065, z, brass);
    axial(barrel, .21, .21, .08, -.56, brass);
    axial(barrel, .17, .13, .28, -.73, dark);
    axial(barrel, .16, .16, .09, -.9, brass);
    axial(barrel, .175, .175, .045, -.95, dark);
    const ocular = mesh(barrel, new THREE.CircleGeometry(.145, 64), glass);
    ocular.position.z = -.975;
    ocular.rotation.y = Math.PI;
    const focusKnob = mesh(barrel, new THREE.CylinderGeometry(.08, .08, .12, 32), brass);
    focusKnob.rotation.z = Math.PI / 2;
    focusKnob.position.set(-.23, -.05, -.48);
    for (let i = 0; i < 12; i++) {
      const groove = mesh(barrel, new THREE.BoxGeometry(.125, .009, .009), dark);
      groove.position.set(-.23, -.05 + Math.sin(i * Math.PI / 6) * .076, -.48 + Math.cos(i * Math.PI / 6) * .076);
      groove.rotation.x = -i * Math.PI / 6;
    }
    const ground = mesh(scene, new THREE.PlaneGeometry(6, 6), new THREE.ShadowMaterial({ opacity: .3 }));
    materials.push(ground.material as THREE.Material);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = .005;
    ground.castShadow = false;
    let disposed = false;
    let texture: THREE.Texture | undefined;
    const ocularCanvas = document.createElement('canvas');
    ocularCanvas.width = 512;
    ocularCanvas.height = 288;
    const ocularContext = ocularCanvas.getContext('2d');
    const landscape = new Image();
    let landscapeLoaded = false;
    let currentAim = aim;
    let currentZoom = zoom;
    const render = () => { if (!disposed) renderer.render(scene, camera); };
    function update(next: Aim, magnification: number) {
      currentAim = next;
      currentZoom = magnification;
      yaw.rotation.y = -.15 - (next.x - .66) * 1.3;
      barrel.rotation.x = -.13 + (next.y - .47) * .85;
      if (texture) {
        const span = .38 / magnification;
        texture.repeat.set(span, span * 2048 / 1152);
        texture.offset.set(next.x - span / 2, 1 - next.y - span * 2048 / 1152 / 2);
      }
      render();
    }
    function paintOcular() {
      if (disposed || !landscapeLoaded || !ocularContext || !texture) return;
      ocularContext.clearRect(0, 0, ocularCanvas.width, ocularCanvas.height);
      ocularContext.drawImage(landscape, 0, 0, ocularCanvas.width, ocularCanvas.height);
      if (ambient.canvas.current) ocularContext.drawImage(ambient.canvas.current, 0, 0, ocularCanvas.width, ocularCanvas.height);
      texture.needsUpdate = true;
      render();
    }
    ambient.listeners.add(paintOcular);
    landscape.onload = () => {
      if (disposed) return;
      landscapeLoaded = true;
      texture = new THREE.CanvasTexture(ocularCanvas);
      texture.colorSpace = THREE.SRGBColorSpace;
      const ocularMaterial = new THREE.MeshBasicMaterial({ map: texture, color: 0xc9dbc9 });
      materials.push(ocularMaterial);
      ocular.material = ocularMaterial;
      update(currentAim, currentZoom);
      paintOcular();
    };
    landscape.src = '/images/yavin-chegada-v1.png';
    function resize() {
      const { width, height } = element!.getBoundingClientRect();
      if (!width || !height) return;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
      render();
    }
    const observer = new ResizeObserver(resize);
    observer.observe(element);
    model.current = { update };
    update(aim, zoom);
    resize();
    return () => {
      disposed = true;
      ambient.listeners.delete(paintOcular);
      landscape.onload = null;
      observer.disconnect();
      model.current = null;
      geometries.forEach(geometry => geometry.dispose());
      materials.forEach(material => material.dispose());
      patina.dispose();
      texture?.dispose();
      sunlight.shadow.map?.dispose();
      renderer.dispose();
      renderer.forceContextLoss();
      renderer.domElement.remove();
    };
  }, [ambient]);
  useEffect(() => { model.current?.update(aim, zoom); }, [aim, zoom]);
  return <div ref={host} className="telescope-object">{unavailable && <span className="telescope-unavailable">A visualização da luneta não está disponível neste navegador.</span>}</div>;
}
